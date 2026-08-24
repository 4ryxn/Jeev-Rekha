"""add pilot geographic review and route details

Revision ID: 0010_pilot_geography
Revises: 0009_data_context
"""
from alembic import op
import sqlalchemy as sa

revision = "0010_pilot_geography"
down_revision = "0009_data_context"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("outbreaks", sa.Column("review_radius_km", sa.Float(), nullable=True))
    op.create_check_constraint("ck_outbreaks_positive_review_radius", "outbreaks", "review_radius_km IS NULL OR review_radius_km > 0")
    op.add_column("route_assessments", sa.Column("route_provider", sa.String(length=120), nullable=True))
    op.add_column("route_assessments", sa.Column("route_geometry", sa.dialects.postgresql.JSONB(), nullable=True))
    op.add_column("route_assessments", sa.Column("route_fallback_reason", sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column("route_assessments", "route_fallback_reason")
    op.drop_column("route_assessments", "route_geometry")
    op.drop_column("route_assessments", "route_provider")
    op.drop_constraint("ck_outbreaks_positive_review_radius", "outbreaks", type_="check")
    op.drop_column("outbreaks", "review_radius_km")
