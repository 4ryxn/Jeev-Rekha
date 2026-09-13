"""add outbreak sources and review sample tracking

Revision ID: 0012_outbreak_sources_and_review_samples
Revises: 0011_pilot_advisory_integrity
"""

from alembic import op
import sqlalchemy as sa


revision = "0012_outbreak_review_samples"
down_revision = "0011_pilot_advisory_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE outbreakstatus ADD VALUE IF NOT EXISTS 'under_investigation'")

    outbreak_source = sa.Enum(
        "lab_confirmed", "vet_observed", "farmer_reported", name="outbreaksource"
    )
    outbreak_source.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "outbreaks",
        sa.Column(
            "source",
            outbreak_source,
            nullable=False,
            server_default="vet_observed",
        ),
    )

    review_case_type = sa.Enum(
        "evidence_gap", "sync_exception", "trace_contact", "lab_referral", name="reviewcasetype"
    )
    sample_status = sa.Enum(
        "none", "collected", "sent_to_lab", "result_received", name="samplestatus"
    )
    review_case_type.create(op.get_bind(), checkfirst=True)
    sample_status.create(op.get_bind(), checkfirst=True)
    op.add_column("review_cases", sa.Column("case_type", review_case_type, nullable=True))
    op.execute("UPDATE review_cases SET case_type = category::reviewcasetype WHERE case_type IS NULL")
    op.alter_column("review_cases", "case_type", nullable=False, server_default="evidence_gap")
    op.add_column(
        "review_cases",
        sa.Column("sample_status", sample_status, nullable=False, server_default="none"),
    )


def downgrade() -> None:
    op.drop_column("review_cases", "sample_status")
    op.drop_column("review_cases", "case_type")
    sa.Enum(name="samplestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="reviewcasetype").drop(op.get_bind(), checkfirst=True)
    op.drop_column("outbreaks", "source")
    sa.Enum(name="outbreaksource").drop(op.get_bind(), checkfirst=True)
