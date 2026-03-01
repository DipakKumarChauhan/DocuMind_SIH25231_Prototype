from pydantic import BaseModel
from typing import List, Optional, Any, Union


# ============================================================
# CHAT REQUEST SCHEMAS
# ============================================================

class ChatRequest(BaseModel):
    """
    Chat endpoint request body.
    At least one of: message, image, or audio must be provided.
    """
    message: Optional[str] = None
    session_id: Optional[str] = None
    # image and audio are form-data files, not in schema
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What does this image show?",
                "session_id": "session-123"
            }
        }


# ============================================================
# AUDIO SEGMENT SCHEMA
# ============================================================

class AudioSegment(BaseModel):
    """
    A segment of audio transcript with timestamps.
    
    Fields:
    - text: Transcript text for this segment
    - start: Start time in seconds
    - end: End time in seconds
    """
    text: str
    start: float
    end: float


# ============================================================
# CITATION SCHEMAS
# ============================================================

class Citation(BaseModel):
    """
    A single citation/reference in the chat response.
    
    Fields:
    - id: Reference ID [1], [2], etc. in the answer
    - modality: "text", "image", or "audio"
    - file_id: Filename or URL depending on modality
    - page: Page number (for PDFs, None for others)
    - timestamp: Audio segments (list) or float, or None
    """
    id: int
    modality: str  # "text" | "image" | "audio"
    file_id: Optional[str] = None
    page: Optional[int] = None
    timestamp: Optional[Union[List[AudioSegment], float]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "modality": "text",
                "file_id": "document.pdf",
                "page": 3,
                "timestamp": None
            }
        }


# ============================================================
# CHAT RESPONSE SCHEMAS
# ============================================================

class ChatResponse(BaseModel):
    """
    Chat endpoint response.
    
    Fields:
    - session_id: ID to reuse for multi-turn conversation
    - answer: LLM-generated answer with optional citations [1], [2], etc.
    - citations: List of referenced sources; maps [1] in answer to actual file/page/etc.
    """
    session_id: str
    answer: str
    citations: List[Citation] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123",
                "answer": "The image [1] shows a sunset. According to the document [2] on page 3, sunsets occur due to Rayleigh scattering.",
                "citations": [
                    {"id": 1, "modality": "image", "file_id": "sunset.jpg", "page": None, "timestamp": None},
                    {"id": 2, "modality": "text", "file_id": "physics.pdf", "page": 3, "timestamp": None}
                ]
            }
        }


class EndSessionResponse(BaseModel):
    """
    Response for ending a chat session.
    """
    status: str  # "success"
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Session session-123 ended and cleaned up"
            }
        }


# ============================================================
# LEGACY REQUEST SCHEMAS
# ============================================================

class AskRequest(BaseModel):
    query: str
    owner_id: str
    