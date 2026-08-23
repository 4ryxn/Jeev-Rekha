from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.main import app
from app.models import Advisory, MovementEvent, Outbreak, RouteAssessment, RouteSegment
from app.seed import seed


client = TestClient(app)
DEMO_ACTIONS = ["checkpoint_screening", "market_notification"]


def confirmed_fmd() -> dict:
    seed()
    outbreaks = client.get("/api/v1/outbreaks").json()
    return next(item for item in outbreaks if item["disease_name"] == "Foot-and-mouth disease" and item["status"] == "confirmed")


def run_scenario(outbreak_id: int, actions: list[str] = DEMO_ACTIONS) -> dict:
    response = client.post(
        f"/api/v1/outbreaks/{outbreak_id}/containment-scenarios",
        json={"horizon_days": 7, "selected_actions": actions},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_seeded_fmd_scenario_has_auditable_bounded_effect() -> None:
    outbreak = confirmed_fmd()
    first = run_scenario(outbreak["id"])
    second = run_scenario(outbreak["id"])

    baseline = first["baseline_summary"]
    scenario = first["scenario_summary"]
    effects = scenario["action_effects"]
    assert baseline["route_checkpoint_contacts"] > 0
    assert baseline["market_contacts"] > 0
    assert effects["checkpoint_screening"] == {
        "category": "route/checkpoint contacts",
        "applicable_workload": baseline["route_checkpoint_contacts"],
        "reduction": 1,
    }
    assert effects["market_notification"] == {
        "category": "market contacts",
        "applicable_workload": baseline["market_contacts"],
        "reduction": 1,
    }
    assert scenario["estimated_review_contacts"] == baseline["estimated_review_contacts"] - 2
    assert 0 <= scenario["estimated_review_contacts"] <= baseline["estimated_review_contacts"]
    assert first["baseline_summary"] == second["baseline_summary"]
    assert first["scenario_summary"] == second["scenario_summary"]


def test_zero_applicable_categories_have_no_reduction() -> None:
    seed()
    location = client.get("/api/v1/locations").json()[0]
    reference = datetime.now(UTC) + timedelta(days=60)
    outbreak_response = client.post(
        "/api/v1/outbreaks",
        json={
            "disease_name": "Synthetic isolated demonstration",
            "species": "Cattle",
            "status": "confirmed",
            "location_id": location["id"],
            "detected_at": reference.isoformat(),
            "confirmed_at": reference.isoformat(),
            "verification_level": "laboratory_confirmed",
        },
    )
    assert outbreak_response.status_code == 201, outbreak_response.text
    scenario = run_scenario(outbreak_response.json()["id"], ["checkpoint_screening", "market_notification", "route_avoidance_advisory"])
    summary = scenario["scenario_summary"]
    assert scenario["baseline_summary"]["estimated_review_contacts"] == 0
    assert summary["estimated_review_contacts"] == 0
    assert all(effect["reduction"] == 0 for effect in summary["action_effects"].values())
    assert "No applicable recorded route/checkpoint workload in this scenario." in scenario["assumptions"]
    assert "No applicable recorded market workload in this scenario." in scenario["assumptions"]
    assert "No applicable recorded route-risk exposure workload in this scenario." in scenario["assumptions"]


def test_scenario_does_not_modify_operational_records() -> None:
    outbreak = confirmed_fmd()
    with SessionLocal() as db:
        before = {
            "advisories": list(db.scalars(select(Advisory.id).order_by(Advisory.id))),
            "assessments": list(db.scalars(select(RouteAssessment.id).order_by(RouteAssessment.id))),
            "segments": list(db.scalars(select(RouteSegment.id).order_by(RouteSegment.id))),
            "outbreak": db.scalar(select(Outbreak).where(Outbreak.id == outbreak["id"])).status.value,
            "movements": [tuple(row) for row in db.execute(select(MovementEvent.id, MovementEvent.consignment_id, MovementEvent.location_id, MovementEvent.occurred_at).order_by(MovementEvent.id))],
        }
    run_scenario(outbreak["id"])
    with SessionLocal() as db:
        after = {
            "advisories": list(db.scalars(select(Advisory.id).order_by(Advisory.id))),
            "assessments": list(db.scalars(select(RouteAssessment.id).order_by(RouteAssessment.id))),
            "segments": list(db.scalars(select(RouteSegment.id).order_by(RouteSegment.id))),
            "outbreak": db.scalar(select(Outbreak).where(Outbreak.id == outbreak["id"])).status.value,
            "movements": [tuple(row) for row in db.execute(select(MovementEvent.id, MovementEvent.consignment_id, MovementEvent.location_id, MovementEvent.occurred_at).order_by(MovementEvent.id))],
        }
    assert after == before


def test_containment_rejects_invalid_outbreak_status_and_payload() -> None:
    outbreak = confirmed_fmd()
    suspected = next(item for item in client.get("/api/v1/outbreaks").json() if item["status"] == "suspected")
    assert client.post(f"/api/v1/outbreaks/{suspected['id']}/containment-scenarios", json={"horizon_days": 7, "selected_actions": DEMO_ACTIONS}).status_code == 422
    assert client.post(f"/api/v1/outbreaks/{outbreak['id']}/containment-scenarios", json={"horizon_days": 9, "selected_actions": ["bad"]}).status_code == 422
