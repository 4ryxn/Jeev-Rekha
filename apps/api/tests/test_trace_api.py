from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


client = TestClient(app)


def outbreaks() -> list[dict]:
    seed()
    response = client.get("/api/v1/outbreaks")
    assert response.status_code == 200
    return response.json()


def confirmed_fmd_id() -> int:
    return next(item["id"] for item in outbreaks() if item["disease_name"] == "Foot-and-mouth disease")


def test_create_and_retrieve_trace_api_response() -> None:
    outbreak_id = confirmed_fmd_id()
    created = client.post(f"/api/v1/outbreaks/{outbreak_id}/traces", json={"direction": "rewind"})
    assert created.status_code == 201
    body = created.json()
    assert body["outbreak"]["id"] == outbreak_id
    assert body["direction"] == "rewind"
    assert body["review_window_days"] == 14
    assert body["source_label"]
    assert body["timeline"] == body["findings"]
    assert body["impacted_counts"]["findings"] == len(body["findings"])
    assert body["disclaimer"] == "Trace results identify contacts for veterinary review; they do not confirm disease transmission."
    fetched = client.get(f"/api/v1/traces/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]
    listed = client.get(f"/api/v1/outbreaks/{outbreak_id}/traces")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == body["id"]


def test_trace_configuration_and_invalid_outbreak_status() -> None:
    records = outbreaks()
    confirmed = next(item for item in records if item["status"] == "confirmed")
    configuration = client.get(f"/api/v1/outbreaks/{confirmed['id']}/trace-configuration")
    assert configuration.status_code == 200
    assert configuration.json()["review_window_days"] == 14
    for status in ("suspected", "closed"):
        outbreak_id = next(item["id"] for item in records if item["status"] == status)
        response = client.post(f"/api/v1/outbreaks/{outbreak_id}/traces", json={"direction": "rewind"})
        assert response.status_code == 422
        assert "Only confirmed outbreaks" in response.json()["detail"]


def test_trace_api_rejects_invalid_direction_and_returns_useful_404s() -> None:
    outbreak_id = confirmed_fmd_id()
    assert client.post(f"/api/v1/outbreaks/{outbreak_id}/traces", json={"direction": "sideways"}).status_code == 422
    assert client.post("/api/v1/outbreaks/999999/traces", json={"direction": "rewind"}).status_code == 404
    assert client.get("/api/v1/traces/999999").status_code == 404
    assert client.get("/api/v1/outbreaks/999999/traces").status_code == 404
