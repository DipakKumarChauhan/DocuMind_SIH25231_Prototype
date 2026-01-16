from app.config import settings
from app.asr.local_whisper import transcribe_local
from app.asr.remote_whisper import transcribe_remote    

def transcribe_audio(audio_url: str) -> dict:
        """
    Unified ASR entrypoint.

    Returns:
    {
      transcript: str,
      segments: [{text, start, end}],
      source: "remote" | "local"
    }
    """
        
        mode =  settings.ASR_MODE
        has_remote_key =  bool(settings.ASR_REMOTE_API_KEY)

        # Remote ASR
        if mode in ["auto", "remote"] and has_remote_key:
            try:
                return transcribe_remote(audio_url)
            except Exception as e:
                if mode == "remote":
                    raise RuntimeError(f"Remote ASR failed: {e}")
                
        # Fallback to local
        return transcribe_local(audio_url)



