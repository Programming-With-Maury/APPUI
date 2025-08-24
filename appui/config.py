from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class AppUIConfig(BaseModel):
    """Runtime configuration for the APPUI server."""

    title: str = "APPUI"
    allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])

    mount_static: bool = True
    static_dir: Optional[Path] = None
    root_path: str = "/"

    # Uploads
    enable_uploads: bool = True
    upload_dir: Path = Path("/tmp/appui-uploads")
    max_upload_size_mb: int = 50


