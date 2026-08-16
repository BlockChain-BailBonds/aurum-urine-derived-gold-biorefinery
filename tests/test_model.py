import unittest
from dataclasses import replace
from decimal import Decimal

from aurum_biorefinery import Scenario, ScenarioError, evaluate, sensitivity_grid


def scenario_mapping() -> dict:
    return {
        "name": "test scenario",
        "evidence_status": "hypothesis",
        "feed": {
            "batch_volume_l": "100",
            "gold_concentration_mg_l": "0.25",
            "accessible_gold_fraction": "0.90",
        },
        "secretome": {
            "capture_phase_volume_l": "5",
            "binding_capacity_mg_l": "4.5",
            "active_fraction": "0.80",
            "reuse_cycles": 3,
            "per_reuse_capacity_retention": "0.90",
        },
        "process": {
            "affinity_capture_fraction": "0.85",
            "reduction_yield_fraction": "0.92",
            "harvest_yield_fraction": "0.95",
            "refining_yield_fraction": "0.99",
            "product_purity_fraction": "0.995",
            "batches_per_day": "2",
            "operating_days_per_year": 300,
            "energy_kwh_per_batch": "1.5",
        },
        "economics": {
            "gold_price_usd_g": "75",
            "electricity_price_usd_kwh": "0.12",
            "consumables_usd_per_batch": "4.5",
            "annual_fixed_cost_usd": "250",
        },
    }


