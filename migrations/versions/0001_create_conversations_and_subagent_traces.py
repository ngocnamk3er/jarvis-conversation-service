"""create conversations and subagent_traces

Revision ID: 0001
Revises:
Create Date: 2026-08-24

The full, final schema in a single migration — this service starts with a
fresh, empty database, so there's no history to replay from jarvis-backend's
own (now-deleted) migrations/ directory.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False, server_default="New conversation"),
        sa.Column("last_model", sa.Text(), nullable=True),
        sa.Column("last_subagent_model", sa.Text(), nullable=True),
        sa.Column("context_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sandbox_session_id", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_user_id"), "conversations", ["user_id"], unique=False)

    op.create_table(
        "subagent_traces",
        sa.Column("tool_call_id", sa.Text(), nullable=False),
        sa.Column("conversation_id", sa.Text(), nullable=False),
        sa.Column("events", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tool_call_id"),
    )
    op.create_index(op.f("ix_subagent_traces_conversation_id"), "subagent_traces", ["conversation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_subagent_traces_conversation_id"), table_name="subagent_traces")
    op.drop_table("subagent_traces")
    op.drop_index(op.f("ix_conversations_user_id"), table_name="conversations")
    op.drop_table("conversations")
