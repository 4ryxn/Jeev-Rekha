"""add root operational data context

Revision ID: 0009_data_context
Revises: 0008_location_registry
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_data_context"
down_revision = "0008_location_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    source_enum = sa.Enum("demo_seed", "pilot_entered", name="locationdatasource")
    source_enum.create(op.get_bind(), checkfirst=True)
    for table in ("outbreaks", "consignments"):
        op.add_column(table, sa.Column("data_source", source_enum, nullable=True))
        # Every record that predates Pilot Mode is controlled synthetic demo data.
        op.execute(f"UPDATE {table} SET data_source = 'demo_seed' WHERE data_source IS NULL")
        op.alter_column(table, "data_source", nullable=False)
    op.add_column("sync_receipts", sa.Column("data_source", source_enum, nullable=True))
    op.execute("UPDATE sync_receipts SET data_source = 'demo_seed' WHERE data_source IS NULL")
    op.create_index("ix_outbreaks_data_source_detected_at", "outbreaks", ["data_source", "detected_at"])
    op.create_index("ix_consignments_data_source_departure_at", "consignments", ["data_source", "departure_at"])


def downgrade() -> None:
    op.drop_index("ix_consignments_data_source_departure_at", table_name="consignments")
    op.drop_index("ix_outbreaks_data_source_detected_at", table_name="outbreaks")
    op.drop_column("consignments", "data_source")
    op.drop_column("outbreaks", "data_source")
    op.drop_column("sync_receipts", "data_source")
