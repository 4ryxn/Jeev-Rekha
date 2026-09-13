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


def test_create_lab_referral_from_outbreak_and_filter_review_queue():
    outbreak = setup_sources()
    created = client.post(f"/api/v1/outbreaks/{outbreak['id']}/lab-referrals")
    assert created.status_code == 201, created.text
    referral = created.json()
    assert referral["source_type"] == "outbreak"
    assert referral["source_id"] == str(outbreak["id"])
    assert referral["case_type"] == "lab_referral"
    assert referral["category"] == "lab_referral"
    assert referral["sample_status"] == "none"
    filtered = client.get("/api/v1/review-cases?category=lab_referral")
    assert filtered.status_code == 200
    assert [item["id"] for item in filtered.json()] == [referral["id"]]


def test_lab_referral_sample_lifecycle_and_resolution_note_preserve_outbreak():
    outbreak = setup_sources()
    referral = client.post(f"/api/v1/outbreaks/{outbreak['id']}/lab-referrals").json()
    with SessionLocal() as db:
        before = db.get(Outbreak, outbreak["id"])
        source_evidence = (before.disease_name, before.status, before.notes, before.verification_level)
    for sample_status in ("collected", "sent_to_lab", "result_received"):
        updated = client.patch(f"/api/v1/review-cases/{referral['id']}/sample-status", json={"sample_status": sample_status})
        assert updated.status_code == 200, updated.text
        assert updated.json()["sample_status"] == sample_status
    resolved = client.patch(f"/api/v1/review-cases/{referral['id']}", json={"status": "resolved", "resolution_note": "PCR result received: negative."})
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["resolution_note"] == "PCR result received: negative."
    with SessionLocal() as db:
        after = db.get(Outbreak, outbreak["id"])
        assert (after.disease_name, after.status, after.notes, after.verification_level) == source_evidence


def test_lab_referral_can_resolve_without_result_note_and_reports_include_it():
    outbreak = setup_sources()
    referral = client.post(f"/api/v1/outbreaks/{outbreak['id']}/lab-referrals").json()
    resolved = client.patch(f"/api/v1/review-cases/{referral['id']}", json={"status": "resolved"})
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["resolution_note"] is None
    reports = client.get("/api/v1/reports")
    assert any(item["id"] == referral["id"] for item in reports.json()["lab_referrals"])
    assert client.get(f"/api/v1/reports/lab-referrals/{referral['id']}").status_code == 200
