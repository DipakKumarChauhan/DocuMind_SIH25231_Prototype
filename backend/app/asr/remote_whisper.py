# app/asr/remote_whisper.py
import requests
from app.config import settings


def transcribe_remote(audio_url: str) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }

    audio_bytes = requests.get(audio_url).content

    files = {
        "file": ("audio.mp3", audio_bytes),
        "model": (None, "whisper-1"),
        "response_format": (None, "verbose_json"),
    }

    response = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers=headers,
        files=files,
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()

    return {
        "transcript": data["text"],
        "segments": [
            {
                "text": seg["text"],
                "start": seg["start"],
                "end": seg["end"],
            }
            for seg in data.get("segments", [])
        ],
        "source": "remote",
    }
