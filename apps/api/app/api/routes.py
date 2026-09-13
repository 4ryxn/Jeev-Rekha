import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.core import LocationDataSource, LocationType
from app.repositories.core import OperationsRepository
from app.repositories.advisories import AdvisoryRepository
from app.schemas import AdvisoryEvaluateRequest, AdvisoryRead, ConsignmentCreate, ConsignmentRead, LocationCreate, LocationRead, LocationUpdate, OutbreakCreate, OutbreakRead, SyncBatchRequest, SyncOperationResult, TraceConfigurationRead, TraceCreateRequest, TraceRunResponse
from app.services.advisory import AdvisoryService
from app.services.operations import OperationsService
from app.services.routing import RouteService
from app.schemas.routes import RouteAssessRequest, RouteAssessmentRead
from app.models import RouteAssessment
from app.models import Location, SyncReceipt, TraceRun
from app.repositories.traces import TraceRepository
from app.core.trace_windows import get_trace_review_window
from app.services.tracing import TraceNotFoundError, TraceService, TraceValidationError
from app.services.containment import ContainmentService
from app.schemas import ContainmentCreate, ContainmentRead
from app.models import ContainmentScenario, ReviewCase, Advisory, TraceRun
from app.schemas import ReviewCasePatch, ReviewCaseRead, ReportIndexRead, SampleStatusUpdate
from app.schemas import PublicMovementCheckRequest, PublicMovementCheckResponse
from app.services.public_movement_check import PublicMovementCheckService
from app.services.reviews import ReviewService
from app.services.locations import LocationRegistryService
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1")
repository = OperationsRepository()
service = OperationsService(repository)
advisory_repository = AdvisoryRepository()
advisory_service = AdvisoryService(advisory_repository)
route_service=RouteService()
trace_repository = TraceRepository()
trace_service = TraceService(trace_repository)
containment_service=ContainmentService()
review_service=ReviewService()
public_movement_check_service=PublicMovementCheckService()
location_registry_service = LocationRegistryService()


@router.get("/locations", response_model=list[LocationRead], tags=["locations"])
def list_locations(
    type: LocationType | None = None,
    include_inactive: bool = False,
    source: LocationDataSource | None = None,
    db: Session = Depends(get_db),
) -> list[object]:
    return repository.list_locations(db, type, include_inactive, source)

@router.get("/routing/status", tags=["routing"])
def routing_status() -> dict[str, object]:
    configured = bool(get_settings().routing_provider_base_url)
    return {"configured": configured, "provider": "OSRM-compatible" if configured else None}


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED, tags=["locations"])
def create_location(payload: LocationCreate, db: Session = Depends(get_db)) -> object:
    return location_registry_service.create(db, payload)


@router.patch("/locations/{location_id}", response_model=LocationRead, tags=["locations"])
def update_location(location_id: int, payload: LocationUpdate, db: Session = Depends(get_db)) -> object:
    return location_registry_service.update(db, location_id, payload)


@router.post("/locations/{location_id}/archive", response_model=LocationRead, tags=["locations"])
def archive_location(location_id: int, db: Session = Depends(get_db)) -> object:
    return location_registry_service.archive(db, location_id)

@router.post("/public/movement-check",response_model=PublicMovementCheckResponse,tags=["public"])
def public_movement_check(payload:PublicMovementCheckRequest,db:Session=Depends(get_db)):
 return public_movement_check_service.check(db,payload.origin_location_id,payload.destination_location_id,payload.species,payload.approximate_animal_count,payload.vehicle_reference,payload.vaccination_evidence)


@router.get("/outbreaks", response_model=list[OutbreakRead], tags=["outbreaks"])
def list_outbreaks(source: LocationDataSource | None = None, db: Session = Depends(get_db)) -> list[object]:
    return repository.list_outbreaks(db, source)


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
def list_consignments(source: LocationDataSource | None = None, db: Session = Depends(get_db)) -> list[object]:
    return repository.list_consignments(db, source)


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
def list_advisories(source: LocationDataSource | None = None, db: Session = Depends(get_db)) -> list[object]:
    return advisory_repository.list_recent_advisories(db, source)


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


