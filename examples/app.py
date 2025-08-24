from __future__ import annotations

from typing import Any, cast

from appui.runtime import Session
from appui.models import UINode
from appui.dsl import vstack, chat


def build_ui(session: Session) -> UINode:
    messages = cast(list[dict[str, Any]], session.vars.get("messages", [
        {"role": "assistant", "content": "Hi! I'm Echo. Type something."}
    ]))

    def on_send(text_value: str) -> None:
        session.vars["messages"] = messages + [
            {"role": "user", "content": text_value},
            {"role": "assistant", "content": text_value},
        ]

    return vstack([
        chat(messages=messages, on_send=on_send)
    ], gap=12)


