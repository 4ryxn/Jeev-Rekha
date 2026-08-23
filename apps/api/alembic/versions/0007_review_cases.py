"""add persisted review cases
Revision ID: 0007_review_cases
Revises: 0006_containment_scenarios
"""
from alembic import op
import sqlalchemy as sa
revision="0007_review_cases"; down_revision="0006_containment_scenarios"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("review_cases",sa.Column("id",sa.Integer,primary_key=True),sa.Column("source_type",sa.String(32),nullable=False),sa.Column("source_id",sa.String(64),nullable=False),sa.Column("category",sa.String(32),nullable=False),sa.Column("priority",sa.String(16),nullable=False),sa.Column("title",sa.String(200),nullable=False),sa.Column("summary",sa.Text,nullable=False),sa.Column("status",sa.String(16),server_default="open",nullable=False),sa.Column("resolution_note",sa.Text),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False),sa.Column("acknowledged_at",sa.DateTime(timezone=True)),sa.Column("resolved_at",sa.DateTime(timezone=True)),sa.CheckConstraint("category IN ('evidence_gap', 'sync_exception', 'trace_contact')",name="ck_review_cases_category"),sa.CheckConstraint("priority IN ('high', 'medium', 'low')",name="ck_review_cases_priority"),sa.CheckConstraint("status IN ('open', 'acknowledged', 'resolved')",name="ck_review_cases_status"),sa.UniqueConstraint("source_type","source_id","category",name="uq_review_cases_source_category"))
 op.create_index("ix_review_cases_status_created_at","review_cases",["status","created_at"])
def downgrade(): op.drop_table("review_cases")
