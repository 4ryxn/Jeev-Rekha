from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models import Consignment, Outbreak
from app.seed import seed


client = TestClient(app)


def pilot_location(name: str) -> int:
    response = client.post("/api/v1/locations", json={"name": name, "location_type": "village", "district": "Pilot District", "state": "Pilot State", "latitude": 18.0 if name.endswith("A") else 18.1, "longitude": 78.0 if name.endswith("A") else 78.1})
    assert response.status_code == 201
    return response.json()["id"]


def test_seed_roots_are_demo_and_primary_filters_are_source_aware() -> None:
    seed()
    assert {item["data_source"] for item in client.get("/api/v1/outbreaks?source=demo_seed").json()} == {"demo_seed"}
    assert {item["data_source"] for item in client.get("/api/v1/consignments?source=demo_seed").json()} == {"demo_seed"}
    assert client.get("/api/v1/outbreaks?source=pilot_entered").json() == []


def test_pilot_and_demo_records_cannot_mix_location_contexts() -> None:
    seed()
    demo_location = client.get("/api/v1/locations?source=demo_seed").json()[0]["id"]
    pilot_a, pilot_b = pilot_location("Pilot A"), pilot_location("Pilot B")
    invalid_pilot = client.post("/api/v1/outbreaks", json={"disease_name": "Pilot test", "species": "Cattle", "status": "suspected", "location_id": demo_location, "data_source": "pilot_entered", "detected_at": datetime.now(UTC).isoformat(), "verification_level": "reported"})
    assert invalid_pilot.status_code == 422
    invalid_demo = client.post("/api/v1/consignments", json={"origin_location_id": pilot_a, "destination_location_id": pilot_b, "data_source": "demo_seed", "species": "Cattle", "animal_count": 2, "vehicle_reference": "CTX-001", "departure_at": datetime.now(UTC).isoformat(), "vaccination_evidence": "verified"})
    assert invalid_demo.status_code == 422
    created = client.post("/api/v1/consignments", json={"origin_location_id": pilot_a, "destination_location_id": pilot_b, "data_source": "pilot_entered", "species": "Cattle", "animal_count": 2, "vehicle_reference": "CTX-002", "departure_at": datetime.now(UTC).isoformat(), "vaccination_evidence": "verified"})
    assert created.status_code == 201 and created.json()["data_source"] == "pilot_entered"


def test_sync_preserves_submitted_data_context_without_reclassification() -> None:
    seed(); pilot_a, pilot_b = pilot_location("Sync A"), pilot_location("Sync B")
    operation = {"client_operation_id": f"pilot-context-sync-{uuid4()}", "operation_type": "create_consignment", "payload": {"origin_location_id": pilot_a, "destination_location_id": pilot_b, "data_source": "pilot_entered", "species": "Goat", "animal_count": 4, "vehicle_reference": "CTX-SYNC", "departure_at": datetime.now(UTC).isoformat(), "vaccination_evidence": "declared"}}
    result = client.post("/api/v1/sync/operations", json={"operations": [operation]})
    assert result.status_code == 200 and result.json()[0]["status"] == "synced"
    repeated = client.post("/api/v1/sync/operations", json={"operations": [operation]})
    assert repeated.json()[0]["entity_id"] == result.json()[0]["entity_id"]
    with SessionLocal() as db:
        item = db.scalar(select(Consignment).where(Consignment.id == result.json()[0]["entity_id"]))
        assert item is not None and item.data_source.value == "pilot_entered"


def test_derived_lists_inherit_and_filter_root_data_source() -> None:
    seed()
    fmd = next(item for item in client.get("/api/v1/outbreaks?source=demo_seed").json() if item["status"] == "confirmed")
    trace = client.post(f"/api/v1/outbreaks/{fmd['id']}/traces", json={"direction": "rewind"})
    scenario = client.post(f"/api/v1/outbreaks/{fmd['id']}/containment-scenarios", json={"horizon_days": 7, "selected_actions": ["checkpoint_screening"]})
    assert trace.status_code == 201 and trace.json()["data_source"] == "demo_seed"
    assert scenario.status_code == 201 and scenario.json()["data_source"] == "demo_seed"
    assert all(item["data_source"] == "demo_seed" for item in client.get("/api/v1/advisories?source=demo_seed").json())
    assert client.get("/api/v1/traces?source=pilot_entered").json() == []
    assert client.get("/api/v1/containment-scenarios?source=pilot_entered").json() == []
