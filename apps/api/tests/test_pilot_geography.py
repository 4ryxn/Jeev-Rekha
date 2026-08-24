from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed
from app.services.road_routing import RoadRoute
from app.services.routing import RouteService
from app.db.session import SessionLocal

client = TestClient(app)

def location(name: str, latitude: float, longitude: float) -> int:
    response = client.post("/api/v1/locations", json={"name": name, "location_type": "village", "district": "Pilot", "state": "State", "latitude": latitude, "longitude": longitude})
    assert response.status_code == 201
    return response.json()["id"]

def pilot_consignment() -> int:
    origin, destination = location("Pilot route A", 12.1, 77.1), location("Pilot route B", 12.2, 77.2)
    response = client.post("/api/v1/consignments", json={"origin_location_id": origin, "destination_location_id": destination, "data_source": "pilot_entered", "species": "Cattle", "animal_count": 3, "vehicle_reference": "PILOT-ROAD", "departure_at": datetime.now(UTC).isoformat(), "vaccination_evidence": "verified"})
    assert response.status_code == 201
    return response.json()["id"]

class WorkingProvider:
    def route(self, origin, destination):
        return RoadRoute(geometry=[[origin[0], origin[1]], [destination[0], destination[1]]], distance_km=18.2, minutes=31, provider="mock-osrm")

class DownProvider:
    def route(self, origin, destination):
        raise RuntimeError("down")

def test_pilot_locations_filter_and_review_radius_validation() -> None:
    seed(); pilot = location("Pilot outbreak", 12.3, 77.3)
    assert all(x["data_source"] == "pilot_entered" for x in client.get("/api/v1/locations?source=pilot_entered").json())
    bad = client.post("/api/v1/outbreaks", json={"disease_name":"Pilot disease","species":"Cattle","status":"suspected","location_id":pilot,"data_source":"pilot_entered","review_radius_km":0,"detected_at":datetime.now(UTC).isoformat(),"verification_level":"reported"})
    assert bad.status_code == 422
    demo = client.get("/api/v1/locations?source=demo_seed").json()[0]["id"]
    assert client.post("/api/v1/outbreaks", json={"disease_name":"Demo","species":"Cattle","status":"suspected","location_id":demo,"data_source":"demo_seed","review_radius_km":2,"detected_at":datetime.now(UTC).isoformat(),"verification_level":"reported"}).status_code == 422

def test_mocked_pilot_road_route_persists_and_demo_never_calls_provider() -> None:
    seed(); consignment_id = pilot_consignment()
    with SessionLocal() as db:
        assessment = RouteService(WorkingProvider()).assess(db, consignment_id)
        assert assessment.route_provider == "mock-osrm" and assessment.route_geometry and assessment.safer_route is None
        demo_id = client.get("/api/v1/consignments?source=demo_seed").json()[0]["id"]
        demo = RouteService(DownProvider()).assess(db, demo_id)
        assert demo.route_provider is None and demo.route_geometry is None

def test_unavailable_pilot_route_returns_explicit_fallback() -> None:
    seed(); consignment_id = pilot_consignment()
    with SessionLocal() as db:
        assessment = RouteService(DownProvider()).assess(db, consignment_id)
        assert assessment.route_geometry is None
        assert assessment.route_fallback_reason == "Road route unavailable; no navigation recommendation is shown."
