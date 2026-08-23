"""create core operations tables

Revision ID: 0001_core_operations
Revises:
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0001_core_operations"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    location_type = sa.Enum("village", "market", "checkpost", "veterinary_centre", name="locationtype")
    outbreak_status = sa.Enum("suspected", "confirmed", "closed", name="outbreakstatus")
    verification_level = sa.Enum("reported", "veterinary_verified", "laboratory_confirmed", name="verificationlevel")
    vaccination_evidence = sa.Enum("verified", "declared", "unknown", name="vaccinationevidence")
    movement_event_type = sa.Enum("departure", "market_entry", "checkpoint", "arrival", name="movementeventtype")

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False, unique=True),
        sa.Column("type", location_type, nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("geometry", Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_locations_type", "locations", ["type"])
    op.create_index("ix_locations_geometry", "locations", ["geometry"], postgresql_using="gist")
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vehicle_reference", sa.String(length=64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_table(
        "outbreaks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("disease_name", sa.String(length=120), nullable=False),
        sa.Column("species", sa.String(length=80), nullable=False),
        sa.Column("status", outbreak_status, nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("suspected_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confirmed_cases", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mortality_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("verification_level", verification_level, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_outbreaks_status_detected_at", "outbreaks", ["status", "detected_at"])
    op.create_table(
        "consignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("origin_location_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("destination_location_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("species", sa.String(length=80), nullable=False),
        sa.Column("animal_count", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("departure_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vaccination_evidence", vaccination_evidence, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("animal_count > 0", name="ck_consignments_positive_animal_count"),
        sa.CheckConstraint("origin_location_id <> destination_location_id", name="ck_consignments_different_locations"),
    )
    op.create_index("ix_consignments_departure_at", "consignments", ["departure_at"])
    op.create_table(
        "movement_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("consignment_id", sa.Integer(), sa.ForeignKey("consignments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("event_type", movement_event_type, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_movement_events_consignment_occurred_at", "movement_events", ["consignment_id", "occurred_at"])


def downgrade() -> None:
    op.drop_table("movement_events")
    op.drop_table("consignments")
    op.drop_table("outbreaks")
    op.drop_table("vehicles")
    op.drop_index("ix_locations_geometry", table_name="locations")
    op.drop_table("locations")
    op.execute("DROP TYPE IF EXISTS movementeventtype")
    op.execute("DROP TYPE IF EXISTS vaccinationevidence")
    op.execute("DROP TYPE IF EXISTS verificationlevel")
    op.execute("DROP TYPE IF EXISTS outbreakstatus")
    op.execute("DROP TYPE IF EXISTS locationtype")
