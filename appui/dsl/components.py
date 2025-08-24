from __future__ import annotations

import uuid
from typing import Any, Callable, Iterable, Optional, Sequence
try:
    import pandas as _pd  # type: ignore
except Exception:  # pragma: no cover
    _pd = None  # type: ignore

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


def button(label: str, on_click: Optional[Callable[[], None]] = None, variant: str = "default") -> UINode:
    node = UINode(
        id=_new_id(),
        type="Button",
        props={"label": label, "variant": variant, "events": {"click": on_click is not None}},
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


def header(text_value: str, level: int = 2) -> UINode:
    return UINode(id=_new_id(), type="Header", props={"text": text_value, "level": level}, children=[])


def paragraph(text_value: str) -> UINode:
    return UINode(id=_new_id(), type="Paragraph", props={"text": text_value}, children=[])


def checkbox(checked: bool, label: str = "", on_change: Optional[Callable[[bool], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(), type="Checkbox", props={"checked": checked, "label": label, "events": {"change": on_change is not None}}, children=[]
    )
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(bool(v)))
    return node


def select(options: Sequence[str], value: Optional[str], on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(), type="Select", props={"options": list(options), "value": value, "events": {"change": on_change is not None}}, children=[]
    )
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


def tabs(tabs_list: Sequence[tuple[str, UINode]], active_index: int = 0, on_change: Optional[Callable[[int], None]] = None) -> UINode:
    tab_titles = [t for t, _ in tabs_list]
    children = [n for _, n in tabs_list]
    node = UINode(
        id=_new_id(),
        type="Tabs",
        props={"titles": tab_titles, "activeIndex": active_index, "events": {"change": on_change is not None}},
        children=children,
    )
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(int(v)))
    return node


def data_table(columns: Sequence[str] | Any, rows: Sequence[Sequence[Any]] | Any) -> UINode:
    # Accept pandas DataFrame for convenience
    if _pd is not None and isinstance(columns, _pd.DataFrame):  # type: ignore[arg-type]
        df = columns  # type: ignore[assignment]
        cols = [str(c) for c in list(df.columns)]
        rws = [[df.iloc[i, j] for j in range(len(cols))] for i in range(len(df))]
        return UINode(id=_new_id(), type="DataTable", props={"columns": cols, "rows": rws}, children=[])
    if _pd is not None and isinstance(rows, _pd.DataFrame):  # type: ignore[arg-type]
        df = rows  # type: ignore[assignment]
        cols = [str(c) for c in list(df.columns)]
        rws = [[df.iloc[i, j] for j in range(len(cols))] for i in range(len(df))]
        return UINode(id=_new_id(), type="DataTable", props={"columns": cols, "rows": rws}, children=[])
    return UINode(id=_new_id(), type="DataTable", props={"columns": list(columns), "rows": [list(r) for r in rows]}, children=[])


def markdown(md: str) -> UINode:
    return UINode(id=_new_id(), type="Markdown", props={"md": md}, children=[])


def file_upload(label: str = "Upload", multiple: bool = False, on_upload: Optional[Callable[[dict], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="FileUpload", props={"label": label, "multiple": multiple, "events": {"uploaded": on_upload is not None}}, children=[])
    if on_upload is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "uploaded", lambda v: on_upload(dict(v or {})))
    return node


def chart(options: dict[str, Any]) -> UINode:
    return UINode(id=_new_id(), type="Chart", props={"options": options}, children=[])


def card(children: Iterable[UINode], title: Optional[str] = None, actions: Optional[Iterable[UINode]] = None, footer: Optional[Iterable[UINode]] = None) -> UINode:
    return UINode(
        id=_new_id(),
        type="Card",
        props={
            "title": title,
            "actions": list(actions) if actions is not None else [],
            "footer": list(footer) if footer is not None else [],
        },
        children=list(children),
    )


def divider() -> UINode:
    return UINode(id=_new_id(), type="Divider", props={}, children=[])


def spacer(height: int = 8, width: Optional[int] = None) -> UINode:
    return UINode(id=_new_id(), type="Spacer", props={"height": height, "width": width}, children=[])


def grid(children: Iterable[UINode], columns: dict[str, int] | None = None, gap: int = 12) -> UINode:
    return UINode(
        id=_new_id(),
        type="Grid",
        props={"columns": columns or {"sm": 1, "md": 2, "lg": 3}, "gap": gap},
        children=list(children),
    )


def theme(children: Iterable[UINode] | UINode, mode: str = "light", density: str = "comfortable", brand: str = "blue", glass: bool = False) -> UINode:
    normalized_children: list[UINode]
    if isinstance(children, UINode):
        normalized_children = [children]
    else:
        normalized_children = list(children)
    return UINode(id=_new_id(), type="Theme", props={"mode": mode, "density": density, "brand": brand, "glass": glass}, children=normalized_children)


def columns(children: Iterable[UINode] | UINode, weights: Optional[Sequence[int]] = None, gap: int = 12) -> UINode:
    normalized_children: list[UINode]
    if isinstance(children, UINode):
        normalized_children = [children]
    else:
        normalized_children = list(children)
    return UINode(id=_new_id(), type="Columns", props={"weights": list(weights) if weights is not None else None, "gap": gap}, children=normalized_children)


# App shell and navigation
def app_shell(sidebar: UINode, header: Optional[UINode], content: UINode, collapsed: bool = False, on_toggle: Optional[Callable[[bool], None]] = None, route: Optional[str] = None) -> UINode:
    # Always provide three children for the renderer: [sidebar, header, content]
    # If header is None, use an empty placeholder so content is the third child.
    children: list[UINode] = [sidebar, header if header is not None else text("")]
    children.append(content)
    node = UINode(id=_new_id(), type="AppShell", props={"collapsed": collapsed, "route": route, "events": {"toggle": on_toggle is not None}}, children=children)
    if on_toggle is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "toggle", lambda v: on_toggle(bool(v)))
    return node


def nav_link(text_value: str, path: str, active: bool = False, icon: Optional[str] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="NavLink",
        props={"text": text_value, "path": path, "active": active, "icon": icon, "events": {"navigate": True}},
        children=[],
    )
    session = get_current_session()
    if session is not None:
        session.register_event_handler(node.id, "navigate", lambda v: session.vars.__setitem__("path", str(v or path)))
    return node


def nav_section(title: str) -> UINode:
    return UINode(id=_new_id(), type="NavSection", props={"title": title}, children=[])


# Chat
def chat(messages: list[dict[str, Any]], on_send: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="Chat",
        props={"messages": messages, "events": {"send": on_send is not None}},
        children=[],
    )
    if on_send is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "send", lambda v: on_send(str(v)))
    return node


