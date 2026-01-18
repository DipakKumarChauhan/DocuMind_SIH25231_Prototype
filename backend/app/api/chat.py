from fastapi import APIRouter, Depends,UploadFile, File,HTTPException,Form
from typing import List,Dict
from app.auth.dependencies import get_current_user
from app.chat.session_store import get_session, cleanup_session
from app.chat.chat_orchestrator import run_chat_turn

router = APIRouter()

@router.post("/api/chat")
async def chat(
    message: str | None = Form(None),
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    session_id: str | None = Form(None),
    user = Depends(get_current_user),
):
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


@router.post("/api/chat/end")
async def end_chat(
    session_id: str = Form(...),
    user = Depends(get_current_user),
):
    """
    End chat session and cleanup temporary assets.
    
    This deletes all temporary images/audio uploaded during the chat session
    from Cloudinary and clears session memory.
    
    Args:
        session_id: Chat session ID to end
        
    Returns:
        Confirmation message
    """
    try:
        cleanup_session(session_id)
        return {
            "status": "success",
            "message": f"Session {session_id} ended and cleaned up",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup session: {str(e)}"
        )

