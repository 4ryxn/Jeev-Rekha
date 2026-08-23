import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import inspect, text

from app.db.session import engine

API_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    """Exercise Alembic against the local synthetic development database."""
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API_ROOT, check=True)
    required = {"locations", "vehicles", "outbreaks", "consignments", "movement_events", "trace_runs", "trace_findings"}
    assert required.issubset(set(inspect(engine).get_table_names()))


def clear_operations_data() -> None:
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE trace_findings, trace_runs, route_assessments, route_segments, advisories, vaccination_events, surveillance_updates, movement_events, consignments, outbreaks, vehicles, locations RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def empty_operations_data(migrated_database: None) -> None:
    clear_operations_data()
    yield
    clear_operations_data()
