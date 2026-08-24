from fastapi import APIRouter, Depends

from app.api.deps import verify_internal_key
from app.db import repository
from app.schemas.conversation import (
    ContextTokensUpdate,
    ConversationCreate,
    ConversationOut,
    SandboxSessionUpdate,
    SubagentTraceUpdate,
    TitleUpdate,
    TouchUpdate,
)

router = APIRouter(dependencies=[Depends(verify_internal_key)])


@router.get("", response_model=list[ConversationOut])
async def list_conversations(user_id: str):
    return await repository.list_conversations(user_id)


@router.post("", response_model=ConversationOut)
async def create_conversation(body: ConversationCreate):
    return await repository.create_conversation(body.title, body.user_id)


@router.get("/{conversation_id}", response_model=ConversationOut | None)
async def get_conversation(conversation_id: str):
    # Returned as data (possibly null), not a 404 — callers on the client
    # side (e.g. ownership checks, sandbox reattachment) already treat a
    # missing conversation as a normal case to branch on, same as the
    # in-process repository function this replaces used to.
    return await repository.get_conversation(conversation_id)


@router.patch("/{conversation_id}/title")
async def update_title(conversation_id: str, body: TitleUpdate):
    await repository.update_conversation_title(conversation_id, body.title)
    return {"ok": True}


@router.patch("/{conversation_id}/touch")
async def touch_conversation(conversation_id: str, body: TouchUpdate):
    await repository.touch_conversation(conversation_id, body.model, body.subagent_model)
    return {"ok": True}


@router.patch("/{conversation_id}/context-tokens")
async def set_context_tokens(conversation_id: str, body: ContextTokensUpdate):
    await repository.set_context_tokens(conversation_id, body.tokens)
    return {"ok": True}


@router.patch("/{conversation_id}/sandbox-session")
async def set_sandbox_session_id(conversation_id: str, body: SandboxSessionUpdate):
    await repository.set_sandbox_session_id(conversation_id, body.session_id)
    return {"ok": True}


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    await repository.delete_conversation(conversation_id)
    return {"ok": True}


@router.put("/{conversation_id}/subagent-traces/{tool_call_id}")
async def save_subagent_trace(conversation_id: str, tool_call_id: str, body: SubagentTraceUpdate):
    await repository.save_subagent_trace(conversation_id, tool_call_id, body.events)
    return {"ok": True}


@router.get("/{conversation_id}/subagent-traces")
async def get_subagent_traces(conversation_id: str):
    return await repository.get_subagent_traces(conversation_id)
