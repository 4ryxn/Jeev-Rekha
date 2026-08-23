"""add controlled route graph

Revision ID: 0003_routes
Revises: 0002_advisories_and_evidence
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0003_routes"; down_revision="0002_advisories_and_evidence"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("route_segments",sa.Column("id",sa.Integer,primary_key=True),sa.Column("start_location_id",sa.Integer,sa.ForeignKey("locations.id"),nullable=False),sa.Column("end_location_id",sa.Integer,sa.ForeignKey("locations.id"),nullable=False),sa.Column("distance_km",sa.Float,nullable=False),sa.Column("estimated_minutes",sa.Integer,nullable=False),sa.Column("path",postgresql.JSONB,nullable=False),sa.Column("active",sa.Boolean,nullable=False,server_default=sa.text("true")))
    op.create_table("route_assessments",sa.Column("id",sa.Integer,primary_key=True),sa.Column("consignment_id",sa.Integer,sa.ForeignKey("consignments.id"),nullable=False),sa.Column("preferred_route",postgresql.JSONB,nullable=False),sa.Column("safer_route",postgresql.JSONB),sa.Column("preferred_distance_km",sa.Float,nullable=False),sa.Column("preferred_minutes",sa.Integer,nullable=False),sa.Column("safer_distance_km",sa.Float),sa.Column("safer_minutes",sa.Integer),sa.Column("risk_reduction",sa.String(32),nullable=False),sa.Column("route_reasons",postgresql.JSONB,nullable=False),sa.Column("assessed_at",sa.DateTime(timezone=True),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False))
    op.create_index("ix_route_assessments_consignment_assessed_at","route_assessments",["consignment_id","assessed_at"])
def downgrade(): op.drop_table("route_assessments"); op.drop_table("route_segments")
