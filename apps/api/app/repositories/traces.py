from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Location, Outbreak, TraceFinding, TraceRun


class TraceRepository:
    """Persistence helpers only; tracing decisions remain outside this repository."""

    def create_trace_run(self, db: Session, trace_run: TraceRun) -> TraceRun:
        db.add(trace_run)
        db.commit()
        return self.get_trace_run_with_findings(db, trace_run.id)  # type: ignore[return-value]

    def add_trace_findings(self, db: Session, findings: Sequence[TraceFinding]) -> list[TraceFinding]:
        db.add_all(findings)
        db.commit()
        return list(findings)

    def get_trace_run_with_findings(self, db: Session, trace_run_id: int) -> TraceRun | None:
        return db.scalar(
            select(TraceRun)
            .options(selectinload(TraceRun.findings), selectinload(TraceRun.outbreak).selectinload(Outbreak.location))
            .where(TraceRun.id == trace_run_id)
        )

    def list_outbreak_trace_runs(self, db: Session, outbreak_id: int) -> list[TraceRun]:
        return list(
            db.scalars(
                select(TraceRun)
                .options(selectinload(TraceRun.findings), selectinload(TraceRun.outbreak).selectinload(Outbreak.location))
                .where(TraceRun.outbreak_id == outbreak_id)
                .order_by(TraceRun.created_at.desc())
            )
        )
