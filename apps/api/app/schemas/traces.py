from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.core import LocationDataSource, TraceDirection, TraceEvidenceLevel
from app.schemas.core import LocationRead, OutbreakRead


TRACE_DISCLAIMER = "Trace results identify contacts for veterinary review; they do not confirm disease transmission."


class TraceCreateRequest(BaseModel):
    direction: TraceDirection
    review_window_days: int | None = Field(default=None, ge=1, le=90)


class TraceConfigurationRead(BaseModel):
    disease_name: str
    review_window_days: int
    source_label: str


class TraceFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: str
    relationship_type: str
    event_timestamp: datetime
    evidence_level: TraceEvidenceLevel
    explanation: str
    review_status: str


class TraceImpactedCounts(BaseModel):
    findings: int
    locations: int
    vehicles: int
    consignments: int


class TraceRunResponse(BaseModel):
    id: int
    outbreak: OutbreakRead
    direction: TraceDirection
    data_source: LocationDataSource
    window_start: datetime
    window_end: datetime
    review_window_days: int
    source_label: str
    findings: list[TraceFindingResponse]
    timeline: list[TraceFindingResponse]
    impacted_counts: TraceImpactedCounts
    impacted_locations: list[LocationRead]
    created_at: datetime
    disclaimer: str = TRACE_DISCLAIMER
