import uuid
from datetime import datetime
from qdrant_client.models import PointStruct
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder

AUDIO_COLLECTION = "audio_collection"
_embedder = None

def _get_embedder() :
    global _embedder
    if _embedder is None:
        _embedder = HFBgeM3Embedder()
    return _embedder

def index_audio(
        audio_url:str,
        owner_id:str,
        file_id:str,
        transcript:str,
        timestamps:list | None = None,
):
    if not transcript or len(transcript.strip()) <10:
        return
    
    embedder = _get_embedder()
    vector  = embedder.embed_query(transcript)

    point = PointStruct(
        id= str(uuid.uuid4()),
        vector= {"transcript": vector},
        payload= {
            "owner_id": owner_id,
            "audio_url": audio_url,
            "file_id": file_id,
            "transcript": transcript,
            "timestamps": timestamps,
            "source": "audio",
            "created_at": datetime.utcnow().isoformat(),
        },
    )

    client = get_qdrant_client()
    client.upsert(AUDIO_COLLECTION, [point])


