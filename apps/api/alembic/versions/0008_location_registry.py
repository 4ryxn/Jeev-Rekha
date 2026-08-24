"""add pilot location registry metadata

Revision ID: 0008_location_registry
Revises: 0007_review_cases
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_location_registry"
down_revision = "0007_review_cases"
branch_labels = None
depends_on = None


def upgrade() -> None:
    data_source = sa.Enum("demo_seed", "pilot_entered", name="locationdatasource")
    data_source.create(op.get_bind(), checkfirst=True)

    op.add_column("locations", sa.Column("district", sa.String(length=120), nullable=True))
    op.add_column("locations", sa.Column("state", sa.String(length=120), nullable=True))
    op.add_column("locations", sa.Column("data_source", data_source, nullable=True))
    op.add_column("locations", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("locations", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.execute("UPDATE locations SET district = 'Jeev Rekha District', state = 'Sampoorna State', data_source = 'demo_seed' WHERE district IS NULL OR state IS NULL OR data_source IS NULL")
    op.alter_column("locations", "district", nullable=False)
    op.alter_column("locations", "state", nullable=False)
    op.alter_column("locations", "data_source", nullable=False)
    op.drop_constraint("locations_name_key", "locations", type_="unique")
    op.create_check_constraint("ck_locations_valid_latitude", "locations", "latitude >= -90 AND latitude <= 90")
    op.create_check_constraint("ck_locations_valid_longitude", "locations", "longitude >= -180 AND longitude <= 180")
    op.create_index("ix_locations_active_source", "locations", ["is_active", "data_source"])
    op.create_index(
        "uq_locations_active_name_district_state",
        "locations",
        ["name", "district", "state"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )


def downgrade() -> None:
    op.drop_index("uq_locations_active_name_district_state", table_name="locations")
    op.drop_index("ix_locations_active_source", table_name="locations")
    op.drop_constraint("ck_locations_valid_longitude", "locations", type_="check")
    op.drop_constraint("ck_locations_valid_latitude", "locations", type_="check")
    op.create_unique_constraint("locations_name_key", "locations", ["name"])
    op.drop_column("locations", "updated_at")
    op.drop_column("locations", "is_active")
    op.drop_column("locations", "data_source")
    op.drop_column("locations", "state")
    op.drop_column("locations", "district")
    sa.Enum(name="locationdatasource").drop(op.get_bind(), checkfirst=True)
