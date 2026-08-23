from datetime import datetime
from enum import StrEnum

from geoalchemy2 import Geometry
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    """Persist API-facing lowercase values rather than Python enum member names."""
    return [member.value for member in enum_class]


class LocationType(StrEnum):
    VILLAGE = "village"
    MARKET = "market"
    CHECKPOST = "checkpost"
    VETERINARY_CENTRE = "veterinary_centre"


class OutbreakStatus(StrEnum):
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    CLOSED = "closed"


class VerificationLevel(StrEnum):
    REPORTED = "reported"
    VETERINARY_VERIFIED = "veterinary_verified"
    LABORATORY_CONFIRMED = "laboratory_confirmed"


class VaccinationEvidence(StrEnum):
    VERIFIED = "verified"
    DECLARED = "declared"
    UNKNOWN = "unknown"


class MovementEventType(StrEnum):
    DEPARTURE = "departure"
    MARKET_ENTRY = "market_entry"
    CHECKPOINT = "checkpoint"
    ARRIVAL = "arrival"


class RiskState(StrEnum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"
    GREY = "grey"


class TraceDirection(StrEnum):
    REWIND = "rewind"
    FAST_FORWARD = "fast_forward"


class TraceEvidenceLevel(StrEnum):
    DIRECT = "direct"
    INDIRECT = "indirect"


class TimestampedModel:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Location(TimestampedModel, Base):
    __tablename__ = "locations"
    __table_args__ = (Index("ix_locations_type", "type"), Index("ix_locations_geometry", "geometry", postgresql_using="gist"))

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    type: Mapped[LocationType] = mapped_column(Enum(LocationType, values_callable=enum_values), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    geometry: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False)


class Vehicle(TimestampedModel, Base):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)


