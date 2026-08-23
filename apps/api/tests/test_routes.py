from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed

client = TestClient(app)


def routes() -> dict[str, int]:
    seed()
    return {f"{item['origin_location']['name']}->{item['destination_location']['name']}": item["id"] for item in client.get("/api/v1/consignments").json()}


def test_shortest_requested_route_and_safer_alternative() -> None:
    result = client.post("/api/v1/routes/assess", json={"consignment_id": routes()["Sundargram->Sampoorna Livestock Market"]})
    assert result.status_code == 201
    body = result.json()
    assert body["preferred_distance_km"] == 9.0
    assert body["safer_distance_km"] == 10.0
    assert body["risk_reduction"] == "Reduced"
    assert body["preferred_route"]["location_ids"] != body["safer_route"]["location_ids"]


def test_direct_outbreak_has_no_safer_route() -> None:
    result = client.post("/api/v1/routes/assess", json={"consignment_id": routes()["Haritpur->Nandipur"]})
    assert result.status_code == 201
    body = result.json()
    assert body["safer_route"] is None
    assert body["risk_reduction"] == "Unchanged"
    assert any("directly affected" in reason for reason in body["route_reasons"])


def test_route_assessment_persistence_and_invalid_consignment() -> None:
    consignment_id = routes()["Sundargram->Sampoorna Livestock Market"]
    created = client.post("/api/v1/routes/assess", json={"consignment_id": consignment_id}).json()
    assert client.get(f"/api/v1/routes/assessments/{created['id']}").status_code == 200
    assert client.get(f"/api/v1/consignments/{consignment_id}/route-assessments").json()[0]["id"] == created["id"]
    assert client.post("/api/v1/routes/assess", json={"consignment_id": 999999}).status_code == 404