@router.get("/traces", response_model=list[TraceRunResponse], tags=["traces"])
def list_traces(source: LocationDataSource | None = None, db: Session = Depends(get_db)) -> list[object]:
    return [serialize_trace(db, trace) for trace in trace_repository.list_trace_runs(db, source)]


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
        data_source=trace.outbreak.data_source,
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


@router.post("/sync/operations", response_model=list[SyncOperationResult], tags=["sync"])
def sync_operations(payload: SyncBatchRequest, db: Session = Depends(get_db)) -> list[SyncOperationResult]:
    results: list[SyncOperationResult] = []
    for operation in payload.operations:
        existing = db.scalar(select(SyncReceipt).where(SyncReceipt.client_operation_id == operation.client_operation_id))
        if existing:
            results.append(SyncOperationResult(client_operation_id=existing.client_operation_id, operation_type=existing.operation_type, status=existing.status, entity_type=existing.entity_type, entity_id=existing.entity_id, received_at=existing.received_at))
            continue
        digest = hashlib.sha256(json.dumps(operation.payload, sort_keys=True, default=str).encode()).hexdigest()
        try:
            entity = service.create_consignment(db, ConsignmentCreate.model_validate(operation.payload)) if operation.operation_type == "create_consignment" else service.create_outbreak(db, OutbreakCreate.model_validate(operation.payload))
            receipt = SyncReceipt(client_operation_id=operation.client_operation_id, operation_type=operation.operation_type, status="synced", entity_type="consignment" if operation.operation_type == "create_consignment" else "outbreak", entity_id=entity.id, payload_hash=digest, data_source=entity.data_source)
            db.add(receipt); db.commit(); db.refresh(receipt)
            results.append(SyncOperationResult(client_operation_id=receipt.client_operation_id, operation_type=receipt.operation_type, status="synced", entity_type=receipt.entity_type, entity_id=receipt.entity_id, received_at=receipt.received_at))
        except (ValidationError, HTTPException, ValueError) as error:
            detail = error.detail if isinstance(error, HTTPException) else str(error)
            submitted_source = operation.payload.get("data_source")
            receipt = SyncReceipt(client_operation_id=operation.client_operation_id, operation_type=operation.operation_type, status="needs_review", entity_type=None, entity_id=None, payload_hash=digest, data_source=submitted_source if submitted_source in {"demo_seed", "pilot_entered"} else None)
            db.add(receipt); db.commit(); db.refresh(receipt)
            results.append(SyncOperationResult(client_operation_id=operation.client_operation_id, operation_type=operation.operation_type, status="needs_review", received_at=receipt.received_at, error=str(detail)))
    return results

@router.post("/outbreaks/{outbreak_id}/containment-scenarios",response_model=ContainmentRead,status_code=201)
def create_containment(outbreak_id:int,payload:ContainmentCreate,db:Session=Depends(get_db)):
 return containment_service.create(db,outbreak_id,payload.horizon_days,payload.selected_actions)
@router.get("/containment-scenarios/{scenario_id}",response_model=ContainmentRead)
def get_containment(scenario_id:int,db:Session=Depends(get_db)):
 item=containment_service.get(db,scenario_id)
 if not item: raise HTTPException(404,"Containment scenario not found")
 return item
@router.get("/outbreaks/{outbreak_id}/containment-scenarios",response_model=list[ContainmentRead])
def list_containment(outbreak_id:int,db:Session=Depends(get_db)):
 if not repository.get_outbreak(db,outbreak_id): raise HTTPException(404,"Outbreak not found")
 return containment_service.list(db,outbreak_id)

@router.get("/containment-scenarios", response_model=list[ContainmentRead])
def list_all_containment(source: LocationDataSource | None = None, db: Session = Depends(get_db)):
 items = list(db.scalars(select(ContainmentScenario).order_by(ContainmentScenario.created_at.desc())))
 return [item for item in items if source is None or item.outbreak.data_source == source]

def serialize_review(item:ReviewCase, db: Session):
 return {**{key:getattr(item,key) for key in ("id","source_type","source_id","category","case_type","sample_status","priority","title","summary","status","resolution_note","created_at","acknowledged_at","resolved_at")},**review_service.source_meta(item, db)}
