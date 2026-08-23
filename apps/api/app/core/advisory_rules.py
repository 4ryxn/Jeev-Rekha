"""Single, transparent configuration point for Phase 3 deterministic advisory rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AdvisoryRules:
    version: str = "phase3-v1"
    confirmed_outbreak_window_days: int = 21
    suspected_outbreak_window_days: int = 14
    nearby_risk_radius_km: float = 3.0
    surveillance_fresh_days: int = 7
    surveillance_ageing_days: int = 14
    vaccination_fresh_days: int = 180
    minimum_safe_decision_score: int = 70
    factor_weight: int = 25


RULES = AdvisoryRules()
