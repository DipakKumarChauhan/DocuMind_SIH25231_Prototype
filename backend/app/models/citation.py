# app/models/citation.py
from typing import Optional
from pydantic import BaseModel

class Citation(BaseModel):
    citation_id: int
    source_type: str           # text | image | audio
    file_id: str
    filename: Optional[str] = None
    page: Optional[int] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    timestamp: Optional[float] = None
    snippet: Optional[str] = None
