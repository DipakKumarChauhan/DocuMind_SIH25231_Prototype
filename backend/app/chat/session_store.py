import uuid
from app.chat.cleanup import cleanup_temp_assets

_CHAT_SESSIONS = {}

MAX_TURNS = 7

def get_session(
        owner_id: str,
        session_id: str | None,
):
    """
    Retrieve an existing chat session or create a new one.
    
    If session_id is provided but a different session exists, clean up old session first.
    
    Returns a tuple of (session_id, session_dict) so callers can persist the ID.
    """
    if session_id and session_id in _CHAT_SESSIONS:
        return session_id, _CHAT_SESSIONS[session_id]

    # New session requested → create fresh one
    session_id = session_id or str(uuid.uuid4())
    _CHAT_SESSIONS[session_id] = {
        "owner_id": owner_id,
        "history": [],
        "citations": [],
        "temp_assets": {
            "images": [],
            "audio": [],
        }
    }

    return session_id, _CHAT_SESSIONS[session_id]


def cleanup_session(session_id: str):
    """
    Explicitly cleanup a session's temporary assets and remove from memory.
    
    Called when user ends chat or starts a new conversation.
    
    Args:
        session_id: Session ID to cleanup
    """
    if session_id in _CHAT_SESSIONS:
        session = _CHAT_SESSIONS[session_id]
        cleanup_temp_assets(session)
        del _CHAT_SESSIONS[session_id]
        print(f"[INFO] Session {session_id} cleaned up and removed")