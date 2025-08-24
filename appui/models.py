from __future__ import annotations

import uuid
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class UINode(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    type: str
    props: Dict[str, Any] = Field(default_factory=dict)
    children: List["UINode"] = Field(default_factory=list)


