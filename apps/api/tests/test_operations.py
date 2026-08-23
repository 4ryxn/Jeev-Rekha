from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


client = TestClient(app)


def test_seed_data_success() -> None:
    message = seed()
    assert "Synthetic" in message
    locations = client.get("/api/v1/locations")
    assert locations.status_code == 200
    assert len(locations.json()) == 13
    assert len(client.get("/api/v1/outbreaks").json()) == 3
    assert len(client.get("/api/v1/consignments").json()) == 7


def test_create_and_retrieve_outbreak() -> None:
    seed()
    location_id = client.get("/api/v1/locations?type=village").json()[0]["id"]
    payload = {
        "disease_name": "Synthetic test disease",
        "species": "Cattle",
        "status": "suspected",
        "location_id": location_id,
        "detected_at": datetime.now(UTC).isoformat(),
        "suspected_cases": 4,
        "confirmed_cases": 0,
        "mortality_count": 0,
        "verification_level": "reported",
        "notes": "Synthetic test only",
    }
    created = client.post("/api/v1/outbreaks", json=payload)
    assert created.status_code == 201
    fetched = client.get(f"/api/v1/outbreaks/{created.json()['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["disease_name"] == "Synthetic test disease"


def test_create_and_retrieve_consignment() -> None:
    seed()
    locations = client.get("/api/v1/locations?type=village").json()
    payload = {
        "origin_location_id": locations[0]["id"],
        "destination_location_id": locations[1]["id"],
        "species": "Goat",
        "animal_count": 23,
        "vehicle_reference": "SYN-TEST-88",
        "departure_at": datetime.now(UTC).isoformat(),
        "vaccination_evidence": "declared",
    }
    created = client.post("/api/v1/consignments", json=payload)
    assert created.status_code == 201
    assert created.json()["movement_events"][0]["event_type"] == "departure"
    fetched = client.get(f"/api/v1/consignments/{created.json()['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["vehicle"]["vehicle_reference"] == "SYN-TEST-88"


def test_invalid_enum_and_form_input_are_rejected() -> None:
    seed()
    invalid_outbreak = client.post("/api/v1/outbreaks", json={"status": "danger"})
    assert invalid_outbreak.status_code == 422
    invalid_consignment = client.post("/api/v1/consignments", json={
        "origin_location_id": 1,
        "destination_location_id": 1,
        "species": "Cow",
        "animal_count": 0,
        "vehicle_reference": "X",
        "departure_at": datetime.now(UTC).isoformat(),
        "vaccination_evidence": "certain",
    })
    assert invalid_consignment.status_code == 422
