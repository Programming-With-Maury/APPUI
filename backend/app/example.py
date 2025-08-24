from __future__ import annotations

from typing import cast

from .app_runtime import Session
from .dsl import button, hstack, input_text, number_input, text, vstack
from .models import UINode


def build_ui(session: Session) -> UINode:
    name = cast(str, session.vars.get("name", "World"))
    count = cast(float, session.vars.get("count", 0))

    def on_name_change(new_value: str) -> None:
        session.vars["name"] = new_value

    def on_inc() -> None:
        session.vars["count"] = count + 1

    def on_dec() -> None:
        session.vars["count"] = count - 1

    return vstack(
        [
            text(f"Hello, {name}!"),
            input_text(value=name, placeholder="Enter your name", on_change=on_name_change),
            hstack(
                [
                    button("-", on_click=on_dec),
                    text(f"Count: {int(count)}"),
                    button("+", on_click=on_inc),
                ],
                gap=12,
                align="center",
            ),
            number_input(value=count, step=1.0, on_change=lambda v: session.vars.__setitem__("count", v)),
        ],
        gap=12,
    )


