"""Deterministic material-balance and campaign economics for AURUM.

The model intentionally describes recovery of pre-existing gold. It has no
variable representing creation or nuclear transmutation of gold.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any

ZERO = Decimal("0")
ONE = Decimal("1")
THOUSAND = Decimal("1000")
BALANCE_TOLERANCE_MG = Decimal("1e-18")


class ScenarioError(ValueError):
    """Raised when a scenario is incomplete, invalid, or nonphysical."""


def _decimal(value: object, field: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ScenarioError(f"{field} must be a finite decimal-compatible number")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ScenarioError(f"{field} must be a finite decimal-compatible number") from exc
    if not result.is_finite():
        raise ScenarioError(f"{field} must be finite")
    return result


def _positive(value: object, field: str) -> Decimal:
    result = _decimal(value, field)
    if result <= ZERO:
        raise ScenarioError(f"{field} must be greater than zero")
    return result


def _nonnegative(value: object, field: str) -> Decimal:
    result = _decimal(value, field)
    if result < ZERO:
        raise ScenarioError(f"{field} must be zero or greater")
    return result


def _fraction(value: object, field: str, *, allow_zero: bool = True) -> Decimal:
    result = _decimal(value, field)
    lower_ok = result >= ZERO if allow_zero else result > ZERO
    if not lower_ok or result > ONE:
        bracket = "[0, 1]" if allow_zero else "(0, 1]"
        raise ScenarioError(f"{field} must be in {bracket}")
    return result


def _integer(value: object, field: str, *, minimum: int = 1) -> int:
    if isinstance(value, bool):
        raise ScenarioError(f"{field} must be an integer")
    try:
        result = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ScenarioError(f"{field} must be an integer") from exc
    if str(result) != str(value).strip() and not isinstance(value, int):
        raise ScenarioError(f"{field} must be an integer")
    if result < minimum:
        raise ScenarioError(f"{field} must be at least {minimum}")
    return result


def _mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ScenarioError(f"{field} must be an object")
    return value


def _strict_fields(
    value: Mapping[str, Any],
    field: str,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    keys = set(value)
    missing = sorted(required - keys)
    unknown = sorted(keys - required - optional)
    if missing:
        raise ScenarioError(f"{field} is missing required fields: {', '.join(missing)}")
    if unknown:
        raise ScenarioError(f"{field} contains unknown fields: {', '.join(unknown)}")


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScenarioError(f"{field} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class FeedSpec:
    """Gold-bearing process feed supplied independently of the urine-derived cells."""

    batch_volume_l: Decimal
    gold_concentration_mg_l: Decimal
    accessible_gold_fraction: Decimal

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> FeedSpec:
        _strict_fields(
            raw,
            "feed",
            {"batch_volume_l", "gold_concentration_mg_l", "accessible_gold_fraction"},
        )
        return cls(
            batch_volume_l=_positive(raw["batch_volume_l"], "feed.batch_volume_l"),
            gold_concentration_mg_l=_nonnegative(
                raw["gold_concentration_mg_l"], "feed.gold_concentration_mg_l"
            ),
            accessible_gold_fraction=_fraction(
                raw["accessible_gold_fraction"], "feed.accessible_gold_fraction"
            ),
        )


@dataclass(frozen=True, slots=True)
class SecretomeSpec:
    """Cell-free capture material derived from a physically separated cell culture."""

    capture_phase_volume_l: Decimal
    binding_capacity_mg_l: Decimal
    active_fraction: Decimal
    reuse_cycles: int
    per_reuse_capacity_retention: Decimal

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> SecretomeSpec:
        _strict_fields(
            raw,
            "secretome",
            {
                "capture_phase_volume_l",
                "binding_capacity_mg_l",
                "active_fraction",
                "reuse_cycles",
                "per_reuse_capacity_retention",
            },
        )
        return cls(
            capture_phase_volume_l=_positive(
                raw["capture_phase_volume_l"], "secretome.capture_phase_volume_l"
            ),
            binding_capacity_mg_l=_nonnegative(
                raw["binding_capacity_mg_l"], "secretome.binding_capacity_mg_l"
            ),
            active_fraction=_fraction(raw["active_fraction"], "secretome.active_fraction"),
            reuse_cycles=_integer(raw["reuse_cycles"], "secretome.reuse_cycles"),
            per_reuse_capacity_retention=_fraction(
                raw["per_reuse_capacity_retention"],
                "secretome.per_reuse_capacity_retention",
            ),
        )

    def effective_capacity_mg(self, reuse_index: int) -> Decimal:
        if reuse_index < 0 or reuse_index >= self.reuse_cycles:
            raise ScenarioError(
                f"reuse_index must be between 0 and {self.reuse_cycles - 1}, inclusive"
            )
        retention = self.per_reuse_capacity_retention**reuse_index
        return (
            self.capture_phase_volume_l
            * self.binding_capacity_mg_l
            * self.active_fraction
            * retention
        )


@dataclass(frozen=True, slots=True)
class ProcessSpec:
    """Stage yields and annual operating schedule."""

    affinity_capture_fraction: Decimal
    reduction_yield_fraction: Decimal
    harvest_yield_fraction: Decimal
    refining_yield_fraction: Decimal
    product_purity_fraction: Decimal
    batches_per_day: Decimal
    operating_days_per_year: int
    energy_kwh_per_batch: Decimal

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> ProcessSpec:
        _strict_fields(
            raw,
            "process",
            {
                "affinity_capture_fraction",
                "reduction_yield_fraction",
                "harvest_yield_fraction",
                "refining_yield_fraction",
                "product_purity_fraction",
                "batches_per_day",
                "operating_days_per_year",
                "energy_kwh_per_batch",
            },
        )
        return cls(
            affinity_capture_fraction=_fraction(
                raw["affinity_capture_fraction"], "process.affinity_capture_fraction"
            ),
            reduction_yield_fraction=_fraction(
                raw["reduction_yield_fraction"], "process.reduction_yield_fraction"
            ),
            harvest_yield_fraction=_fraction(
                raw["harvest_yield_fraction"], "process.harvest_yield_fraction"
            ),
            refining_yield_fraction=_fraction(
                raw["refining_yield_fraction"], "process.refining_yield_fraction"
            ),
            product_purity_fraction=_fraction(
                raw["product_purity_fraction"],
                "process.product_purity_fraction",
                allow_zero=False,
            ),
            batches_per_day=_positive(raw["batches_per_day"], "process.batches_per_day"),
            operating_days_per_year=_integer(
                raw["operating_days_per_year"], "process.operating_days_per_year"
            ),
            energy_kwh_per_batch=_nonnegative(
                raw["energy_kwh_per_batch"], "process.energy_kwh_per_batch"
            ),
        )


@dataclass(frozen=True, slots=True)
class EconomicsSpec:
    """Screening-level economics; inputs are hypotheses rather than market forecasts."""

    gold_price_usd_g: Decimal
    electricity_price_usd_kwh: Decimal
    consumables_usd_per_batch: Decimal
    annual_fixed_cost_usd: Decimal

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> EconomicsSpec:
        _strict_fields(
            raw,
            "economics",
            {
                "gold_price_usd_g",
                "electricity_price_usd_kwh",
                "consumables_usd_per_batch",
                "annual_fixed_cost_usd",
            },
        )
        return cls(
            gold_price_usd_g=_nonnegative(
                raw["gold_price_usd_g"], "economics.gold_price_usd_g"
            ),
            electricity_price_usd_kwh=_nonnegative(
                raw["electricity_price_usd_kwh"], "economics.electricity_price_usd_kwh"
            ),
            consumables_usd_per_batch=_nonnegative(
                raw["consumables_usd_per_batch"], "economics.consumables_usd_per_batch"
            ),
            annual_fixed_cost_usd=_nonnegative(
                raw["annual_fixed_cost_usd"], "economics.annual_fixed_cost_usd"
            ),
        )


@dataclass(frozen=True, slots=True)
class Scenario:
    """Complete, explicitly bounded AURUM screening scenario."""

    name: str
    evidence_status: str
    feed: FeedSpec
    secretome: SecretomeSpec
    process: ProcessSpec
    economics: EconomicsSpec

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> Scenario:
        _strict_fields(
            raw,
            "scenario",
            {"name", "evidence_status", "feed", "secretome", "process", "economics"},
        )
        status = _text(raw["evidence_status"], "evidence_status")
        allowed_statuses = {"hypothesis", "bench-validated", "pilot-validated"}
        if status not in allowed_statuses:
            raise ScenarioError(
                f"evidence_status must be one of: {', '.join(sorted(allowed_statuses))}"
            )
        return cls(
            name=_text(raw["name"], "name"),
            evidence_status=status,
            feed=FeedSpec.from_mapping(_mapping(raw["feed"], "feed")),
            secretome=SecretomeSpec.from_mapping(_mapping(raw["secretome"], "secretome")),
            process=ProcessSpec.from_mapping(_mapping(raw["process"], "process")),
            economics=EconomicsSpec.from_mapping(_mapping(raw["economics"], "economics")),
        )


@dataclass(frozen=True, slots=True)
class StageMassBalance:
    gold_in_feed_mg: Decimal
    accessible_gold_mg: Decimal
    inaccessible_gold_mg: Decimal
    captured_gold_mg: Decimal
    uncaptured_accessible_gold_mg: Decimal
    reduced_gold_mg: Decimal
    unreduced_gold_mg: Decimal
    harvested_gold_mg: Decimal
    harvest_loss_gold_mg: Decimal
    refined_gold_mg: Decimal
    refining_loss_gold_mg: Decimal
    secretome_capacity_mg: Decimal
    unused_secretome_capacity_mg: Decimal
    capacity_limited: bool

    @property
    def total_recovery_fraction(self) -> Decimal:
        if self.gold_in_feed_mg == ZERO:
            return ZERO
        return self.refined_gold_mg / self.gold_in_feed_mg

    @property
    def accounted_gold_mg(self) -> Decimal:
        return (
            self.inaccessible_gold_mg
            + self.uncaptured_accessible_gold_mg
            + self.unreduced_gold_mg
            + self.harvest_loss_gold_mg
            + self.refining_loss_gold_mg
            + self.refined_gold_mg
        )

    def assert_conservation(self) -> None:
        error = abs(self.gold_in_feed_mg - self.accounted_gold_mg)
        if error > BALANCE_TOLERANCE_MG:
            raise ArithmeticError(f"gold material balance failed by {error} mg")


@dataclass(frozen=True, slots=True)
class CampaignResult:
    scenario_name: str
    evidence_status: str
    first_use_balance: StageMassBalance
    mean_refined_gold_mg_per_batch: Decimal
    annual_batches: Decimal
    annual_refined_gold_g: Decimal
    annual_product_mass_g: Decimal
    annual_revenue_usd: Decimal
    annual_energy_cost_usd: Decimal
    annual_consumables_cost_usd: Decimal
    annual_fixed_cost_usd: Decimal
    annual_screening_margin_usd: Decimal
    energy_intensity_kwh_per_g_gold: Decimal | None
    model_warning: str


def _balance_for_reuse(scenario: Scenario, reuse_index: int) -> StageMassBalance:
    feed_gold = scenario.feed.batch_volume_l * scenario.feed.gold_concentration_mg_l
    accessible = feed_gold * scenario.feed.accessible_gold_fraction
    inaccessible = feed_gold - accessible
    capacity = scenario.secretome.effective_capacity_mg(reuse_index)
    affinity_limited = accessible * scenario.process.affinity_capture_fraction
    captured = min(affinity_limited, capacity)
    uncaptured = accessible - captured
    reduced = captured * scenario.process.reduction_yield_fraction
    unreduced = captured - reduced
    harvested = reduced * scenario.process.harvest_yield_fraction
    harvest_loss = reduced - harvested
    refined = harvested * scenario.process.refining_yield_fraction
    refining_loss = harvested - refined
    balance = StageMassBalance(
        gold_in_feed_mg=feed_gold,
        accessible_gold_mg=accessible,
        inaccessible_gold_mg=inaccessible,
        captured_gold_mg=captured,
        uncaptured_accessible_gold_mg=uncaptured,
        reduced_gold_mg=reduced,
        unreduced_gold_mg=unreduced,
        harvested_gold_mg=harvested,
        harvest_loss_gold_mg=harvest_loss,
        refined_gold_mg=refined,
        refining_loss_gold_mg=refining_loss,
        secretome_capacity_mg=capacity,
        unused_secretome_capacity_mg=capacity - captured,
        capacity_limited=capacity < affinity_limited,
    )
    balance.assert_conservation()
    return balance


def evaluate(scenario: Scenario) -> CampaignResult:
    """Evaluate one scenario with exact decimal arithmetic and mass conservation."""

    with localcontext() as context:
        context.prec = 34
        reuse_balances = [
            _balance_for_reuse(scenario, reuse_index)
            for reuse_index in range(scenario.secretome.reuse_cycles)
        ]
        mean_refined = sum((item.refined_gold_mg for item in reuse_balances), ZERO) / Decimal(
            len(reuse_balances)
        )
        annual_batches = (
            scenario.process.batches_per_day * scenario.process.operating_days_per_year
        )
        annual_gold_g = mean_refined * annual_batches / THOUSAND
        annual_product_mass_g = annual_gold_g / scenario.process.product_purity_fraction
        revenue = annual_gold_g * scenario.economics.gold_price_usd_g
        energy_cost = (
            annual_batches
            * scenario.process.energy_kwh_per_batch
            * scenario.economics.electricity_price_usd_kwh
        )
        consumables_cost = annual_batches * scenario.economics.consumables_usd_per_batch
        margin = (
            revenue
            - energy_cost
            - consumables_cost
            - scenario.economics.annual_fixed_cost_usd
        )
        energy_intensity = (
            None
            if annual_gold_g == ZERO
            else annual_batches * scenario.process.energy_kwh_per_batch / annual_gold_g
        )
        return CampaignResult(
            scenario_name=scenario.name,
            evidence_status=scenario.evidence_status,
            first_use_balance=reuse_balances[0],
            mean_refined_gold_mg_per_batch=mean_refined,
            annual_batches=annual_batches,
            annual_refined_gold_g=annual_gold_g,
            annual_product_mass_g=annual_product_mass_g,
            annual_revenue_usd=revenue,
            annual_energy_cost_usd=energy_cost,
            annual_consumables_cost_usd=consumables_cost,
            annual_fixed_cost_usd=scenario.economics.annual_fixed_cost_usd,
            annual_screening_margin_usd=margin,
            energy_intensity_kwh_per_g_gold=energy_intensity,
            model_warning=(
                "Screening result only. Hypothesized yields and economics are not experimental "
                "evidence, and the model recovers only gold already present in the feed."
            ),
        )


def sensitivity_grid(
    scenario: Scenario,
    concentrations_mg_l: Sequence[object],
    affinity_capture_fractions: Sequence[object],
) -> list[CampaignResult]:
    """Evaluate a deterministic cross-product of feed and affinity hypotheses."""

    if not concentrations_mg_l:
        raise ScenarioError("concentrations_mg_l cannot be empty")
    if not affinity_capture_fractions:
        raise ScenarioError("affinity_capture_fractions cannot be empty")
    results: list[CampaignResult] = []
    for concentration_raw in concentrations_mg_l:
        concentration = _nonnegative(concentration_raw, "sensitivity.gold_concentration_mg_l")
        for affinity_raw in affinity_capture_fractions:
            affinity = _fraction(affinity_raw, "sensitivity.affinity_capture_fraction")
            candidate = replace(
                scenario,
                name=(
                    f"{scenario.name} | Au={concentration} mg/L | "
                    f"affinity={affinity}"
                ),
                feed=replace(scenario.feed, gold_concentration_mg_l=concentration),
                process=replace(scenario.process, affinity_capture_fraction=affinity),
            )
            results.append(evaluate(candidate))
    return results
