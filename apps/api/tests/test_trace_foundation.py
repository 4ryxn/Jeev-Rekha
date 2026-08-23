from datetime import UTC, datetime, timedelta
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import Location, Outbreak, TraceFinding, TraceRun
from app.models.core import LocationType, OutbreakStatus, TraceDirection, TraceEvidenceLevel, VerificationLevel
from app.repositories.traces import TraceRepository


API_ROOT = Path(__file__).resolve().parents[1]


def test_trace_lab_migration_runs_on_an_isolated_clean_postgis_database() -> None:
    """The temporary database is created and removed without touching development data."""
    database_url = make_url(get_settings().database_url)
    temporary_name = f"jeevrekha_trace_test_{uuid4().hex[:12]}"
    temporary_url = database_url.set(database=temporary_name)
    admin_engine = create_engine(database_url.set(database="postgres"), isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{temporary_name}"'))
    try:
        environment = os.environ.copy()
        environment["DATABASE_URL"] = temporary_url.render_as_string(hide_password=False)
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API_ROOT, env=environment, check=True)
        temporary_engine = create_engine(temporary_url)
        try:
            tables = set(inspect(temporary_engine).get_table_names())
            assert {"trace_runs", "trace_findings"}.issubset(tables)
        finally:
            temporary_engine.dispose()
    finally:
        with admin_engine.connect() as connection:
            connection.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = :name"), {"name": temporary_name})
            connection.execute(text(f'DROP DATABASE IF EXISTS "{temporary_name}"'))
        admin_engine.dispose()


def trace_outbreak() -> Outbreak:
    db = SessionLocal()
    try:
        location = Location(
            name="Trace Foundation Village",
            type=LocationType.VILLAGE,
            latitude=12.91,
            longitude=77.61,
            geometry="SRID=4326;POINT(77.61 12.91)",
        )
        db.add(location)
        db.flush()
        outbreak = Outbreak(
            disease_name="Synthetic trace foundation disease",
            species="Cattle",
            status=OutbreakStatus.CONFIRMED,
            location_id=location.id,
            detected_at=datetime.now(UTC),
            confirmed_at=datetime.now(UTC),
            suspected_cases=1,
            confirmed_cases=1,
            mortality_count=0,
            verification_level=VerificationLevel.LABORATORY_CONFIRMED,
        )
        db.add(outbreak)
        db.commit()
        db.refresh(outbreak)
        return outbreak
    finally:
        db.close()


def test_trace_run_persists_with_safe_parameters_default() -> None:
    outbreak = trace_outbreak()
    now = datetime.now(UTC)
    db = SessionLocal()
    try:
        trace_run = TraceRun(
            outbreak_id=outbreak.id,
            direction=TraceDirection.REWIND,
            window_start=now - timedelta(days=14),
            window_end=now,
        )
        saved = TraceRepository().create_trace_run(db, trace_run)
        assert saved.id is not None
        assert saved.parameters == {}
        assert saved.direction == TraceDirection.REWIND
    finally:
        db.close()


def test_trace_finding_persists_and_retrieval_is_chronological() -> None:
    outbreak = trace_outbreak()
    now = datetime.now(UTC)
    db = SessionLocal()
    try:
        repository = TraceRepository()
        run = repository.create_trace_run(db, TraceRun(
            outbreak_id=outbreak.id,
            direction=TraceDirection.FAST_FORWARD,
            window_start=now,
            window_end=now + timedelta(days=14),
            parameters={"source": "synthetic test"},
        ))
        repository.add_trace_findings(db, [
            TraceFinding(
                trace_run_id=run.id,
                entity_type="location",
                entity_id="2",
                relationship_type="outgoing_movement",
                event_timestamp=now + timedelta(hours=2),
                evidence_level=TraceEvidenceLevel.INDIRECT,
                explanation="Synthetic evidence-backed record requires veterinary review.",
            ),
            TraceFinding(
                trace_run_id=run.id,
                entity_type="consignment",
                entity_id="1",
                relationship_type="outgoing_movement",
                event_timestamp=now + timedelta(hours=1),
                evidence_level=TraceEvidenceLevel.DIRECT,
                explanation="Synthetic evidence-backed record requires veterinary review.",
            ),
        ])
        found = repository.get_trace_run_with_findings(db, run.id)
        assert found is not None
        assert [finding.entity_id for finding in found.findings] == ["1", "2"]
        assert found.findings[0].trace_run_id == run.id
        assert found.findings[0].review_status == "requires_veterinary_review"
    finally:
        db.close()


def test_invalid_direction_and_evidence_level_are_rejected() -> None:
    outbreak = trace_outbreak()
    now = datetime.now(UTC)
    db = SessionLocal()
    try:
        db.add(TraceRun(
            outbreak_id=outbreak.id,
            direction="sideways",  # type: ignore[arg-type] -- exercise the database constraint.
            window_start=now,
            window_end=now,
        ))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        run = TraceRepository().create_trace_run(db, TraceRun(
            outbreak_id=outbreak.id,
            direction=TraceDirection.REWIND,
            window_start=now - timedelta(days=1),
            window_end=now,
        ))
        db.add(TraceFinding(
            trace_run_id=run.id,
            entity_type="vehicle",
            entity_id="1",
            relationship_type="shared_vehicle",
            event_timestamp=now,
            evidence_level="unsupported",  # type: ignore[arg-type] -- exercise the database constraint.
            explanation="Synthetic record requires veterinary review.",
        ))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.close()