def kpi(title: str, value: str, trend: Optional[str] = None) -> UINode:
    return UINode(id=_new_id(), type="KPI", props={"title": title, "value": value, "trend": trend}, children=[])


# Parity widgets
def slider(value: float, minimum: float = 0.0, maximum: float = 100.0, step: float = 1.0, on_change: Optional[Callable[[float], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="Slider",
        props={"value": value, "min": minimum, "max": maximum, "step": step, "events": {"change": on_change is not None}},
        children=[],
    )
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(float(v)))
    return node


def textarea(value: str, placeholder: str = "", rows: int = 3, on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="TextArea", props={"value": value, "placeholder": placeholder, "rows": rows, "events": {"change": on_change is not None}}, children=[])
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


def radio(options: Sequence[str], value: Optional[str] = None, on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="Radio", props={"options": list(options), "value": value, "events": {"change": on_change is not None}}, children=[])
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


def multiselect(options: Sequence[str], values: Sequence[str], on_change: Optional[Callable[[list[str]], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="MultiSelect", props={"options": list(options), "values": list(values), "events": {"change": on_change is not None}}, children=[])
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change([str(x) for x in (v or [])]))
    return node


def date_input(value: str, on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="DateInput", props={"value": value, "events": {"change": on_change is not None}}, children=[])
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


def time_input(value: str, on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="TimeInput", props={"value": value, "events": {"change": on_change is not None}}, children=[])
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


def image(src: str, alt: str = "", width: Optional[int] = None, height: Optional[int] = None) -> UINode:
    return UINode(id=_new_id(), type="Image", props={"src": src, "alt": alt, "width": width, "height": height}, children=[])


def code(content: str, language: Optional[str] = None) -> UINode:
    return UINode(id=_new_id(), type="Code", props={"content": content, "language": language}, children=[])


def json_view(data: Any) -> UINode:
    return UINode(id=_new_id(), type="Json", props={"data": data}, children=[])


def progress(value: float) -> UINode:
    return UINode(id=_new_id(), type="Progress", props={"value": float(value)}, children=[])


def expander(title: str, open: bool, content: Iterable[UINode] | UINode, on_toggle: Optional[Callable[[bool], None]] = None) -> UINode:
    children = [content] if isinstance(content, UINode) else list(content)
    node = UINode(id=_new_id(), type="Expander", props={"title": title, "open": open, "events": {"toggle": on_toggle is not None}}, children=children)
    if on_toggle is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "toggle", lambda v: on_toggle(bool(v)))
    return node


def modal(content: Iterable[UINode] | UINode, open: bool, title: Optional[str] = None, on_close: Optional[Callable[[], None]] = None) -> UINode:
    children = [content] if isinstance(content, UINode) else list(content)
    node = UINode(id=_new_id(), type="Modal", props={"open": open, "title": title, "events": {"close": on_close is not None}}, children=children)
    if on_close is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "close", lambda _v=None: on_close())
    return node


