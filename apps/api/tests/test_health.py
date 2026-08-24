from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import OperationalError
from pydantic import ValidationError

from app.core.config import Settings
from app import main
from app.main import app


def test_health_endpoint_returns_service_status() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "jeev-rekha-api",
        "environment": "development",
    }


def test_readiness_endpoint_reports_database_connectivity() -> None:
    response = TestClient(app).get("/api/v1/readiness")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "connected"}


def test_readiness_endpoint_returns_non_sensitive_failure(monkeypatch) -> None:
    class UnavailableEngine:
        def connect(self):
            raise OperationalError("SELECT 1", {}, RuntimeError("database unavailable"))

    monkeypatch.setattr(main, "engine", UnavailableEngine())
    response = TestClient(app).get("/api/v1/readiness")

    assert response.status_code == 503
    assert response.json() == {"detail": {"status": "not_ready", "database": "unavailable"}}


def test_production_configuration_rejects_unsafe_defaults() -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings(app_env="production", cors_origins="https://web.example", trusted_hosts="api.example")

    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(
            app_env="production",
            database_url="postgresql+psycopg://user:pass@db:5432/jeevrekha",
            cors_origins="*",
            trusted_hosts="api.example",
        )

    production_settings = Settings(
        app_env="production",
        database_url="postgresql+psycopg://user:pass@db:5432/jeevrekha",
        cors_origins="https://web.example",
        trusted_hosts="api.example",
    )
    assert production_settings.demo_seed_enabled is False
