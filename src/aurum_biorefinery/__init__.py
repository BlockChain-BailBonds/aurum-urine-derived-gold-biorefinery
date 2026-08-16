"""AURUM deterministic biorefinery modeling package."""

from .model import (
    CampaignResult,
    EconomicsSpec,
    FeedSpec,
    ProcessSpec,
    Scenario,
    ScenarioError,
    SecretomeSpec,
    StageMassBalance,
    evaluate,
    sensitivity_grid,
)

__all__ = [
    "CampaignResult",
    "EconomicsSpec",
    "FeedSpec",
    "ProcessSpec",
    "Scenario",
    "ScenarioError",
    "SecretomeSpec",
    "StageMassBalance",
    "evaluate",
    "sensitivity_grid",
]

__version__ = "0.1.0"

