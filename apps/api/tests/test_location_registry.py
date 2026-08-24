from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


client = TestClient(app)


def pilot_payload(name: str = "Pilot Meadow") -> dict[str, object]:
    return {
        "name": name,
        "location_type": "village",
        "district": "Pilot District",
        "state": "Pilot State",
        "latitude": 12.9716,
        "longitude": 77.5946,
    }


def test_create_update_and_filter_pilot_location() -> None:
    seed()
    created = client.post("/api/v1/locations", json=pilot_payload())
    assert created.status_code == 201
    body = created.json()
    assert body["data_source"] == "pilot_entered"
    assert body["is_active"] is True
    assert body["location_type"] == "village"

    updated = client.patch(f"/api/v1/locations/{body['id']}", json={"district": "Updated District", "location_type": "livestock_market"})
    assert updated.status_code == 200
    assert updated.json()["district"] == "Updated District"
    assert updated.json()["type"] == "market"
    assert updated.json()["location_type"] == "livestock_market"

    listed = client.get("/api/v1/locations?source=pilot_entered")
    assert listed.status_code == 200
    assert [location["id"] for location in listed.json()] == [body["id"]]
    assert client.get("/api/v1/locations?source=demo_seed").json()


def test_duplicate_active_location_is_rejected() -> None:
    seed()
    assert client.post("/api/v1/locations", json=pilot_payload()).status_code == 201
    duplicate = client.post("/api/v1/locations", json={**pilot_payload(" pilot meadow "), "district": "pilot district", "state": "PILOT STATE"})
    assert duplicate.status_code == 409
    assert "same name, district, and state" in duplicate.json()["detail"]


def test_archive_unused_location_and_include_inactive_filter() -> None:
    seed()
    created = client.post("/api/v1/locations", json=pilot_payload()).json()
    archived = client.post(f"/api/v1/locations/{created['id']}/archive")
    assert archived.status_code == 200
    assert archived.json()["is_active"] is False
    assert created["id"] not in {location["id"] for location in client.get("/api/v1/locations").json()}
    assert created["id"] in {location["id"] for location in client.get("/api/v1/locations?include_inactive=true").json()}


def test_referenced_pilot_location_cannot_be_archived() -> None:
    seed()
    created = client.post("/api/v1/locations", json=pilot_payload()).json()
    origin = client.post("/api/v1/locations", json=pilot_payload("Pilot Origin")).json()
    consignment = client.post("/api/v1/consignments", json={
        "origin_location_id": origin["id"],
        "destination_location_id": created["id"],
        "species": "Cattle",
        "animal_count": 3,
        "vehicle_reference": "PILOT-REF-001",
        "departure_at": datetime.now(UTC).isoformat(),
        "vaccination_evidence": "verified",
        "data_source": "pilot_entered",
    })
    assert consignment.status_code == 201
    archive = client.post(f"/api/v1/locations/{created['id']}/archive")
    assert archive.status_code == 409
    assert "cannot be archived because it is referenced" in archive.json()["detail"]


def test_demo_seed_locations_are_read_only() -> None:
    seed()
    demo = client.get("/api/v1/locations?source=demo_seed").json()[0]
    assert client.patch(f"/api/v1/locations/{demo['id']}", json={"district": "Changed"}).status_code == 403
    assert client.post(f"/api/v1/locations/{demo['id']}/archive").status_code == 403
