from __future__ import annotations

from pydantic import BaseModel


class UploadResponse(BaseModel):
    storage_key: str
    url: str
    local_path: str
    filename: str
