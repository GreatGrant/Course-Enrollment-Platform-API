"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-05-28 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index(op.f("ix_courses_code"), "courses", ["code"], unique=True)
    op.create_index(op.f("ix_courses_id"), "courses", ["id"], unique=False)

    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )
    op.create_index(op.f("ix_enrollments_course_id"), "enrollments", ["course_id"], unique=False)
    op.create_index(op.f("ix_enrollments_id"), "enrollments", ["id"], unique=False)
    op.create_index(op.f("ix_enrollments_user_id"), "enrollments", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_enrollments_user_id"), table_name="enrollments")
    op.drop_index(op.f("ix_enrollments_id"), table_name="enrollments")
    op.drop_index(op.f("ix_enrollments_course_id"), table_name="enrollments")
    op.drop_table("enrollments")

    op.drop_index(op.f("ix_courses_id"), table_name="courses")
    op.drop_index(op.f("ix_courses_code"), table_name="courses")
    op.drop_table("courses")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")