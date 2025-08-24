from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any, Callable, Dict, Optional, Tuple

from .models import UINode


_current_session: ContextVar["Session"] = ContextVar("current_session")


def get_current_session() -> Optional["Session"]:
    try:
        return _current_session.get()
    except LookupError:
        return None


class Session:
    """Per-websocket session holding state and event handlers."""

    def __init__(self, builder: Callable[["Session"], UINode]):
        self.id: str = uuid.uuid4().hex
        self.vars: Dict[str, Any] = {}
        self._event_handlers: Dict[Tuple[str, str], Callable[[Any], None]] = {}
        self._builder: Callable[["Session"], UINode] = builder

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


