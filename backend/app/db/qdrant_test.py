from qdrant_client import QdrantClient
from app.config import settings

def test_qdrant_connection():
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key = settings.QDRANT_API_KEY
    )
    collections =  client.get_collections()
    print("✅ Qdrant connected successfully")
    print("Collections:", [c.name for c in collections.collections])

if __name__ == "__main__":
    test_qdrant_connection()
    