import whisper
import tempfile
import requests 
import os
from app.config import settings

_model = None

def _get_model():
    global _model
    if _model is None:
        # Store/download Whisper models under central cache dir
        whisper_cache = os.path.join(settings.MODEL_CACHE_DIR, "whisper")
        os.makedirs(whisper_cache, exist_ok=True)
        _model = whisper.load_model("base", download_root=whisper_cache)
    return _model

def transcribe_local(audio_url:str) ->dict:

    audio_bytes = requests.get(audio_url).content

    with tempfile.NamedTemporaryFile(suffix = ".mp3") as f: # Note this line does not mean that only mp3 files are supported
        f.write(audio_bytes)
        f.flush()
        model = _get_model()
        result = model.transcribe(f.name)

    return {

        "transcript": result["text"],
        "segments": [
            {
                "text": seg["text"],
                "start": seg["start"],
                "end": seg["end"],
            }
            for seg in result.get("segments",[])
        ],
        "source": "local_whisper",
    }

