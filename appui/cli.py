from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Optional

import uvicorn

from .runtime import Session
from .server import create_app
from .config import AppUIConfig


def _load_callable(module_path: str, symbol: Optional[str]) -> object:
    path = Path(module_path)
    if not path.exists():
        raise SystemExit(f"File not found: {module_path}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise SystemExit("Cannot load module")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = mod
    spec.loader.exec_module(mod)
    if symbol:
        return getattr(mod, symbol)
    # default export name
    return getattr(mod, "build_ui")


def run() -> None:
    parser = argparse.ArgumentParser(prog="appui", description="Run an APPUI app")
    sub = parser.add_subparsers(dest="command")
    runp = sub.add_parser("run", help="Run an app from a Python file")
    runp.add_argument("target", help="path/to/app.py[:callable] (default callable: build_ui)")
    runp.add_argument("--host", default="127.0.0.1")
    runp.add_argument("--port", type=int, default=8000)
    runp.add_argument("--title", default="APPUI")
    runp.add_argument("--no-static", action="store_true", help="Disable static file serving")
    runp.add_argument("--static-dir", default=None, help="Serve static files from this dir")
    runp.add_argument("--root-path", default="/", help="Application root path")
    runp.add_argument(
        "--allow-origins",
        default="*",
        help="Comma-separated list of allowed CORS origins",
    )

    args = parser.parse_args()
    if args.command != "run":
        parser.print_help()
        raise SystemExit(2)

    module_path, _, symbol = str(args.target).partition(":")
    builder = _load_callable(module_path, symbol)

    cfg = AppUIConfig(
        title=args.title,
        allow_origins=[o.strip() for o in str(args.allow_origins).split(",") if o.strip()],
        mount_static=not bool(args.no_static),
        static_dir=Path(args.static_dir) if args.static_dir else None,
        root_path=args.root_path,
    )

    app = create_app(builder, cfg)  # type: ignore[arg-type]
    uvicorn.run(app, host=str(args.host), port=int(args.port))


if __name__ == "__main__":
    run()


