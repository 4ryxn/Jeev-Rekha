from fastapi.testclient import TestClient
from sqlalchemy import func,select
from app.db.session import SessionLocal
from app.main import app
from app.models import Advisory, Consignment, Outbreak, RouteAssessment, TraceRun
from app.seed import seed

client=TestClient(app)
def locations(): seed();return {x["name"]:x["id"] for x in client.get("/api/v1/locations").json()}
def check(origin,destination,vaccination="verified",vehicle="PUBLIC-01"):
 return client.post("/api/v1/public/movement-check",json={"origin_location_id":origin,"destination_location_id":destination,"species":"Cattle","approximate_animal_count":8,"vehicle_reference":vehicle,"vaccination_evidence":vaccination})
def test_public_check_is_read_only_and_has_no_internal_fields():
 ids=locations()
 with SessionLocal() as db: before=[db.scalar(select(func.count(table.id))) for table in [Consignment,Outbreak,Advisory,RouteAssessment,TraceRun]]
 response=check(ids["Asha Nagar"],ids["Kaveri Cattle Market"]);assert response.status_code==200
 with SessionLocal() as db: after=[db.scalar(select(func.count(table.id))) for table in [Consignment,Outbreak,Advisory,RouteAssessment,TraceRun]]
 assert before==after
 body=response.json();assert body["risk_state"]=="green";assert {"risk_state","reasons","evidence_coverage_score","information_coverage","recommended_action","advisory_disclaimer","generated_at"}==set(body);assert not ({"id","consignment_id","trace_id","route_assessment_id","review_case_id","evidence_factors"}&set(body))
def test_public_check_demonstrates_all_states_and_validates_locations():
 ids=locations()
 assert check(ids["Asha Nagar"],ids["Kaveri Cattle Market"]).json()["risk_state"]=="green"
 assert check(ids["Navjeevan"],ids["Madhavpura"]).json()["risk_state"]=="amber"
 assert check(ids["Haritpur"],ids["Nandipur"]).json()["risk_state"]=="red"
 assert check(ids["Bhoomi Village"],ids["Navjeevan"]).json()["risk_state"]=="grey"
 assert check(ids["Asha Nagar"],ids["Asha Nagar"]).status_code==422
 assert check(999999,ids["Asha Nagar"]).status_code==404
