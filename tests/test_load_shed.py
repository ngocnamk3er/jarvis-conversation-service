"""Admission control in the conversation service: the limit is the DB pool, probes are never refused."""

import asyncio

import httpx
from fastapi import FastAPI

from app.core.config import settings
from app.core.load_shed import LoadShedMiddleware, conversation_classifier

PREFIX = "/api/v1"


def build(limit: int):
    app = FastAPI()
    gate = asyncio.Event()

    @app.get("/api/v1/conversations")
    async def listing():
        await gate.wait()
        return []

    @app.get("/")
    async def root():
        await gate.wait()
        return {"ok": True}

    app.add_middleware(LoadShedMiddleware, classify=conversation_classifier(PREFIX), limits=lambda: {"default": limit})
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t"), gate


async def test_past_the_limit_the_caller_is_refused_at_once_and_told_when_to_retry():
    client, gate = build(2)
    held = [asyncio.create_task(client.get("/api/v1/conversations")) for _ in range(2)]
    await asyncio.sleep(0.05)
    refused = await asyncio.wait_for(client.get("/api/v1/conversations"), timeout=1)
    assert refused.status_code == 503 and refused.headers["retry-after"] == "1"
    assert refused.json()["code"] == "overloaded"
    gate.set()
    assert [r.status_code for r in await asyncio.gather(*held)] == [200, 200]
    assert (await client.get("/api/v1/conversations")).status_code == 200          # a slot came back


async def test_the_probe_path_is_never_refused():
    client, gate = build(1)
    held = asyncio.create_task(client.get("/api/v1/conversations"))
    await asyncio.sleep(0.05)
    probe = asyncio.create_task(client.get("/"))
    await asyncio.sleep(0.05)
    gate.set()
    assert (await probe).status_code == 200
    await held


def test_the_default_limit_matches_the_database_pool():
    """SQLAlchemy's default pool is 5 + 10 overflow. A higher limit would let requests queue for a connection."""
    assert settings.LOAD_SHED_MAX_INFLIGHT == 5 + 10


def test_the_real_app_has_the_middleware():
    from app.main import app

    assert LoadShedMiddleware in [m.cls for m in app.user_middleware]
