import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import make_url

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import MovementEvent, Outbreak, TraceRun
from app.models.core import OutbreakStatus, TraceDirection, TraceEvidenceLevel
from app.seed import seed
from app.services.tracing import TraceService, TraceValidationError


API_ROOT = Path(__file__).resolve().parents[1]


def confirmed_fmd() -> Outbreak:
    seed()
    db = SessionLocal()
    try:
        return db.scalar(select(Outbreak).where(
            Outbreak.disease_name == "Foot-and-mouth disease",
            Outbreak.status == OutbreakStatus.CONFIRMED,
        ))  # type: ignore[return-value]
    finally:
        db.close()


def create_trace(direction: TraceDirection, window_override: int | None = None) -> TraceRun:
    outbreak = confirmed_fmd()
    db = SessionLocal()
    try:
        service = TraceService()
        if direction == TraceDirection.REWIND:
            return service.create_rewind_trace(db, outbreak.id, window_override)
        return service.create_fast_forward_trace(db, outbreak.id, window_override)
    finally:
        db.close()


def test_confirmed_fmd_creates_a_persisted_rewind_trace_with_direct_and_indirect_findings() -> None:
    trace = create_trace(TraceDirection.REWIND)
    assert trace.id is not None
    assert trace.direction == TraceDirection.REWIND
    assert trace.parameters["review_window_days"] == 14
    assert {finding.evidence_level for finding in trace.findings} == {
        TraceEvidenceLevel.DIRECT,
        TraceEvidenceLevel.INDIRECT,
    }
    assert any(finding.relationship_type == "incoming_movement" for finding in trace.findings)


def test_confirmed_fmd_creates_a_distinct_persisted_fast_forward_trace() -> None:
    rewind = create_trace(TraceDirection.REWIND)
    fast_forward = create_trace(TraceDirection.FAST_FORWARD)
    assert fast_forward.id != rewind.id
    assert fast_forward.direction == TraceDirection.FAST_FORWARD
    assert {finding.evidence_level for finding in fast_forward.findings} == {
        TraceEvidenceLevel.DIRECT,
        TraceEvidenceLevel.INDIRECT,
    }
    assert any(finding.relationship_type == "outgoing_movement" for finding in fast_forward.findings)
    assert {finding.entity_id for finding in rewind.findings} != {finding.entity_id for finding in fast_forward.findings}


def test_review_window_override_excludes_outside_rewind_events() -> None:
    trace = create_trace(TraceDirection.REWIND, window_override=1)
    assert trace.findings == []
    assert trace.window_end > trace.window_start


def test_suspected_and_closed_outbreaks_are_rejected() -> None:
    seed()
    db = SessionLocal()
    try:
        service = TraceService()
        statuses = [OutbreakStatus.SUSPECTED, OutbreakStatus.CLOSED]
        for status in statuses:
            outbreak = db.scalar(select(Outbreak).where(Outbreak.status == status))
            assert outbreak is not None
            with pytest.raises(TraceValidationError, match="Only confirmed outbreaks"):
                service.create_rewind_trace(db, outbreak.id)
    finally:
        db.close()


def test_findings_are_chronological_and_have_neutral_required_fields() -> None:
    trace = create_trace(TraceDirection.REWIND)
    timestamps = [finding.event_timestamp for finding in trace.findings]
    assert timestamps == sorted(timestamps)
    for finding in trace.findings:
        assert finding.evidence_level in {TraceEvidenceLevel.DIRECT, TraceEvidenceLevel.INDIRECT}
        assert finding.explanation
        assert "requires veterinary review" in finding.explanation.lower()
        assert finding.review_status == "requires_veterinary_review"


def test_seed_is_idempotent_for_trace_connections() -> None:
    seed()
    db = SessionLocal()
    try:
        initial_count = db.scalar(select(func.count(MovementEvent.id)))
    finally:
        db.close()
    message = seed()
    db = SessionLocal()
    try:
        assert db.scalar(select(func.count(MovementEvent.id))) == initial_count
    finally:
        db.close()
    assert "already exist" in message


