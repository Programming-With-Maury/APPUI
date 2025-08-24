from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .runtime import Session
from .models import UINode
from .config import AppUIConfig


def create_app(builder: Callable[[Session], UINode], config: Optional[AppUIConfig] = None) -> FastAPI:
    cfg = config or AppUIConfig()
    app = FastAPI(title=cfg.title, root_path=cfg.root_path)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allow_origins,
        allow_credentials=cfg.allow_credentials,
        allow_methods=cfg.allow_methods,
        allow_headers=cfg.allow_headers,
    )

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {"status": "ok"}

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        session = Session(builder=builder)

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

    static_dir = cfg.static_dir or (Path(__file__).parent / "static")
    if cfg.mount_static and static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


