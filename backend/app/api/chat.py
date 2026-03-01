from fastapi import APIRouter, Depends,UploadFile, File,HTTPException,Form
from typing import List,Dict, Optional
from app.auth.dependencies import get_current_user
from app.chat.session_store import get_session, cleanup_session
from app.chat.chat_orchestrator import run_chat_turn
from app.schemas.api import ChatResponse, EndSessionResponse

router = APIRouter()

@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    message: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    session_id: Optional[str] = Form(None),
    user = Depends(get_current_user),
) -> ChatResponse:
    """
    Chat with multimodal input (text, image, audio).
    
    At least one of: message, image, or audio must be provided.
    
    Args:
        message: Text query
        image: Image file (PNG, JPEG, GIF, WebP)
        audio: Audio file (MP3, WAV, M4A, etc.)
        session_id: Optional session ID for multi-turn chat
        user: Authenticated user
        
    Returns:
        ChatResponse with answer and citations
        
    Raises:
        HTTPException 400: No input provided
        HTTPException 413: File too large
        HTTPException 415: Unsupported file type
    """
    if not message and not image and not audio:
        raise HTTPException(status_code=400, detail="At least one of message, image, or audio must be provided.")
    
    response = await run_chat_turn(
        owner_id=user.id,
        session_id=session_id,
        message=message,
        image=image,
        audio=audio,
    )

    return response


@router.post("/api/chat/end", response_model=EndSessionResponse)
async def end_chat(
    session_id: str = Form(...),
    user = Depends(get_current_user),
) -> EndSessionResponse:
    """
    End chat session and cleanup temporary assets.
    
    This deletes all temporary images/audio uploaded during the chat session
    from Cloudinary and clears session memory.
    
    Args:
        session_id: Chat session ID to end
        user: Authenticated user
        
    Returns:
        EndSessionResponse with success confirmation
        
    Raises:
        HTTPException 500: Session cleanup failed
    """
    try:
        cleanup_session(session_id)
        return EndSessionResponse(
            status="success",
            message=f"Session {session_id} ended and cleaned up",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup session: {str(e)}"
        )