def data_editor(columns: Sequence[str], rows: Sequence[Sequence[Any]], on_cell_change: Optional[Callable[[dict], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="DataEditor",
        props={
            "columns": list(columns),
            "rows": [list(r) for r in rows],
            "events": {"cell": on_cell_change is not None},
        },
        children=[],
    )
    if on_cell_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "cell", lambda v: on_cell_change(dict(v or {})))
    return node


def download_button(label: str, filename: str, content: str, mime: str = "text/plain") -> UINode:
    return UINode(id=_new_id(), type="Download", props={"label": label, "filename": filename, "content": content, "mime": mime}, children=[])


def alert(message: str, kind: str = "info") -> UINode:
    return UINode(id=_new_id(), type="Alert", props={"message": message, "kind": kind}, children=[])


def spinner(label: Optional[str] = None) -> UINode:
    return UINode(id=_new_id(), type="Spinner", props={"label": label}, children=[])


def toast(message: str, kind: str = "info") -> UINode:
    # Non-blocking UI hint; renderer may position it globally
    return UINode(id=_new_id(), type="Toast", props={"message": message, "kind": kind}, children=[])


def audio(src: str, controls: bool = True, autoplay: bool = False) -> UINode:
    return UINode(id=_new_id(), type="Audio", props={"src": src, "controls": controls, "autoplay": autoplay}, children=[])


def video(src: str, controls: bool = True, autoplay: bool = False) -> UINode:
    return UINode(id=_new_id(), type="Video", props={"src": src, "controls": controls, "autoplay": autoplay}, children=[])


def form(children: Iterable[UINode] | UINode, on_submit: Optional[Callable[[], None]] = None) -> UINode:
    normalized = [children] if isinstance(children, UINode) else list(children)
    node = UINode(id=_new_id(), type="Form", props={"events": {"submit": on_submit is not None}}, children=normalized)
    if on_submit is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "submit", lambda _v=None: on_submit())
    return node


def color_picker(value: str, on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="Color", props={"value": value, "events": {"change": on_change is not None}}, children=[])
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


def range_slider(min_value: float, max_value: float, minimum: float = 0.0, maximum: float = 100.0, step: float = 1.0, on_change: Optional[Callable[[tuple[float, float]], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="RangeSlider",
        props={"minValue": min_value, "maxValue": max_value, "min": minimum, "max": maximum, "step": step, "events": {"change": on_change is not None}},
        children=[],
    )
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change((float(v.get("min")), float(v.get("max")))))
    return node


def datetime_input(value: str, on_change: Optional[Callable[[str], None]] = None) -> UINode:
    node = UINode(id=_new_id(), type="DateTime", props={"value": value, "events": {"change": on_change is not None}}, children=[])
    if on_change is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "change", lambda v: on_change(str(v)))
    return node


# Command palette
def command_palette(items: Sequence[dict[str, Any]], on_run: Optional[Callable[[dict], None]] = None) -> UINode:
    node = UINode(
        id=_new_id(),
        type="CommandPalette",
        props={"items": list(items), "events": {"run": on_run is not None}},
        children=[],
    )
    if on_run is not None:
        session = get_current_session()
        if session is not None:
            session.register_event_handler(node.id, "run", lambda v: on_run(dict(v or {})))
    return node

