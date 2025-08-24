from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from appui.server import create_app
from appui.runtime import Session
from appui.models import UINode
from appui.dsl import text


def builder(_session: Session) -> UINode:
    return text("ok")


def test_health_http() -> None:
    app = create_app(builder)
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_websocket_roundtrip() -> None:
    from starlette.testclient import TestClient as WSClient

    app = create_app(builder)
    with WSClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            first = ws.receive_text()
            data: Any = json.loads(first)
            assert isinstance(data, dict)
            assert data.get("type") == "Text"

