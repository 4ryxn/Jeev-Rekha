from fastapi.testclient import TestClient
import httpx

from app.main import app
from app.seed import seed
from app.services import weather


client = TestClient(app)


def test_outbreak_trends_aggregate_seeded_data_in_the_requested_context() -> None:
    seed()
    response = client.get("/api/v1/outbreaks/trends?source=demo_seed")
    assert response.status_code == 200, response.text
    points = response.json()
    assert sum(point["outbreak_count"] for point in points) == 3
    assert {point["disease_name"] for point in points} == {
        "Foot-and-mouth disease",
        "Peste des petits ruminants",
        "Haemorrhagic septicaemia",
    }
    assert client.get("/api/v1/outbreaks/trends?source=pilot_entered").json() == []


class OpenMeteoResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return {
            "current": {"time": "2026-09-13T10:00", "temperature_2m": 27.5, "relative_humidity_2m": 71, "wind_speed_10m": 11.2, "weather_code": 3},
            "daily": {"time": ["2026-09-12", "2026-09-13"], "precipitation_sum": [2.4, 0.0], "temperature_2m_max": [29.0, 30.0], "temperature_2m_min": [21.0, 22.0]},
        }


def outbreak_id() -> int:
    seed()
    return client.get("/api/v1/outbreaks?source=demo_seed").json()[0]["id"]


def test_outbreak_weather_context_returns_mocked_open_meteo_conditions(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def get(url: str, **kwargs: object) -> OpenMeteoResponse:
        captured["url"] = url
        captured.update(kwargs)
        return OpenMeteoResponse()

    monkeypatch.setattr(weather.httpx, "get", get)
    response = client.get(f"/api/v1/outbreaks/{outbreak_id()}/weather-context")
    assert response.status_code == 200, response.text
    body = response.json()
    assert captured["url"] == "https://api.open-meteo.com/v1/forecast"
    assert captured["timeout"] == 5.0
    assert body["available"] is True
    assert body["temperature_c"] == 27.5
    assert body["recent_days"] == [{"date": "2026-09-12", "precipitation_mm": 2.4, "temperature_max_c": 29.0, "temperature_min_c": 21.0}, {"date": "2026-09-13", "precipitation_mm": 0.0, "temperature_max_c": 30.0, "temperature_min_c": 22.0}]


def test_outbreak_weather_context_returns_unavailable_fallback_on_timeout(monkeypatch) -> None:
    def get(*args: object, **kwargs: object) -> None:
        raise httpx.TimeoutException("Open-Meteo timed out")

    monkeypatch.setattr(weather.httpx, "get", get)
    response = client.get(f"/api/v1/outbreaks/{outbreak_id()}/weather-context")
    assert response.status_code == 200, response.text
    assert response.json() == {"available": False, "message": "Weather data unavailable.", "observed_at": None, "temperature_c": None, "relative_humidity": None, "wind_speed_kmh": None, "weather_code": None, "recent_days": []}
