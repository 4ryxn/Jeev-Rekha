"""add advisory evidence and output tables

Revision ID: 0002_advisories_and_evidence
Revises: 0001_core_operations
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_advisories_and_evidence"
down_revision = "0001_core_operations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    risk_state = sa.Enum("green", "amber", "red", "grey", name="riskstate")
    vaccination_evidence = postgresql.ENUM(name="vaccinationevidence", create_type=False)
    verification_level = postgresql.ENUM(name="verificationlevel", create_type=False)
    op.create_table(
        "vaccination_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("consignment_id", sa.Integer(), sa.ForeignKey("consignments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence", vaccination_evidence, nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verification_level", verification_level, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_vaccination_events_consignment_recorded_at", "vaccination_events", ["consignment_id", "recorded_at"])
    op.create_table(
        "surveillance_updates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verification_level", verification_level, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_surveillance_updates_location_updated_at", "surveillance_updates", ["location_id", "updated_at"])
    op.create_table(
        "advisories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("consignment_id", sa.Integer(), sa.ForeignKey("consignments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("risk_state", risk_state, nullable=False),
        sa.Column("evidence_coverage_score", sa.Integer(), nullable=False),
        sa.Column("reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence_factors", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recommended_action", sa.Text(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("rules_version", sa.String(length=32), nullable=False),
        sa.CheckConstraint("evidence_coverage_score >= 0 AND evidence_coverage_score <= 100", name="ck_advisories_coverage_range"),
    )
    op.create_index("ix_advisories_consignment_evaluated_at", "advisories", ["consignment_id", "evaluated_at"])
    op.create_index("ix_advisories_risk_state", "advisories", ["risk_state"])


def downgrade() -> None:
    op.drop_table("advisories")
    op.drop_table("surveillance_updates")
    op.drop_table("vaccination_events")
    op.execute("DROP TYPE IF EXISTS riskstate")
