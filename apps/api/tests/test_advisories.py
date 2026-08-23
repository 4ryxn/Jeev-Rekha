from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


client = TestClient(app)


def seeded_advisories() -> list[dict]:
    seed()
    response = client.get("/api/v1/advisories")
    assert response.status_code == 200
    return response.json()


def test_seeded_examples_cover_all_four_advisory_states() -> None:
    advisories = seeded_advisories()
    by_route = {f"{item['consignment']['origin_location']['name']}->{item['consignment']['destination_location']['name']}": item for item in advisories}
    assert by_route["Asha Nagar->Kaveri Cattle Market"]["risk_state"] == "green"
    assert by_route["Navjeevan->Madhavpura"]["risk_state"] == "amber"
    assert by_route["Haritpur->Nandipur"]["risk_state"] == "red"
    assert by_route["Bhoomi Village->Navjeevan"]["risk_state"] == "grey"


def test_red_rule_precedence_over_declared_vaccination() -> None:
    seed()
    locations = {item["name"]: item["id"] for item in client.get("/api/v1/locations").json()}
    consignment = client.post("/api/v1/consignments", json={
        "origin_location_id": locations["Haritpur"], "destination_location_id": locations["Nandipur"], "species": "Cattle", "animal_count": 6,
        "vehicle_reference": "SYN-PRECEDENCE-01", "departure_at": datetime.now(UTC).isoformat(), "vaccination_evidence": "unknown",
    }).json()
    advisory = client.post("/api/v1/advisories/evaluate", json={"consignment_id": consignment["id"]})
    assert advisory.status_code == 201
    assert advisory.json()["risk_state"] == "red"
    assert advisory.json()["reasons"][0]["code"] == "confirmed_outbreak_exposure"


def test_coverage_score_factors_and_actions_are_explainable() -> None:
    advisories = seeded_advisories()
    green = next(item for item in advisories if item["risk_state"] == "green")
    grey = next(item for item in advisories if item["risk_state"] == "grey")
    assert green["evidence_coverage_score"] == 100
    assert [factor["score"] for factor in green["evidence_factors"]] == [25, 25, 25, 25]
    assert grey["evidence_coverage_score"] == 50
    assert "field verification" in grey["recommended_action"].lower()
    assert len(green["reasons"]) >= 2


def test_advisory_persistence_and_retrieval() -> None:
    advisories = seeded_advisories()
    advisory = advisories[0]
    fetched = client.get(f"/api/v1/advisories/{advisory['id']}")
    by_consignment = client.get(f"/api/v1/consignments/{advisory['consignment_id']}/advisories")
    assert fetched.status_code == 200
    assert fetched.json()["rules_version"] == "phase3-v1"
    assert by_consignment.status_code == 200
    assert any(item["id"] == advisory["id"] for item in by_consignment.json())
