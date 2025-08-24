from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
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
        # Seed route from URL query param (e.g., /ws?path=widgets)
        try:
            path_param = websocket.query_params.get("path")  # type: ignore[attr-defined]
            if isinstance(path_param, str) and path_param:
                # Normalize: strip leading slashes
                norm = path_param.lstrip("/")
                session.vars["path"] = norm or "home"
        except Exception:
            # Best-effort; ignore if unavailable in environment
            pass

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

    if cfg.enable_uploads:
        cfg.upload_dir.mkdir(parents=True, exist_ok=True)

        @app.post("/upload")
        async def upload(file: UploadFile = File(...)) -> Dict[str, Any]:
            contents = await file.read()
            size_mb = len(contents) / (1024 * 1024)
            if size_mb > cfg.max_upload_size_mb:
                raise HTTPException(status_code=413, detail="File too large")
            target = (cfg.upload_dir / file.filename).resolve()
            if cfg.upload_dir not in target.parents and cfg.upload_dir != target:
                raise HTTPException(status_code=400, detail="Invalid file path")
            target.write_bytes(contents)
            return {"filename": file.filename, "size": len(contents)}

    static_dir = cfg.static_dir or (Path(__file__).parent / "static")
    if cfg.mount_static and static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


