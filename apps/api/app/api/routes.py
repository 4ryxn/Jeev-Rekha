from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.core import LocationType
from app.repositories.core import OperationsRepository
from app.repositories.advisories import AdvisoryRepository
from app.schemas import AdvisoryEvaluateRequest, AdvisoryRead, ConsignmentCreate, ConsignmentRead, LocationRead, OutbreakCreate, OutbreakRead, TraceConfigurationRead, TraceCreateRequest, TraceRunResponse
from app.services.advisory import AdvisoryService
from app.services.operations import OperationsService
from app.services.routing import RouteService
from app.schemas.routes import RouteAssessRequest, RouteAssessmentRead
from app.models import RouteAssessment
from app.models import Location, TraceRun
from app.repositories.traces import TraceRepository
from app.core.trace_windows import get_trace_review_window
from app.services.tracing import TraceNotFoundError, TraceService, TraceValidationError

router = APIRouter(prefix="/api/v1")
repository = OperationsRepository()
service = OperationsService(repository)
advisory_repository = AdvisoryRepository()
advisory_service = AdvisoryService(advisory_repository)
route_service=RouteService()
trace_repository = TraceRepository()
trace_service = TraceService(trace_repository)


@router.get("/locations", response_model=list[LocationRead], tags=["locations"])
def list_locations(type: LocationType | None = None, db: Session = Depends(get_db)) -> list[object]:
    return repository.list_locations(db, type)


@router.get("/outbreaks", response_model=list[OutbreakRead], tags=["outbreaks"])
def list_outbreaks(db: Session = Depends(get_db)) -> list[object]:
    return repository.list_outbreaks(db)


@router.post("/outbreaks", response_model=OutbreakRead, status_code=status.HTTP_201_CREATED, tags=["outbreaks"])
def create_outbreak(payload: OutbreakCreate, db: Session = Depends(get_db)) -> object:
    return service.create_outbreak(db, payload)


@router.get("/outbreaks/{outbreak_id}", response_model=OutbreakRead, tags=["outbreaks"])
def get_outbreak(outbreak_id: int, db: Session = Depends(get_db)) -> object:
    outbreak = repository.get_outbreak(db, outbreak_id)
    if not outbreak:
        raise HTTPException(status_code=404, detail="Outbreak not found")
    return outbreak


@router.get("/consignments", response_model=list[ConsignmentRead], tags=["consignments"])
def list_consignments(db: Session = Depends(get_db)) -> list[object]:
    return repository.list_consignments(db)


@router.post("/consignments", response_model=ConsignmentRead, status_code=status.HTTP_201_CREATED, tags=["consignments"])
def create_consignment(payload: ConsignmentCreate, db: Session = Depends(get_db)) -> object:
    return service.create_consignment(db, payload)


@router.get("/consignments/{consignment_id}", response_model=ConsignmentRead, tags=["consignments"])
def get_consignment(consignment_id: int, db: Session = Depends(get_db)) -> object:
    consignment = repository.get_consignment(db, consignment_id)
    if not consignment:
        raise HTTPException(status_code=404, detail="Consignment not found")
    return consignment


@router.post("/advisories/evaluate", response_model=AdvisoryRead, status_code=status.HTTP_201_CREATED, tags=["advisories"])
def evaluate_advisory(payload: AdvisoryEvaluateRequest, db: Session = Depends(get_db)) -> object:
    return advisory_service.evaluate(db, payload.consignment_id)


@router.get("/advisories/{advisory_id}", response_model=AdvisoryRead, tags=["advisories"])
def get_advisory(advisory_id: int, db: Session = Depends(get_db)) -> object:
    advisory = advisory_repository.get_advisory(db, advisory_id)
    if not advisory:
        raise HTTPException(status_code=404, detail="Advisory not found")
    return advisory


@router.get("/advisories", response_model=list[AdvisoryRead], tags=["advisories"])
def list_advisories(db: Session = Depends(get_db)) -> list[object]:
    return advisory_repository.list_recent_advisories(db)


@router.get("/consignments/{consignment_id}/advisories", response_model=list[AdvisoryRead], tags=["advisories"])
def list_consignments_advisories(consignment_id: int, db: Session = Depends(get_db)) -> list[object]:
    if not advisory_repository.get_consignment(db, consignment_id):
        raise HTTPException(status_code=404, detail="Consignment not found")
    return advisory_repository.list_consignments_advisories(db, consignment_id)
