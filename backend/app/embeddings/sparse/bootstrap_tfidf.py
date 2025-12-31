from app.embeddings.sparse.tfidf import TfidfSparseEncoder
from app.db.qdrant_client import get_qdrant_client

def bootstrap_tfidf_from_existing_chunks(chunks):
    texts = [c["text"] for c in chunks]
    tfidf = TfidfSparseEncoder()
    tfidf.fit(texts)
    print("TF-IDF vocabulary initialized")

# Run ONCE before indexing
