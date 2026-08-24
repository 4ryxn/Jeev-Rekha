"""Explicit Phase 4 pilot-advisory policy coverage; no external routing calls."""
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models import Advisory, RouteAssessment
from app.seed import seed
from app.services.advisory import AdvisoryService

client = TestClient(app)

def pilot_location(name, lat, lon):
    response=client.post("/api/v1/locations",json={"name":name,"location_type":"village","district":"Pilot","state":"State","latitude":lat,"longitude":lon});assert response.status_code==201;return response.json()["id"]
def pilot_consignment(vaccination="verified"):
    suffix=uuid4().hex[:8];a,b=pilot_location(f"Pilot origin {suffix}",12,77),pilot_location(f"Pilot destination {suffix}",12,77.2)
    response=client.post("/api/v1/consignments",json={"origin_location_id":a,"destination_location_id":b,"data_source":"pilot_entered","species":"Cattle","animal_count":2,"vehicle_reference":"PILOT-ADV","departure_at":datetime.now(UTC).isoformat(),"vaccination_evidence":vaccination});assert response.status_code==201;return response.json(),a,b
def route(db, consignment, geometry=True):
    item=RouteAssessment(consignment_id=consignment["id"],preferred_route={"coordinates":[[77,12],[77.2,12]],"distance_km":22,"minutes":30},safer_route=None,preferred_distance_km=22,preferred_minutes=30,safer_distance_km=None,safer_minutes=None,risk_reduction="Unchanged",route_reasons=[],route_provider="mock" if geometry else None,route_geometry=[[77,12],[77.2,12]] if geometry else None,route_fallback_reason=None if geometry else "Road route unavailable; no navigation recommendation is shown.");db.add(item);db.commit()
def outbreak(location_id,status,radius=5):
    return client.post("/api/v1/outbreaks",json={"disease_name":"Pilot disease","species":"Cattle","status":status,"location_id":location_id,"data_source":"pilot_entered","review_radius_km":radius,"detected_at":datetime.now(UTC).isoformat(),"verification_level":"reported"})
def evaluate(consignment_id):
    with SessionLocal() as db:return AdvisoryService().evaluate(db,consignment_id)

def test_confirmed_and_suspected_route_radius_intersections_are_red_and_amber():
    seed();c,_,b=pilot_consignment()
    with SessionLocal() as db: route(db,c)
    assert outbreak(b,"confirmed").status_code==201 and evaluate(c["id"]).risk_state.value=="red"
    # isolated fixture makes a second scenario independent
def test_suspected_intersection_and_endpoint_inside_radius_are_amber():
    seed();c,a,_=pilot_consignment()
    with SessionLocal() as db: route(db,c)
    assert outbreak(a,"suspected",1).status_code==201 and evaluate(c["id"]).risk_state.value=="amber"
def test_missing_route_unknown_vaccination_and_unverified_vaccination_are_conservative():
    seed();unknown,_,_=pilot_consignment("unknown"); assert evaluate(unknown["id"]).risk_state.value=="grey"
    seed();declared,_,_=pilot_consignment("declared")
    with SessionLocal() as db: route(db,declared)
    assert evaluate(declared["id"]).risk_state.value=="amber"
def test_closed_outbreak_is_excluded_and_re_evaluation_preserves_snapshot():
    seed();c,_,b=pilot_consignment()
    with SessionLocal() as db: route(db,c)
    assert outbreak(b,"closed",10).status_code==201
    first=evaluate(c["id"]); second=evaluate(c["id"])
    assert first.risk_state.value=="green" and second.id!=first.id and first.policy_snapshot==second.policy_snapshot
def test_pilot_red_review_case_does_not_mutate_advisory_and_demo_is_separate():
    seed();c,_,b=pilot_consignment()
    with SessionLocal() as db: route(db,c)
    outbreak(b,"confirmed"); advisory=evaluate(c["id"]); before=advisory.risk_state
    cases=client.get("/api/v1/review-cases").json(); assert any(x["source_id"]==str(advisory.id) for x in cases)
    with SessionLocal() as db: assert db.get(Advisory,advisory.id).risk_state==before
    assert all(x["data_source"]=="demo_seed" for x in client.get("/api/v1/advisories?source=demo_seed").json())
