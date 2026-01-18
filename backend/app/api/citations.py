from fastapi import APIRouter, HTTPException, Depends
from app.chat.session_store import _CHAT_SESSIONS
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/citations", tags=["Citations"])


@router.get("/{session_id}/{citation_id}")
def resolve_citation(
    session_id: str, 
    citation_id: int,
    current_user = Depends(get_current_user),
):
    session = _CHAT_SESSIONS.get(session_id)

    if not session:
        raise HTTPException(404, "Session not found")
    
    if session["owner_id"] != current_user.id:
       raise HTTPException(status_code=403, detail="Forbidden")
    

    citations = session.get("citations", [])

    for c in citations:
        if c["id"] == citation_id:
            return c

    raise HTTPException(404, "Citation not found")