class Outbreak(TimestampedModel, Base):
    __tablename__ = "outbreaks"
    __table_args__ = (Index("ix_outbreaks_status_detected_at", "status", "detected_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    disease_name: Mapped[str] = mapped_column(String(120), nullable=False)
    species: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[OutbreakStatus] = mapped_column(Enum(OutbreakStatus, values_callable=enum_values), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    suspected_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confirmed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mortality_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    verification_level: Mapped[VerificationLevel] = mapped_column(Enum(VerificationLevel, values_callable=enum_values), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    location: Mapped[Location] = relationship()
    trace_runs: Mapped[list["TraceRun"]] = relationship(cascade="all, delete-orphan", back_populates="outbreak")


class Consignment(TimestampedModel, Base):
    __tablename__ = "consignments"
    __table_args__ = (
        CheckConstraint("animal_count > 0", name="ck_consignments_positive_animal_count"),
        CheckConstraint("origin_location_id <> destination_location_id", name="ck_consignments_different_locations"),
        Index("ix_consignments_departure_at", "departure_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    origin_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    destination_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    species: Mapped[str] = mapped_column(String(80), nullable=False)
    animal_count: Mapped[int] = mapped_column(Integer, nullable=False)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    departure_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vaccination_evidence: Mapped[VaccinationEvidence] = mapped_column(Enum(VaccinationEvidence, values_callable=enum_values), nullable=False)
    origin_location: Mapped[Location] = relationship(foreign_keys=[origin_location_id])
    destination_location: Mapped[Location] = relationship(foreign_keys=[destination_location_id])
    vehicle: Mapped[Vehicle] = relationship()
    movement_events: Mapped[list["MovementEvent"]] = relationship(cascade="all, delete-orphan")
    vaccination_events: Mapped[list["VaccinationEvent"]] = relationship(cascade="all, delete-orphan")
    advisories: Mapped[list["Advisory"]] = relationship(cascade="all, delete-orphan", back_populates="consignment")


class MovementEvent(TimestampedModel, Base):
    __tablename__ = "movement_events"
    __table_args__ = (Index("ix_movement_events_consignment_occurred_at", "consignment_id", "occurred_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    consignment_id: Mapped[int] = mapped_column(ForeignKey("consignments.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    event_type: Mapped[MovementEventType] = mapped_column(Enum(MovementEventType, values_callable=enum_values), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[Location] = relationship()


class VaccinationEvent(TimestampedModel, Base):
    """Persisted vaccination-evidence record; all Phase 3 seed rows are synthetic."""
    __tablename__ = "vaccination_events"
    __table_args__ = (Index("ix_vaccination_events_consignment_recorded_at", "consignment_id", "recorded_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    consignment_id: Mapped[int] = mapped_column(ForeignKey("consignments.id"), nullable=False)
    evidence: Mapped[VaccinationEvidence] = mapped_column(Enum(VaccinationEvidence, values_callable=enum_values), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verification_level: Mapped[VerificationLevel] = mapped_column(Enum(VerificationLevel, values_callable=enum_values), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class SurveillanceUpdate(TimestampedModel, Base):
    """Location-level freshness and verification evidence used by deterministic scoring."""
    __tablename__ = "surveillance_updates"
    __table_args__ = (Index("ix_surveillance_updates_location_updated_at", "location_id", "updated_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verification_level: Mapped[VerificationLevel] = mapped_column(Enum(VerificationLevel, values_callable=enum_values), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    location: Mapped[Location] = relationship()


class Advisory(Base):
    __tablename__ = "advisories"
    __table_args__ = (Index("ix_advisories_consignment_evaluated_at", "consignment_id", "evaluated_at"), Index("ix_advisories_risk_state", "risk_state"))

    id: Mapped[int] = mapped_column(primary_key=True)
    consignment_id: Mapped[int] = mapped_column(ForeignKey("consignments.id"), nullable=False)
    risk_state: Mapped[RiskState] = mapped_column(Enum(RiskState, values_callable=enum_values), nullable=False)
    evidence_coverage_score: Mapped[int] = mapped_column(Integer, nullable=False)
    reasons: Mapped[list[dict[str, str]]] = mapped_column(JSONB, nullable=False)
    evidence_factors: Mapped[list[dict[str, object]]] = mapped_column(JSONB, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rules_version: Mapped[str] = mapped_column(String(32), nullable=False)
    consignment: Mapped[Consignment] = relationship(back_populates="advisories")


class RouteSegment(Base):
    __tablename__ = "route_segments"
    id: Mapped[int] = mapped_column(primary_key=True)
    start_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    end_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    distance_km: Mapped[float] = mapped_column(nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(nullable=False)
    path: Mapped[list[list[float]]] = mapped_column(JSONB, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    start_location: Mapped[Location] = relationship(foreign_keys=[start_location_id])
    end_location: Mapped[Location] = relationship(foreign_keys=[end_location_id])


class RouteAssessment(Base):
    __tablename__ = "route_assessments"
    __table_args__ = (Index("ix_route_assessments_consignment_assessed_at", "consignment_id", "assessed_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    consignment_id: Mapped[int] = mapped_column(ForeignKey("consignments.id"), nullable=False)
    preferred_route: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    safer_route: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    preferred_distance_km: Mapped[float] = mapped_column(nullable=False)
    preferred_minutes: Mapped[int] = mapped_column(nullable=False)
    safer_distance_km: Mapped[float | None] = mapped_column()
    safer_minutes: Mapped[int | None] = mapped_column()
    risk_reduction: Mapped[str] = mapped_column(String(32), nullable=False)
    route_reasons: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    assessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    consignment: Mapped[Consignment] = relationship()


class TraceRun(TimestampedModel, Base):
    """Persisted trace-run setup and output ownership; trace algorithms arrive in Phase 5A.2."""

    __tablename__ = "trace_runs"
    __table_args__ = (
        CheckConstraint("direction IN ('rewind', 'fast_forward')", name="ck_trace_runs_direction"),
        Index("ix_trace_runs_outbreak_created_at", "outbreak_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    outbreak_id: Mapped[int] = mapped_column(ForeignKey("outbreaks.id", ondelete="CASCADE"), nullable=False)
    direction: Mapped[TraceDirection] = mapped_column(String(32), nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    parameters: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    outbreak: Mapped[Outbreak] = relationship(back_populates="trace_runs")
    findings: Mapped[list["TraceFinding"]] = relationship(
        cascade="all, delete-orphan", back_populates="trace_run", order_by="TraceFinding.event_timestamp"
    )


class TraceFinding(TimestampedModel, Base):
    """An evidence-backed finding owned by a persisted trace run."""

    __tablename__ = "trace_findings"
    __table_args__ = (
        CheckConstraint("evidence_level IN ('direct', 'indirect')", name="ck_trace_findings_evidence_level"),
        Index("ix_trace_findings_run_event_timestamp", "trace_run_id", "event_timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    trace_run_id: Mapped[int] = mapped_column(ForeignKey("trace_runs.id", ondelete="CASCADE"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence_level: Mapped[TraceEvidenceLevel] = mapped_column(String(16), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(64), nullable=False, default="requires_veterinary_review", server_default="requires_veterinary_review"
    )
    trace_run: Mapped[TraceRun] = relationship(back_populates="findings")


class SyncReceipt(Base):
    __tablename__ = "sync_receipts"
    __table_args__ = (Index("ix_sync_receipts_received_at", "received_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    client_operation_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    operation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(32))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
