from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False, server_default="New conversation")
    last_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_subagent_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Current context size (not a lifetime total) — the most recent top-level
    # LLM call's total_tokens, overwritten each turn by the Chat/Agent
    # service. Drops after a Compact run since the follow-up model call that
    # closes out the tool turn sees the now-trimmed context.
    context_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    # OpenSandbox isolation-session ID for this conversation's bash sandbox,
    # set/cleared by the Chat/Agent service so any of its processes can
    # reattach to the same session on the shared host pod.
    sandbox_session_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class SubagentTrace(Base):
    """A subagent's own tool_start/tool_end events (via the `task` tool), saved
    purely for the user to view after reload — never read back into the model's
    context. Keyed by the `task` call's tool_call_id, which is stable across
    reloads (unlike LangGraph's per-run run_id)."""

    __tablename__ = "subagent_traces"

    tool_call_id: Mapped[str] = mapped_column(Text, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        Text, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    events: Mapped[list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class MessageTrace(Base):
    """Maps one assistant message to the Langfuse trace Jarvis recorded while
    generating it — purely so the frontend's thumbs up/down control (see
    jarvis-backend's observability.create_score) knows which trace to attach
    feedback to, including after a reload (the live SSE stream already tells
    it the trace_id directly; this is what the message-history endpoint reads
    instead, same role subagent_traces plays for subagent output). Keyed by
    the LangChain message id, which — like a `task` call's tool_call_id — is
    stable across reloads, unlike a LangGraph run_id."""

    __tablename__ = "message_traces"

    message_id: Mapped[str] = mapped_column(Text, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        Text, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trace_id: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
