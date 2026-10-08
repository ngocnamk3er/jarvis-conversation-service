"""create message_traces

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-08

Maps an assistant message to the Langfuse trace recorded while generating
it, for the message-feedback (thumbs up/down) feature — see
jarvis-backend's app/core/observability.py.
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "message_traces",
        sa.Column("message_id", sa.Text(), nullable=False),
        sa.Column("conversation_id", sa.Text(), nullable=False),
        sa.Column("trace_id", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index(op.f("ix_message_traces_conversation_id"), "message_traces", ["conversation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_message_traces_conversation_id"), table_name="message_traces")
    op.drop_table("message_traces")
