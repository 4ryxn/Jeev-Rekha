"""add offline sync receipts

Revision ID: 0005_offline_sync
Revises: 0004_trace_lab
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_offline_sync"
down_revision = "0004_trace_lab"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("sync_receipts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("client_operation_id", sa.String(64), nullable=False, unique=True), sa.Column("operation_type", sa.String(32), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("entity_type", sa.String(32)), sa.Column("entity_id", sa.Integer()), sa.Column("payload_hash", sa.String(64), nullable=False), sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.create_index("ix_sync_receipts_received_at", "sync_receipts", ["received_at"])

def downgrade() -> None:
    op.drop_table("sync_receipts")