@router.get("/review-cases",response_model=list[ReviewCaseRead],tags=["review-cases"])
def list_review_cases(status_filter:str|None=Query(None,alias="status"),category:str|None=None,source: LocationDataSource | None = None,db:Session=Depends(get_db)):
 return [serialize_review(item, db) for item in review_service.list(db,status_filter,category,source)]
@router.get("/review-cases/{case_id}",response_model=ReviewCaseRead,tags=["review-cases"])
def get_review_case(case_id:int,db:Session=Depends(get_db)):
 item=review_service.get(db,case_id)
 if not item: raise HTTPException(404,"Review case not found")
 return serialize_review(item, db)
@router.post("/outbreaks/{outbreak_id}/lab-referrals",response_model=ReviewCaseRead,status_code=status.HTTP_201_CREATED,tags=["review-cases"])
def create_lab_referral(outbreak_id:int,db:Session=Depends(get_db)):
 item=review_service.create_lab_referral(db,outbreak_id)
 if not item: raise HTTPException(404,"Outbreak not found")
 return serialize_review(item,db)
@router.patch("/review-cases/{case_id}",response_model=ReviewCaseRead,tags=["review-cases"])
def update_review_case(case_id:int,payload:ReviewCasePatch,db:Session=Depends(get_db)):
 item=review_service.get(db,case_id)
 if not item: raise HTTPException(404,"Review case not found")
 try:return serialize_review(review_service.update(db,item,payload.status,payload.resolution_note or ""), db)
 except ValueError as error:raise HTTPException(422,str(error)) from error
@router.patch("/review-cases/{case_id}/sample-status",response_model=ReviewCaseRead,tags=["review-cases"])
def update_review_case_sample_status(case_id:int,payload:SampleStatusUpdate,db:Session=Depends(get_db)):
 item=review_service.get(db,case_id)
 if not item: raise HTTPException(404,"Review case not found")
 try:return serialize_review(review_service.update_sample_status(db,item,payload.sample_status),db)
 except ValueError as error:raise HTTPException(422,str(error)) from error

@router.get("/reports",response_model=ReportIndexRead,tags=["reports"])
def list_reports(source: LocationDataSource | None = None, db:Session=Depends(get_db)):
 traces=trace_repository.list_trace_runs(db, source)[:12]
 scenarios=[item for item in db.scalars(select(ContainmentScenario).order_by(ContainmentScenario.created_at.desc()).limit(12)) if source is None or item.outbreak.data_source == source]
 lab_referrals=[item for item in review_service.list(db,category="lab_referral",source=source)[:12]]
 return {"advisories":[{"id":x.id,"href":f"/reports/advisories/{x.id}","title":f"{x.risk_state.value.title()} movement advisory","data_source":x.data_source} for x in advisory_repository.list_recent_advisories(db, source)],"traces":[{"id":x.id,"href":f"/reports/traces/{x.id}","title":f"{x.direction.replace('_',' ').title()} trace contact review","data_source":x.outbreak.data_source} for x in traces],"containment":[{"id":x.id,"href":f"/containment-scenarios/{x.id}/print","title":"Containment action brief","data_source":x.outbreak.data_source} for x in scenarios],"lab_referrals":[{"id":x.id,"href":f"/reports/lab-referrals/{x.id}","title":x.title,"data_source":review_service.source_data_source(x,db)} for x in lab_referrals]}
@router.get("/reports/{kind}/{source_id}",tags=["reports"])
def get_report_source(kind:str,source_id:int,db:Session=Depends(get_db)):
 if kind=="advisories": item=advisory_repository.get_advisory(db,source_id)
 elif kind=="traces": item=trace_repository.get_trace_run_with_findings(db,source_id)
 elif kind=="containment": item=containment_service.get(db,source_id)
 elif kind=="lab-referrals": item=db.scalar(select(ReviewCase).where(ReviewCase.id==source_id,ReviewCase.case_type=="lab_referral"))
 else: raise HTTPException(404,"Report source not found")
 if not item: raise HTTPException(404,"Report source not found")
 if kind=="traces": return serialize_trace(db,item)
 if kind=="advisories": return AdvisoryRead.model_validate(item).model_dump(mode="json")
 if kind=="lab-referrals": return serialize_review(item,db)
 return ContainmentRead.model_validate(item).model_dump(mode="json")
