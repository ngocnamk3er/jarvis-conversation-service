from datetime import datetime
from pydantic import BaseModel


class ConversationOut(BaseModel):
    id: str
    user_id: str
    title: str
    last_model: str | None = None
    last_subagent_model: str | None = None
    context_tokens: int = 0
    sandbox_session_id: str | None = None
    created_at: datetime
    updated_at: datetime


class ConversationCreate(BaseModel):
    title: str
    user_id: str


class TitleUpdate(BaseModel):
    title: str


class TouchUpdate(BaseModel):
    model: str | None = None
    subagent_model: str | None = None


class ContextTokensUpdate(BaseModel):
    tokens: int


class SandboxSessionUpdate(BaseModel):
    session_id: str | None = None


class SubagentTraceUpdate(BaseModel):
    events: list[dict]


class MessageTraceUpdate(BaseModel):
    trace_id: str
