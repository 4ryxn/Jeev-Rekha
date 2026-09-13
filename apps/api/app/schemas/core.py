from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.models.core import (
    LocationType,
    LocationDataSource,
    MovementEventType,
    OutbreakSource,
    OutbreakStatus,
    VaccinationEvidence,
    VerificationLevel,
    RiskState,
    TraceDirection,
    TraceEvidenceLevel,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LocationRead(ORMModel):
    id: int
    name: str
    type: LocationType
    district: str
    state: str
    latitude: float
    longitude: float
    data_source: LocationDataSource
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def location_type(self) -> str:
        return "livestock_market" if self.type == LocationType.MARKET else self.type.value


class LocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    location_type: str
    district: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator("name", "district", "state")
    @classmethod
    def trim_location_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("location_type")
    @classmethod
    def validate_registry_location_type(cls, value: str) -> str:
        valid = {"village", "livestock_market", "checkpost", "veterinary_centre"}
        if value not in valid:
            raise ValueError("location_type must be village, livestock_market, checkpost, or veterinary_centre")
        return value


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    location_type: str | None = None
    district: str | None = Field(default=None, min_length=2, max_length=120)
    state: str | None = Field(default=None, min_length=2, max_length=120)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("name", "district", "state")
    @classmethod
    def trim_optional_location_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("location_type")
    @classmethod
    def validate_optional_registry_location_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        valid = {"village", "livestock_market", "checkpost", "veterinary_centre"}
        if value not in valid:
            raise ValueError("location_type must be village, livestock_market, checkpost, or veterinary_centre")
        return value

    @model_validator(mode="after")
    def require_one_change(self) -> "LocationUpdate":
        if not self.model_dump(exclude_none=True):
            raise ValueError("at least one location field must be provided")
        return self


class VehicleRead(ORMModel):
    id: int
    vehicle_reference: str
    created_at: datetime


class OutbreakCreate(BaseModel):
    disease_name: str = Field(min_length=2, max_length=120)
    species: str = Field(min_length=2, max_length=80)
    status: OutbreakStatus
    source: OutbreakSource = OutbreakSource.VET_OBSERVED
    location_id: int = Field(gt=0)
    data_source: LocationDataSource = LocationDataSource.DEMO_SEED
    review_radius_km: float | None = Field(default=None, gt=0)
    detected_at: datetime
    confirmed_at: datetime | None = None
    suspected_cases: int = Field(default=0, ge=0)
    confirmed_cases: int = Field(default=0, ge=0)
    mortality_count: int = Field(default=0, ge=0)
    verification_level: VerificationLevel
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("disease_name", "species")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class OutbreakRead(ORMModel):
    id: int
    disease_name: str
    species: str
    status: OutbreakStatus
    source: OutbreakSource
    location_id: int
    data_source: LocationDataSource
    review_radius_km: float | None
    detected_at: datetime
    confirmed_at: datetime | None
    suspected_cases: int
    confirmed_cases: int
    mortality_count: int
    verification_level: VerificationLevel
    notes: str | None
    created_at: datetime
    location: LocationRead


class ConsignmentCreate(BaseModel):
    origin_location_id: int = Field(gt=0)
    destination_location_id: int = Field(gt=0)
    data_source: LocationDataSource = LocationDataSource.DEMO_SEED
    species: str = Field(min_length=2, max_length=80)
    animal_count: int = Field(gt=0, le=100000)
    vehicle_reference: str = Field(min_length=3, max_length=64)
    departure_at: datetime
    vaccination_evidence: VaccinationEvidence

    @field_validator("species", "vehicle_reference")
    @classmethod
    def trim_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value.upper() if value == value.upper() else value

    @field_validator("destination_location_id")
    @classmethod
    def require_different_destination(cls, value: int, info: object) -> int:
        data = getattr(info, "data", {})
        if data.get("origin_location_id") == value:
            raise ValueError("destination must be different from origin")
        return value


class MovementEventRead(ORMModel):
    id: int
    consignment_id: int
    location_id: int
    event_type: MovementEventType
    occurred_at: datetime
    created_at: datetime
    location: LocationRead


class ConsignmentRead(ORMModel):
    id: int
    origin_location_id: int
    destination_location_id: int
    data_source: LocationDataSource
    species: str
    animal_count: int
    vehicle_id: int
    departure_at: datetime
    vaccination_evidence: VaccinationEvidence
    created_at: datetime
    origin_location: LocationRead
    destination_location: LocationRead
    vehicle: VehicleRead
    movement_events: list[MovementEventRead] = []


class EvidenceFactor(BaseModel):
    key: str
    label: str
    score: int = Field(ge=0, le=25)
    max_score: int = 25
    freshness_date: datetime | None = None
    explanation: str


class AdvisoryReason(BaseModel):
    code: str
    text: str


class AdvisoryEvaluateRequest(BaseModel):
    consignment_id: int = Field(gt=0)


class AdvisoryRead(ORMModel):
    id: int
    consignment_id: int
    risk_state: RiskState
    evidence_coverage_score: int = Field(ge=0, le=100)
    reasons: list[AdvisoryReason]
    evidence_factors: list[EvidenceFactor]
    recommended_action: str
    evaluated_at: datetime
    rules_version: str
    data_source: LocationDataSource
    policy_snapshot: dict[str, object] | None = None
    considered_outbreak_ids: list[int] | None = None
    route_state: str | None = None
    consignment: ConsignmentRead


class TraceFindingRead(ORMModel):
    id: int
    trace_run_id: int
    entity_type: str
    entity_id: str
    relationship_type: str
    event_timestamp: datetime
    evidence_level: TraceEvidenceLevel
    explanation: str
    review_status: str
    created_at: datetime


class TraceRunRead(ORMModel):
    id: int
    outbreak_id: int
    direction: TraceDirection
    window_start: datetime
    window_end: datetime
    parameters: dict[str, object]
    created_at: datetime
    findings: list[TraceFindingRead] = []
