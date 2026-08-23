"""add containment scenarios
Revision ID: 0006_containment_scenarios
Revises: 0005_offline_sync
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0006_containment_scenarios"; down_revision="0005_offline_sync"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("containment_scenarios",sa.Column("id",sa.Integer,primary_key=True),sa.Column("outbreak_id",sa.Integer,sa.ForeignKey("outbreaks.id",ondelete="CASCADE"),nullable=False),sa.Column("horizon_days",sa.Integer,nullable=False),sa.Column("selected_actions",postgresql.JSONB,nullable=False),sa.Column("baseline_summary",postgresql.JSONB,nullable=False),sa.Column("scenario_summary",postgresql.JSONB,nullable=False),sa.Column("assumptions",postgresql.JSONB,nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False));op.create_index("ix_containment_scenarios_outbreak_created_at","containment_scenarios",["outbreak_id","created_at"])
def downgrade(): op.drop_table("containment_scenarios")
