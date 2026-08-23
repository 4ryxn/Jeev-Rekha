"""add persisted trace lab foundation

Revision ID: 0004_trace_lab
Revises: 0003_routes
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004_trace_lab"
down_revision = "0003_routes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trace_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("outbreak_id", sa.Integer(), sa.ForeignKey("outbreaks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("direction", sa.String(length=32), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("direction IN ('rewind', 'fast_forward')", name="ck_trace_runs_direction"),
    )
    op.create_index("ix_trace_runs_outbreak_created_at", "trace_runs", ["outbreak_id", "created_at"])
    op.create_table(
        "trace_findings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trace_run_id", sa.Integer(), sa.ForeignKey("trace_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("relationship_type", sa.String(length=64), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evidence_level", sa.String(length=16), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("review_status", sa.String(length=64), nullable=False, server_default="requires_veterinary_review"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("evidence_level IN ('direct', 'indirect')", name="ck_trace_findings_evidence_level"),
    )
    op.create_index("ix_trace_findings_run_event_timestamp", "trace_findings", ["trace_run_id", "event_timestamp"])


def downgrade() -> None:
    op.drop_table("trace_findings")
    op.drop_table("trace_runs")
