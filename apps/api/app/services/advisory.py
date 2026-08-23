from datetime import UTC, datetime, timedelta
from math import asin, cos, radians, sin, sqrt

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.advisory_rules import RULES, AdvisoryRules
from app.models import Advisory, Consignment, Outbreak, SurveillanceUpdate, VaccinationEvent
from app.models.core import OutbreakStatus, RiskState, VaccinationEvidence, VerificationLevel
from app.repositories.advisories import AdvisoryRepository


class AdvisoryService:
    """Rules-first movement assessment. No ML, routing, or external data is used."""

    def __init__(self, repository: AdvisoryRepository | None = None, rules: AdvisoryRules = RULES) -> None:
        self.repository = repository or AdvisoryRepository()
        self.rules = rules

    def evaluate(self, db: Session, consignment_id: int, now: datetime | None = None) -> Advisory:
        now = now or datetime.now(UTC)
        consignment = self.repository.get_consignment(db, consignment_id)
        if not consignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consignment not found")
        all_outbreaks = self.repository.list_relevant_outbreaks(db, now - timedelta(days=self.rules.confirmed_outbreak_window_days))
        confirmed = [outbreak for outbreak in all_outbreaks if outbreak.status == OutbreakStatus.CONFIRMED and outbreak.detected_at >= now - timedelta(days=self.rules.confirmed_outbreak_window_days) and self._is_relevant(consignment, outbreak)]
        suspected = [outbreak for outbreak in all_outbreaks if outbreak.status == OutbreakStatus.SUSPECTED and outbreak.detected_at >= now - timedelta(days=self.rules.suspected_outbreak_window_days) and self._is_relevant(consignment, outbreak)]
        factors = self._coverage_factors(db, consignment, now)
        coverage = sum(int(factor["score"]) for factor in factors)
        risk_state, reasons, action = self._determine_state(consignment, confirmed, suspected, coverage)
        return self.repository.add_advisory(db, Advisory(
            consignment_id=consignment.id,
            risk_state=risk_state,
            evidence_coverage_score=coverage,
            reasons=reasons,
            evidence_factors=factors,
            recommended_action=action,
            rules_version=self.rules.version,
        ))

    def _determine_state(self, consignment: Consignment, confirmed: list[Outbreak], suspected: list[Outbreak], coverage: int) -> tuple[RiskState, list[dict[str, str]], str]:
        if confirmed:
            outbreak = confirmed[0]
            return RiskState.RED, [
                {"code": "confirmed_outbreak_exposure", "text": f"A confirmed {outbreak.disease_name} outbreak is relevant to this movement near {outbreak.location.name}."},
                {"code": "valid_time_window", "text": f"The confirmed outbreak falls inside the {self.rules.confirmed_outbreak_window_days}-day active risk window."},
            ], "Do not proceed until authorised veterinary guidance is obtained."
        if suspected:
            outbreak = suspected[0]
            return RiskState.AMBER, [
                {"code": "suspected_outbreak_exposure", "text": f"A suspected {outbreak.disease_name} outbreak is relevant to this movement near {outbreak.location.name}."},
                {"code": "precaution_required", "text": "Use precautionary inspection and verify current local evidence before movement."},
            ], "Inspect the consignment, verify evidence, and seek veterinary advice before proceeding."
        if consignment.vaccination_evidence in [VaccinationEvidence.DECLARED, VaccinationEvidence.UNKNOWN]:
            description = "declared but not independently verified" if consignment.vaccination_evidence == VaccinationEvidence.DECLARED else "unknown"
            return RiskState.AMBER, [
                {"code": "vaccination_precaution", "text": f"Vaccination evidence is {description}."},
                {"code": "precaution_required", "text": "No high-risk confirmed outbreak was found, but a precaution is still required."},
            ], "Verify vaccination evidence and complete a precautionary inspection before proceeding."
        if coverage < self.rules.minimum_safe_decision_score:
            return RiskState.GREY, [
                {"code": "insufficient_evidence", "text": f"Evidence Coverage Score is {coverage}/100, below the {self.rules.minimum_safe_decision_score}/100 safe-decision threshold."},
                {"code": "not_low_risk", "text": "Grey means the available evidence is insufficient; it does not mean lower risk."},
            ], "Request field verification or apply precaution before movement."
        return RiskState.GREEN, [
            {"code": "no_relevant_active_outbreak", "text": "No relevant active confirmed or suspected outbreak was found in the configured time windows."},
            {"code": "sufficient_evidence", "text": f"Evidence Coverage Score is {coverage}/100, meeting the safe-decision threshold."},
        ], "Proceed with the advisory record and retain the movement reference."

    def _coverage_factors(self, db: Session, consignment: Consignment, now: datetime) -> list[dict[str, object]]:
        origin_update = self.repository.latest_surveillance(db, consignment.origin_location_id)
        destination_update = self.repository.latest_surveillance(db, consignment.destination_location_id)
        surveillance_date = min_date(origin_update, destination_update)
        surveillance_score, surveillance_text = self._surveillance_score(surveillance_date, now)
        verification_score, verification_text = self._verification_score(origin_update, destination_update)
        vaccination = self.repository.latest_vaccination(db, consignment.id)
        vaccination_score, vaccination_text, vaccination_date = self._vaccination_score(vaccination, now)
        movement_score, movement_text = self._movement_score(consignment)
        return [
            {"key": "surveillance_freshness", "label": "Veterinary / surveillance update freshness", "score": surveillance_score, "max_score": self.rules.factor_weight, "freshness_date": iso_or_none(surveillance_date), "explanation": surveillance_text},
            {"key": "verification_availability", "label": "Laboratory / verification availability", "score": verification_score, "max_score": self.rules.factor_weight, "freshness_date": iso_or_none(surveillance_date), "explanation": verification_text},
            {"key": "vaccination_freshness", "label": "Vaccination-evidence freshness", "score": vaccination_score, "max_score": self.rules.factor_weight, "freshness_date": iso_or_none(vaccination_date), "explanation": vaccination_text},
            {"key": "movement_registration", "label": "Movement-registration coverage", "score": movement_score, "max_score": self.rules.factor_weight, "freshness_date": consignment.departure_at.isoformat(), "explanation": movement_text},
        ]

    def _surveillance_score(self, updated_at: datetime | None, now: datetime) -> tuple[int, str]:
        if not updated_at: return 0, "No surveillance update is available for both movement endpoints."
        age = (now - updated_at).days
        if age <= self.rules.surveillance_fresh_days: return 25, f"Endpoint surveillance updates are current ({age} day(s) old)."
        if age <= self.rules.surveillance_ageing_days: return 15, f"Endpoint surveillance updates are ageing ({age} days old)."
        return 0, f"Endpoint surveillance updates are stale ({age} days old)."

    def _verification_score(self, origin: SurveillanceUpdate | None, destination: SurveillanceUpdate | None) -> tuple[int, str]:
        updates = [item for item in [origin, destination] if item]
        verified = [item for item in updates if item.verification_level in [VerificationLevel.VETERINARY_VERIFIED, VerificationLevel.LABORATORY_CONFIRMED]]
        if len(verified) == 2: return 25, "Both endpoints have verified veterinary or laboratory evidence."
        if len(verified) == 1: return 12, "Only one endpoint has verified veterinary or laboratory evidence."
        return 0, "No verified veterinary or laboratory evidence is available for the endpoints."

    def _vaccination_score(self, event: VaccinationEvent | None, now: datetime) -> tuple[int, str, datetime | None]:
        if not event: return 0, "No persisted vaccination-evidence record is available.", None
        age = (now - event.recorded_at).days
        if event.evidence == VaccinationEvidence.VERIFIED and age <= self.rules.vaccination_fresh_days: return 25, f"Verified vaccination evidence is current ({age} day(s) old).", event.recorded_at
        if event.evidence == VaccinationEvidence.DECLARED and age <= self.rules.vaccination_fresh_days: return 15, f"Vaccination evidence is declared ({age} day(s) old), not independently verified.", event.recorded_at
        return 0, f"Vaccination evidence is {event.evidence.value} or stale ({age} days old).", event.recorded_at

    def _movement_score(self, consignment: Consignment) -> tuple[int, str]:
        has_departure = any(event.event_type.value == "departure" for event in consignment.movement_events)
        if has_departure and consignment.vehicle_id and consignment.origin_location_id != consignment.destination_location_id:
            return 25, "Origin, destination, vehicle reference, departure time, and departure event are recorded."
        return 10, "The movement record is only partially complete."

    def _is_relevant(self, consignment: Consignment, outbreak: Outbreak) -> bool:
        if outbreak.location_id in [consignment.origin_location_id, consignment.destination_location_id]: return True
        return any(haversine_km(outbreak.location.latitude, outbreak.location.longitude, location.latitude, location.longitude) <= self.rules.nearby_risk_radius_km for location in [consignment.origin_location, consignment.destination_location])


def haversine_km(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    lat_delta, lon_delta = radians(lat_b - lat_a), radians(lon_b - lon_a)
    a = sin(lat_delta / 2) ** 2 + cos(radians(lat_a)) * cos(radians(lat_b)) * sin(lon_delta / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def min_date(*updates: SurveillanceUpdate | None) -> datetime | None:
    dates = [item.updated_at for item in updates if item]
    return min(dates) if len(dates) == len(updates) else None


def iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
