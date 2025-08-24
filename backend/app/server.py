from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .app_runtime import Session
from .example import build_ui


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    session = Session(builder=build_ui)

    async def send_tree() -> None:
        tree = session.build_tree()
        await websocket.send_text(tree.model_dump_json())

    await send_tree()

    try:
        while True:
            msg = await websocket.receive_text()
            try:
                payload = json.loads(msg)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            event = payload.get("event")
            node_id = payload.get("nodeId")
            value = payload.get("value")
            if isinstance(event, str) and isinstance(node_id, str):
                session.dispatch_event(node_id, event, value)
                await send_tree()
    except WebSocketDisconnect:
        pass