class ModelTests(unittest.TestCase):
    def test_reference_scenario_is_mass_conserving(self) -> None:
        result = evaluate(Scenario.from_mapping(scenario_mapping()))
        balance = result.first_use_balance
        self.assertEqual(balance.gold_in_feed_mg, Decimal("25.00"))
        self.assertEqual(balance.accessible_gold_mg, Decimal("22.5000"))
        self.assertEqual(balance.captured_gold_mg, Decimal("18.000"))
        self.assertEqual(balance.refined_gold_mg, Decimal("15.57468000"))
        self.assertEqual(balance.accounted_gold_mg, balance.gold_in_feed_mg)
        self.assertTrue(balance.capacity_limited)
        self.assertEqual(result.mean_refined_gold_mg_per_batch, Decimal("14.0691276000"))
        self.assertEqual(result.annual_refined_gold_g, Decimal("8.4414765600"))
        self.assertEqual(result.annual_screening_margin_usd, Decimal("-2424.8892580000000"))

    def test_zero_gold_has_zero_recovery_and_no_division_error(self) -> None:
        raw = scenario_mapping()
        raw["feed"]["gold_concentration_mg_l"] = 0
        result = evaluate(Scenario.from_mapping(raw))
        self.assertEqual(result.annual_refined_gold_g, Decimal("0"))
        self.assertIsNone(result.energy_intensity_kwh_per_g_gold)
        self.assertEqual(result.first_use_balance.total_recovery_fraction, Decimal("0"))

    def test_affinity_can_be_limiting_instead_of_capacity(self) -> None:
        raw = scenario_mapping()
        raw["process"]["affinity_capture_fraction"] = "0.10"
        result = evaluate(Scenario.from_mapping(raw))
        self.assertFalse(result.first_use_balance.capacity_limited)
        self.assertEqual(result.first_use_balance.captured_gold_mg, Decimal("2.250000"))

    def test_reuse_index_is_bounded(self) -> None:
        scenario = Scenario.from_mapping(scenario_mapping())
        with self.assertRaisesRegex(ScenarioError, "reuse_index"):
            scenario.secretome.effective_capacity_mg(3)
        with self.assertRaisesRegex(ScenarioError, "reuse_index"):
            scenario.secretome.effective_capacity_mg(-1)

    def test_unknown_fields_are_rejected(self) -> None:
        raw = scenario_mapping()
        raw["creates_gold"] = True
        with self.assertRaisesRegex(ScenarioError, "unknown fields: creates_gold"):
            Scenario.from_mapping(raw)

    def test_invalid_fractions_and_nonfinite_values_are_rejected(self) -> None:
        raw = scenario_mapping()
        raw["feed"]["accessible_gold_fraction"] = "1.01"
        with self.assertRaisesRegex(ScenarioError, r"\[0, 1\]"):
            Scenario.from_mapping(raw)
        raw = scenario_mapping()
        raw["feed"]["gold_concentration_mg_l"] = "NaN"
        with self.assertRaisesRegex(ScenarioError, "finite"):
            Scenario.from_mapping(raw)

    def test_bad_evidence_status_is_rejected(self) -> None:
        raw = scenario_mapping()
        raw["evidence_status"] = "proven"
        with self.assertRaisesRegex(ScenarioError, "bench-validated"):
            Scenario.from_mapping(raw)

    def test_missing_and_nonobject_sections_are_rejected(self) -> None:
        raw = scenario_mapping()
        del raw["feed"]
        with self.assertRaisesRegex(ScenarioError, "missing required fields: feed"):
            Scenario.from_mapping(raw)
        raw = scenario_mapping()
        raw["secretome"] = []
        with self.assertRaisesRegex(ScenarioError, "secretome must be an object"):
            Scenario.from_mapping(raw)

    def test_invalid_text_integer_and_positive_fields_are_rejected(self) -> None:
        raw = scenario_mapping()
        raw["name"] = " "
        with self.assertRaisesRegex(ScenarioError, "non-empty string"):
            Scenario.from_mapping(raw)
        raw = scenario_mapping()
        raw["secretome"]["reuse_cycles"] = "3.5"
        with self.assertRaisesRegex(ScenarioError, "must be an integer"):
            Scenario.from_mapping(raw)
        raw = scenario_mapping()
        raw["secretome"]["reuse_cycles"] = 0
        with self.assertRaisesRegex(ScenarioError, "at least 1"):
            Scenario.from_mapping(raw)
        raw = scenario_mapping()
        raw["feed"]["batch_volume_l"] = 0
        with self.assertRaisesRegex(ScenarioError, "greater than zero"):
            Scenario.from_mapping(raw)

    def test_negative_and_boolean_numeric_inputs_are_rejected(self) -> None:
        raw = scenario_mapping()
        raw["economics"]["annual_fixed_cost_usd"] = -1
        with self.assertRaisesRegex(ScenarioError, "zero or greater"):
            Scenario.from_mapping(raw)
        raw = scenario_mapping()
        raw["process"]["operating_days_per_year"] = True
        with self.assertRaisesRegex(ScenarioError, "must be an integer"):
            Scenario.from_mapping(raw)

    def test_sensitivity_grid_is_ordered_and_complete(self) -> None:
        scenario = Scenario.from_mapping(scenario_mapping())
        results = sensitivity_grid(scenario, ["0", "0.1"], ["0.25", "0.75"])
        self.assertEqual(len(results), 4)
        self.assertIn("Au=0 mg/L | affinity=0.25", results[0].scenario_name)
        self.assertIn("Au=0.1 mg/L | affinity=0.75", results[-1].scenario_name)

    def test_empty_sensitivity_axis_is_rejected(self) -> None:
        scenario = Scenario.from_mapping(scenario_mapping())
        with self.assertRaisesRegex(ScenarioError, "cannot be empty"):
            sensitivity_grid(scenario, [], ["0.5"])
        with self.assertRaisesRegex(ScenarioError, "cannot be empty"):
            sensitivity_grid(scenario, ["0.1"], [])

    def test_immutable_scenario_can_be_safely_replaced(self) -> None:
        scenario = Scenario.from_mapping(scenario_mapping())
        changed = replace(scenario, name="changed")
        self.assertEqual(scenario.name, "test scenario")
        self.assertEqual(changed.name, "changed")


if __name__ == "__main__":
    unittest.main()
