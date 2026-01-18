from app.retrieval.text_retriever import retrieve_text_chunks
from app.retrieval.image_retriever import retrieve_images_from_text, retrieve_image_from_image
from app.retrieval.text_to_audio_retriever import retrieve_audio_from_text
from app.retrieval.audio_to_text_retriever import retrieve_text_from_audio
from app.retrieval.image_to_text_retriever import retrieve_text_from_image
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder

def route_query(q):
    results = {}
    
    # Initialize embedder for text operations
    embedder = HFBgeM3Embedder()

    if q['text']:
        results['text'] = retrieve_text_chunks(q['text'], q['owner_id'], embedder)
        results['image'] = retrieve_images_from_text(q['text'], q['owner_id'])
        results['audio'] = retrieve_audio_from_text(q['text'], q['owner_id'])

    if q.get('image_url'):
        print(f"[DEBUG] Processing image_url: {q['image_url']}")
        results['image_text'] = retrieve_text_from_image(q['image_url'], q['owner_id'])
        print(f"[DEBUG] image_text results: {len(results.get('image_text', []))} items")

    if q.get('audio_url'):
        print(f"[DEBUG] Processing audio_url: {q['audio_url']}")
        results['audio_text'] = retrieve_text_from_audio(q['audio_url'], q['owner_id'])
        print(f"[DEBUG] audio_text results: {len(results.get('audio_text', []))} items")

    print(f"[DEBUG] Final route_query results keys: {results.keys()}")
    return results
 