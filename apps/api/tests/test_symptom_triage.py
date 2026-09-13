from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.triage_rules import HIGH_CONCERN_PROFILES
from app.main import app
from app.models import ReviewCase
from app.db.session import SessionLocal
from app.seed import seed


client = TestClient(app)


def payload(*, symptoms: list[str], mortality_count: int = 0, reporter_type: str = "farmer") -> dict[str, object]:
    seed()
    location = client.get("/api/v1/locations?source=demo_seed").json()[0]
    return {
        "disease_name": "Symptom and mortality report", "species": "Cattle", "status": "suspected",
        "location_id": location["id"], "data_source": "demo_seed", "detected_at": datetime.now(UTC).isoformat(),
        "suspected_cases": 20, "confirmed_cases": 0, "mortality_count": mortality_count,
        "verification_level": "reported", "symptoms": symptoms, "days_since_onset": 2,
        "reporter_type": reporter_type, "animals_affected": 20,
    }


@pytest.mark.parametrize("profile", HIGH_CONCERN_PROFILES, ids=lambda p: p.disease_name)
def test_each_high_concern_symptom_profile_creates_veterinary_review(profile):
    response = client.post("/api/v1/outbreaks", json=payload(symptoms=sorted(profile.symptoms)))
    assert response.status_code == 201, response.text
    assert response.json()["disease_name"] == profile.disease_name
    assert response.json()["source"] == "farmer_reported"
    with SessionLocal() as db:
        case = db.scalar(select(ReviewCase).where(ReviewCase.source_type == "outbreak", ReviewCase.source_id == str(response.json()["id"])))
        assert case and case.priority == profile.priority and "Requires veterinary review" in case.summary


def test_online_submission_veterinary_source_and_mortality_threshold_trigger():
    response = client.post("/api/v1/outbreaks", json=payload(symptoms=["fever"], mortality_count=3, reporter_type="veterinary_officer"))
    assert response.status_code == 201, response.text
    assert response.json()["source"] == "vet_observed"
    with SessionLocal() as db:
        assert db.scalar(select(ReviewCase).where(ReviewCase.source_type == "outbreak", ReviewCase.source_id == str(response.json()["id"])))


def test_no_trigger_case_creates_no_review_case():
    response = client.post("/api/v1/outbreaks", json=payload(symptoms=["fever"], mortality_count=2))
    assert response.status_code == 201, response.text
    with SessionLocal() as db:
        assert db.scalar(select(ReviewCase).where(ReviewCase.source_type == "outbreak", ReviewCase.source_id == str(response.json()["id"]))) is None


def test_offline_queue_sync_operation_is_idempotent():
    operation = {"client_operation_id": f"symptom-offline-{uuid4()}", "operation_type": "create_outbreak", "payload": payload(symptoms=["fever"], mortality_count=3)}
    first = client.post("/api/v1/sync/operations", json={"operations": [operation]})
    retry = client.post("/api/v1/sync/operations", json={"operations": [operation]})
    assert first.status_code == retry.status_code == 200
    assert first.json()[0]["status"] == retry.json()[0]["status"] == "synced"
    assert first.json()[0]["entity_id"] == retry.json()[0]["entity_id"]