def test_trace_service_runs_from_a_clean_isolated_seeded_postgis_database() -> None:
    """Migrate, seed, trace, and remove an isolated database without using development rows."""
    database_url = make_url(get_settings().database_url)
    temporary_name = f"jeevrekha_trace_service_{uuid4().hex[:12]}"
    temporary_url = database_url.set(database=temporary_name)
    admin_engine = create_engine(database_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{temporary_name}"'))
    try:
        environment = os.environ.copy()
        environment["DATABASE_URL"] = temporary_url.render_as_string(hide_password=False)
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API_ROOT, env=environment, check=True)
        subprocess.run([sys.executable, "-m", "app.seed"], cwd=API_ROOT, env=environment, check=True)
        verify_script = """
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
assert client.get('/api/v1/health').status_code == 200
outbreak = next(item for item in client.get('/api/v1/outbreaks').json() if item['disease_name'] == 'Foot-and-mouth disease')
rewind = client.post(f\"/api/v1/outbreaks/{outbreak['id']}/traces\", json={'direction': 'rewind'})
assert rewind.status_code == 201, rewind.text
fast = client.post(f\"/api/v1/outbreaks/{outbreak['id']}/traces\", json={'direction': 'fast_forward'})
assert fast.status_code == 201, fast.text
assert {item['evidence_level'] for item in rewind.json()['findings']} == {'direct', 'indirect'}
assert {item['evidence_level'] for item in fast.json()['findings']} == {'direct', 'indirect'}
assert client.get(f\"/api/v1/traces/{rewind.json()['id']}\").status_code == 200
locations = client.get('/api/v1/locations?type=village').json()
operation = {'client_operation_id': 'isolated-sync-0001', 'operation_type': 'create_consignment', 'payload': {'origin_location_id': locations[0]['id'], 'destination_location_id': locations[1]['id'], 'species': 'Goat', 'animal_count': 3, 'vehicle_reference': 'ISO-SYNC-01', 'departure_at': '2026-08-24T10:00:00Z', 'vaccination_evidence': 'declared'}}
synced = client.post('/api/v1/sync/operations', json={'operations': [operation]})
assert synced.status_code == 200, synced.text
retried = client.post('/api/v1/sync/operations', json={'operations': [operation]})
assert retried.json()[0]['entity_id'] == synced.json()[0]['entity_id']
scenario = client.post(f\"/api/v1/outbreaks/{outbreak['id']}/containment-scenarios\", json={'horizon_days': 7, 'selected_actions': ['checkpoint_screening']})
assert scenario.status_code == 201, scenario.text
assert client.get(f\"/api/v1/containment-scenarios/{scenario.json()['id']}\").status_code == 200
cases = client.get('/api/v1/review-cases')
assert cases.status_code == 200 and cases.json(), cases.text
case = cases.json()[0]
updated = client.patch(f\"/api/v1/review-cases/{case['id']}\", json={'status': 'acknowledged'})
assert updated.status_code == 200 and updated.json()['status'] == 'acknowledged', updated.text
reports = client.get('/api/v1/reports')
assert reports.status_code == 200 and reports.json()['advisories'], reports.text
assert client.get(f\"/api/v1/reports/advisories/{reports.json()['advisories'][0]['id']}\").status_code == 200
assert any(item['id'] == rewind.json()['id'] for item in reports.json()['traces'])
assert any(item['id'] == scenario.json()['id'] for item in reports.json()['containment'])
assert client.get(f\"/api/v1/reports/traces/{rewind.json()['id']}\").status_code == 200
assert client.get(f\"/api/v1/reports/containment/{scenario.json()['id']}\").status_code == 200
"""
        subprocess.run([sys.executable, "-c", verify_script], cwd=API_ROOT, env=environment, check=True)
    finally:
        with admin_engine.connect() as connection:
            connection.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :name"), {"name": temporary_name})
            connection.execute(text(f'DROP DATABASE IF EXISTS "{temporary_name}"'))
        admin_engine.dispose()