@router.post("/routes/assess",response_model=RouteAssessmentRead,status_code=201)
def assess_route(payload:RouteAssessRequest,db:Session=Depends(get_db)):
 try:return route_service.assess(db,payload.consignment_id)
 except ValueError as e:raise HTTPException(status_code=404,detail=str(e))
@router.get("/routes/assessments/{assessment_id}",response_model=RouteAssessmentRead)
def get_route(assessment_id:int,db:Session=Depends(get_db)):
 a=db.get(RouteAssessment,assessment_id)
 if not a:raise HTTPException(status_code=404,detail="Route assessment not found")
 return a
@router.get("/consignments/{consignment_id}/route-assessments",response_model=list[RouteAssessmentRead])
def list_routes(consignment_id:int,db:Session=Depends(get_db)):
 return list(db.scalars(select(RouteAssessment).where(RouteAssessment.consignment_id==consignment_id).order_by(RouteAssessment.assessed_at.desc())))


@router.get("/outbreaks/{outbreak_id}/trace-configuration", response_model=TraceConfigurationRead, tags=["traces"])
def get_trace_configuration(outbreak_id: int, db: Session = Depends(get_db)) -> object:
    outbreak = repository.get_outbreak(db, outbreak_id)
    if not outbreak:
        raise HTTPException(status_code=404, detail="Outbreak not found")
    configuration = get_trace_review_window(outbreak.disease_name)
    return TraceConfigurationRead(
        disease_name=configuration.canonical_name,
        review_window_days=configuration.review_window_days,
        source_label=configuration.source_label,
    )


@router.post("/outbreaks/{outbreak_id}/traces", response_model=TraceRunResponse, status_code=status.HTTP_201_CREATED, tags=["traces"])
def create_trace(outbreak_id: int, payload: TraceCreateRequest, db: Session = Depends(get_db)) -> object:
    try:
        trace = (
            trace_service.create_rewind_trace(db, outbreak_id, payload.review_window_days)
            if payload.direction.value == "rewind"
            else trace_service.create_fast_forward_trace(db, outbreak_id, payload.review_window_days)
        )
    except TraceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except TraceValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return serialize_trace(db, trace)


@router.get("/traces/{trace_run_id}", response_model=TraceRunResponse, tags=["traces"])
def get_trace(trace_run_id: int, db: Session = Depends(get_db)) -> object:
    trace = trace_repository.get_trace_run_with_findings(db, trace_run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace run not found")
    return serialize_trace(db, trace)


@router.get("/outbreaks/{outbreak_id}/traces", response_model=list[TraceRunResponse], tags=["traces"])
def list_outbreak_traces(outbreak_id: int, db: Session = Depends(get_db)) -> list[object]:
    if not repository.get_outbreak(db, outbreak_id):
        raise HTTPException(status_code=404, detail="Outbreak not found")
    return [serialize_trace(db, trace) for trace in trace_repository.list_outbreak_trace_runs(db, outbreak_id)]


def serialize_trace(db: Session, trace: TraceRun) -> TraceRunResponse:
    findings = sorted(trace.findings, key=lambda finding: (finding.event_timestamp, finding.id))
    location_ids = {int(finding.entity_id) for finding in findings if finding.entity_type in {"location", "market", "checkpost"}}
    locations = list(db.scalars(select(Location).where(Location.id.in_(location_ids)).order_by(Location.name))) if location_ids else []
    source_label = str(trace.parameters.get("source_label", "Configured synthetic demonstration review window — requires veterinary validation."))
    review_window_days = int(trace.parameters.get("review_window_days", 0))
    return TraceRunResponse(
        id=trace.id,
        outbreak=trace.outbreak,
        direction=trace.direction,
        window_start=trace.window_start,
        window_end=trace.window_end,
        review_window_days=review_window_days,
        source_label=source_label,
        findings=findings,
        timeline=findings,
        impacted_counts={
            "findings": len(findings),
            "locations": len(location_ids),
            "vehicles": len({finding.entity_id for finding in findings if finding.entity_type == "vehicle"}),
            "consignments": len({finding.entity_id for finding in findings if finding.entity_type == "consignment"}),
        },
        impacted_locations=locations,
        created_at=trace.created_at,
    )
