"""add bonus features: soft deletes and audit logs

Revision ID: 0002_add_bonus_features
Revises: 0001_initial_schema
Create Date: 2026-06-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_bonus_features"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Soft delete column on courses
    op.add_column("courses", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Audit logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("performed_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_course_id"), "audit_logs", ["course_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_course_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_column("courses", "deleted_at")
