from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.seed import seed
from app.models import Advisory, MovementEvent, Outbreak, RouteAssessment
from app.db.session import SessionLocal

client=TestClient(app)
def setup_sources():
 seed(); fmd=next(x for x in client.get('/api/v1/outbreaks').json() if x['status']=='confirmed'); client.post(f"/api/v1/outbreaks/{fmd['id']}/traces",json={'direction':'rewind'}); client.post('/api/v1/sync/operations',json={'operations':[{'client_operation_id':'review-needs-review','operation_type':'create_consignment','payload':{'origin_location_id':999999}}]})
 return fmd
def test_review_case_generation_lifecycle_and_source_integrity():
 setup_sources(); cases=client.get('/api/v1/review-cases').json(); assert {x['category'] for x in cases}>={'evidence_gap','sync_exception','trace_contact'}; assert len(cases)==len(client.get('/api/v1/review-cases').json())
 item=cases[0]; assert client.patch(f"/api/v1/review-cases/{item['id']}",json={'status':'resolved'}).status_code==422
 with SessionLocal() as db: before=(list(db.scalars(select(Advisory.id))),list(db.scalars(select(MovementEvent.id))),list(db.scalars(select(RouteAssessment.id))),list(db.scalars(select(Outbreak.id))))
 resolved=client.patch(f"/api/v1/review-cases/{item['id']}",json={'status':'resolved','resolution_note':'Reviewed synthetic evidence.'}); assert resolved.status_code==200; assert resolved.json()['status']=='resolved'
 with SessionLocal() as db: after=(list(db.scalars(select(Advisory.id))),list(db.scalars(select(MovementEvent.id))),list(db.scalars(select(RouteAssessment.id))),list(db.scalars(select(Outbreak.id))))
 assert before==after
def test_reports_list_and_retrieve_persisted_trace_and_containment_sources():
    fmd = setup_sources()
    trace = client.post(f"/api/v1/outbreaks/{fmd['id']}/traces", json={"direction": "fast_forward"})
    scenario = client.post(f"/api/v1/outbreaks/{fmd['id']}/containment-scenarios", json={"horizon_days": 7, "selected_actions": ["checkpoint_screening"]})
    assert trace.status_code == 201, trace.text
    assert scenario.status_code == 201, scenario.text
    reports = client.get('/api/v1/reports')
    assert reports.status_code == 200
    body = reports.json()
    assert any(item["id"] == trace.json()["id"] for item in body["traces"])
    assert any(item["id"] == scenario.json()["id"] for item in body["containment"])
    assert client.get(f"/api/v1/reports/traces/{trace.json()['id']}").status_code == 200
    assert client.get(f"/api/v1/reports/containment/{scenario.json()['id']}").status_code == 200
    assert client.get('/api/v1/reports/traces/999999').status_code == 404
