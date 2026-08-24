"""add immutable pilot advisory evidence snapshots

Revision ID: 0011_pilot_advisory_integrity
Revises: 0010_pilot_geography
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
revision="0011_pilot_advisory_integrity"; down_revision="0010_pilot_geography"; branch_labels=None; depends_on=None
def upgrade():
 op.add_column("advisories",sa.Column("policy_snapshot",JSONB(),nullable=True));op.add_column("advisories",sa.Column("considered_outbreak_ids",JSONB(),nullable=True));op.add_column("advisories",sa.Column("route_state",sa.String(length=64),nullable=True))
def downgrade():
 op.drop_column("advisories","route_state");op.drop_column("advisories","considered_outbreak_ids");op.drop_column("advisories","policy_snapshot")
