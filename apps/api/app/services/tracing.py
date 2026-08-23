"""Deterministic, evidence-backed trace-run creation for fictional synthetic records."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.trace_windows import TraceReviewWindow, get_trace_review_window
from app.models import Consignment, Location, MovementEvent, Outbreak, TraceFinding, TraceRun, Vehicle
from app.models.core import LocationType, OutbreakStatus, TraceDirection, TraceEvidenceLevel
from app.repositories.traces import TraceRepository


class TraceNotFoundError(LookupError):
    """Raised when a requested outbreak record does not exist."""


class TraceValidationError(ValueError):
    """Raised when a trace request cannot be evaluated from persisted evidence."""


class TraceService:
    """Creates explainable trace records from persisted movement events only.

    A trace starts from an event recorded at a confirmed outbreak location. Other
    events of that same consignment inside the selected review window are indirect
    route or market/checkpost contacts. This is operational review support only.
    """

    def __init__(self, repository: TraceRepository | None = None) -> None:
        self.repository = repository or TraceRepository()

    def create_rewind_trace(self, db: Session, outbreak_id: int, window_override: int | None = None) -> TraceRun:
        return self._create_trace(db, outbreak_id, TraceDirection.REWIND, window_override)

    def create_fast_forward_trace(self, db: Session, outbreak_id: int, window_override: int | None = None) -> TraceRun:
        return self._create_trace(db, outbreak_id, TraceDirection.FAST_FORWARD, window_override)

    def _create_trace(
        self, db: Session, outbreak_id: int, direction: TraceDirection, window_override: int | None
    ) -> TraceRun:
        outbreak = db.get(Outbreak, outbreak_id)
        if outbreak is None:
            raise TraceNotFoundError("Outbreak not found")
        if outbreak.status != OutbreakStatus.CONFIRMED:
            raise TraceValidationError("Only confirmed outbreaks can create a trace run")

        configured_window = get_trace_review_window(outbreak.disease_name)
        review_window_days = self._review_window_days(configured_window, window_override)
        reference_time = outbreak.confirmed_at or outbreak.detected_at
        window_start, window_end = self._window(direction, reference_time, review_window_days)
        trace_run = self.repository.create_trace_run(
            db,
            TraceRun(
                outbreak_id=outbreak.id,
                direction=direction,
                window_start=window_start,
                window_end=window_end,
                parameters={
                    "disease_name": configured_window.canonical_name,
                    "review_window_days": review_window_days,
                    "source_label": configured_window.source_label,
                    "reference_timestamp": reference_time.isoformat(),
                },
            ),
        )
        findings = self._findings(db, trace_run.id, outbreak, direction, window_start, window_end)
        if findings:
            self.repository.add_trace_findings(db, findings)
        return self.repository.get_trace_run_with_findings(db, trace_run.id)  # type: ignore[return-value]

    @staticmethod
    def _review_window_days(configured: TraceReviewWindow, override: int | None) -> int:
        if override is None:
            return configured.review_window_days
        if isinstance(override, bool) or not isinstance(override, int) or not 1 <= override <= 90:
            raise TraceValidationError("Review-window override must be an integer from 1 to 90 days")
        return override

    @staticmethod
    def _window(direction: TraceDirection, reference_time: datetime, review_window_days: int) -> tuple[datetime, datetime]:
        interval = timedelta(days=review_window_days)
        if direction == TraceDirection.REWIND:
            return reference_time - interval, reference_time
        return reference_time, reference_time + interval

    def _findings(
        self,
        db: Session,
        trace_run_id: int,
        outbreak: Outbreak,
        direction: TraceDirection,
        window_start: datetime,
        window_end: datetime,
    ) -> list[TraceFinding]:
        time_filter = [MovementEvent.occurred_at >= window_start, MovementEvent.occurred_at <= window_end]
        if direction == TraceDirection.REWIND:
            time_filter[-1] = MovementEvent.occurred_at < window_end

        rows = list(
            db.execute(
                select(MovementEvent, Consignment, Location, Vehicle)
                .join(Consignment, MovementEvent.consignment_id == Consignment.id)
                .join(Location, MovementEvent.location_id == Location.id)
                .join(Vehicle, Consignment.vehicle_id == Vehicle.id)
                .where(*time_filter)
                .order_by(MovementEvent.occurred_at, MovementEvent.id)
            )
        )
        connected_consignment_ids = {
            event.consignment_id for event, _consignment, _location, _vehicle in rows if event.location_id == outbreak.location_id
        }
        if not connected_consignment_ids:
            return []

        findings: list[TraceFinding] = []
        seen: set[tuple[str, str, str, datetime]] = set()
        movement_relationship = "incoming_movement" if direction == TraceDirection.REWIND else "outgoing_movement"
        for event, consignment, location, vehicle in rows:
            if consignment.id not in connected_consignment_ids:
                continue
            is_direct = event.location_id == outbreak.location_id
            if is_direct:
                self._append(
                    findings, seen, trace_run_id, "consignment", str(consignment.id), movement_relationship,
                    event.occurred_at, TraceEvidenceLevel.DIRECT,
                    f"Consignment {consignment.id} recorded a movement at {location.name} within the configured review window; requires veterinary review.",
                )
                self._append(
                    findings, seen, trace_run_id, "vehicle", str(vehicle.id), "shared_vehicle",
                    event.occurred_at, TraceEvidenceLevel.DIRECT,
                    f"Vehicle {vehicle.vehicle_reference} recorded a movement connected to {location.name} within the configured review window; requires veterinary review.",
                )
                continue

            entity_type, relationship = self._indirect_entity(location)
            self._append(
                findings, seen, trace_run_id, entity_type, str(location.id), relationship,
                event.occurred_at, TraceEvidenceLevel.INDIRECT,
                self._indirect_explanation(location, consignment, vehicle),
            )
        return findings

    @staticmethod
    def _indirect_entity(location: Location) -> tuple[str, str]:
        if location.type == LocationType.MARKET:
            return "market", "shared_market"
        if location.type == LocationType.CHECKPOST:
            return "checkpost", "route_contact"
        return "location", "route_contact"

    @staticmethod
    def _indirect_explanation(location: Location, consignment: Consignment, vehicle: Vehicle) -> str:
        if location.type == LocationType.MARKET:
            return f"Market visit at {location.name} by consignment {consignment.id} using vehicle {vehicle.vehicle_reference} is an indirect contact and requires veterinary review."
        if location.type == LocationType.CHECKPOST:
            return f"Checkpoint record at {location.name} for consignment {consignment.id} using vehicle {vehicle.vehicle_reference} is an indirect contact and requires veterinary review."
        return f"Movement record at {location.name} for consignment {consignment.id} using vehicle {vehicle.vehicle_reference} is an indirect contact and requires veterinary review."

    @staticmethod
    def _append(
        findings: list[TraceFinding],
        seen: set[tuple[str, str, str, datetime]],
        trace_run_id: int,
        entity_type: str,
        entity_id: str,
        relationship_type: str,
        event_timestamp: datetime,
        evidence_level: TraceEvidenceLevel,
        explanation: str,
    ) -> None:
        key = (entity_type, entity_id, relationship_type, event_timestamp)
        if key in seen:
            return
        seen.add(key)
        findings.append(
            TraceFinding(
                trace_run_id=trace_run_id,
                entity_type=entity_type,
                entity_id=entity_id,
                relationship_type=relationship_type,
                event_timestamp=event_timestamp,
                evidence_level=evidence_level,
                explanation=explanation,
                review_status="requires_veterinary_review",
            )
        )
