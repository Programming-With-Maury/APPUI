from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any, Callable, Dict, Optional, Tuple
import os
import time
from pathlib import Path
import json

from .models import UINode


_current_session: ContextVar["Session"] = ContextVar("current_session")


def get_current_session() -> Optional["Session"]:
    try:
        return _current_session.get()
    except LookupError:
        return None


class Session:
    def __init__(self, builder: Callable[["Session"], UINode]):
        self.id: str = uuid.uuid4().hex
        self.vars: Dict[str, Any] = {}
        self._event_handlers: Dict[Tuple[str, str], Callable[[Any], None]] = {}
        self._builder: Callable[["Session"], UINode] = builder
        # Load secrets from environment and optional .env file in CWD
        self.secrets: Dict[str, Any] = {}
        try:
            self.secrets.update(dict(os.environ))
            env_path = Path.cwd() / ".env"
            if env_path.exists():
                for raw in env_path.read_text().splitlines():
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        key = k.strip()
                        val = v.strip().strip('"').strip("'")
                        if key:
                            self.secrets[key] = val
        except Exception:
            # Best-effort; secrets remain whatever we could load
            pass
        # Minimal persistent key-value store (Replit DB-like)
        self.store: "AppStore" = AppStore(Path.cwd() / ".appui_store.json")

    def register_event_handler(
        self, node_id: str, event_name: str, handler: Callable[[Any], None]
    ) -> None:
        self._event_handlers[(node_id, event_name)] = handler

    def dispatch_event(self, node_id: str, event_name: str, value: Any = None) -> None:
        handler = self._event_handlers.get((node_id, event_name))
        if handler is not None:
            handler(value)

    def build_tree(self) -> UINode:
        token = _current_session.set(self)
        try:
            return self._builder(self)
        finally:
            _current_session.reset(token)


# Caching utilities (similar to Streamlit's cache_data/resource)
_cache_data_store: Dict[str, Tuple[float, Any]] = {}
_cache_resource_store: Dict[str, Tuple[float, Any]] = {}


def _make_cache_key(fn: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
    # Simple, robust key using repr; good enough for most cases
    try:
        args_repr = ",".join(repr(a) for a in args)
        kwargs_repr = ",".join(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
        return f"{fn.__module__}.{getattr(fn, '__qualname__', getattr(fn, '__name__', 'fn'))}({args_repr}){{{kwargs_repr}}}"
    except Exception:
        return f"{fn.__module__}.{getattr(fn, '__qualname__', getattr(fn, '__name__', 'fn'))}:{id(args)}:{id(tuple(sorted(kwargs.items())))}"


def cache_data(ttl: Optional[float] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Cache pure function results in-memory with optional TTL (seconds)."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _make_cache_key(fn, args, kwargs)
            now = time.time()
            hit = _cache_data_store.get(key)
            if hit is not None:
                ts, val = hit
                if ttl is None or (now - ts) < float(ttl):
                    return val
            result = fn(*args, **kwargs)
            _cache_data_store[key] = (now, result)
            return result

        return wrapper

    return decorator


def cache_resource(ttl: Optional[float] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Cache resource-like objects (e.g., models, connections) with optional TTL."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _make_cache_key(fn, args, kwargs)
            now = time.time()
            hit = _cache_resource_store.get(key)
            if hit is not None:
                ts, val = hit
                if ttl is None or (now - ts) < float(ttl):
                    return val
            result = fn(*args, **kwargs)
            _cache_resource_store[key] = (now, result)
            return result

        return wrapper

    return decorator


def clear_cache_data() -> None:
    _cache_data_store.clear()


def clear_cache_resource() -> None:
    _cache_resource_store.clear()


def clear_all_caches() -> None:
    clear_cache_data()
    clear_cache_resource()


class AppStore:
    def __init__(self, path: Path):
        self._path: Path = path
        self._cache: Dict[str, Any] = {}
        self._loaded: bool = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        try:
            if self._path.exists():
                self._cache = json.loads(self._path.read_text())
        except Exception:
            self._cache = {}
        finally:
            self._loaded = True

    def _flush(self) -> None:
        try:
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            tmp.write_text(json.dumps(self._cache))
            tmp.replace(self._path)
        except Exception:
            # Best-effort persistence
            pass

    def get(self, key: str, default: Any = None) -> Any:
        self._ensure_loaded()
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._ensure_loaded()
        self._cache[key] = value
        self._flush()

    def delete(self, key: str) -> None:
        self._ensure_loaded()
        if key in self._cache:
            del self._cache[key]
            self._flush()

    def all(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return dict(self._cache)


