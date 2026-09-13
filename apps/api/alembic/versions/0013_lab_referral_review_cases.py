"""allow lab referral review case categories

Revision ID: 0013_lab_referral_review_cases
Revises: 0012_outbreak_review_samples
"""

from alembic import op


revision = "0013_lab_referral_review_cases"
down_revision = "0012_outbreak_review_samples"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_review_cases_category", "review_cases", type_="check")
    op.create_check_constraint(
        "ck_review_cases_category",
        "review_cases",
        "category IN ('evidence_gap', 'sync_exception', 'trace_contact', 'lab_referral')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_review_cases_category", "review_cases", type_="check")
    op.create_check_constraint(
        "ck_review_cases_category",
        "review_cases",
        "category IN ('evidence_gap', 'sync_exception', 'trace_contact')",
    )
