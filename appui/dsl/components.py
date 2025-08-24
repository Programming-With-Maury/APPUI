from __future__ import annotations

import uuid
from typing import Any, Callable, Iterable, Optional

from ..runtime import get_current_session
from ..models import UINode


def _new_id() -> str:
    return uuid.uuid4().hex


def text(content: str) -> UINode:
    return UINode(id=_new_id(), type="Text", props={"text": content}, children=[])


def vstack(children: Iterable[UINode], gap: int = 8, align: str = "start", justify: str = "start") -> UINode:
    return UINode(
        id=_new_id(),
        type="VStack",
        props={"gap": gap, "align": align, "justify": justify},
        children=list(children),
    )


def hstack(children: Iterable[UINode], gap: int = 8, align: str = "center", justify: str = "start") -> UINode:
    return UINode(
        id=_new_id(),
        type="HStack",
        props={"gap": gap, "align": align, "justify": justify},
        children=list(children),
    )


def button(label: str, on_click: Optional[Callable[[], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="Button",
        props={"label": label, "events": {"click": on_click is not None}},
        children=[],
    )
    if on_click is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "click", lambda _v=None: on_click())
    return node


def input_text(value: str, placeholder: str = "", on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="InputText",
        props={"value": value, "placeholder": placeholder, "events": {"change": on_change is not None}},
        children=[],
    )
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


def number_input(value: float, step: float = 1.0, on_change: Optional[Callable[[float], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="NumberInput",
        props={"value": value, "step": step, "events": {"change": on_change is not None}},
        children=[],
    )
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(float(v)))
    return node


