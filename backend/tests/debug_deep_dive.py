#!/usr/bin/env python3
"""
Deep dive debug - check embedding and query
"""

import sys
sys.path.insert(0, '/home/dipak/SIH-25321_MVP/backend')

from app.asr.orchestrator import transcribe_audio
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.db.qdrant_client import get_qdrant_client
from qdrant_client.models import Filter, FieldCondition, MatchValue

audio_url = "https://res.cloudinary.com/du3jktmzs/video/upload/v1768408831/sih/audio/temp/1584bf98-0ebb-4bff-b0ad-3d09f2f8043c/e6b1adda-2fbd-430a-b935-5c5c08f3ddff.3gp"
owner_id = "1584bf98-0ebb-4bff-b0ad-3d09f2f8043c"

print("Step-by-step debug:")
print("=" * 70)

# Step 1: Transcribe
print("\n1. Transcribing...")
result_dict = transcribe_audio(audio_url)
transcript = result_dict.get("transcript", "")
print(f"   Transcript ({len(transcript)} chars): {transcript[:200]}...")

if not transcript or len(transcript.strip()) < 5:
    print("   ✗ Transcript too short, exiting")
    sys.exit(1)

# Step 2: Embed
print("\n2. Embedding transcript...")
embedder = HFBgeM3Embedder()
text_vec = embedder.embed_query(transcript)
print(f"   Vector dimension: {len(text_vec)}")
print(f"   Vector first 5 values: {text_vec[:5]}")

# Step 3: Query WITHOUT filter (to see if any results exist)
print("\n3. Querying image collection (NO owner filter)...")
client = get_qdrant_client()

try:
    result_no_filter = client.query_points(
        collection_name="image_collection",
        query=text_vec,
        using="ocr",
        limit=5,
        with_payload=True,
    )
    
    print(f"   Without filter: {len(result_no_filter.points)} results")
    if result_no_filter.points:
        for p in result_no_filter.points:
            print(f"   - Score: {p.score:.4f}, Owner: {p.payload.get('owner_id', 'N/A')}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Query WITH filter
print(f"\n4. Querying with owner_id filter: {owner_id}...")
try:
    result_with_filter = client.query_points(
        collection_name="image_collection",
        query=text_vec,
        using="ocr",
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="owner_id",
                    match=MatchValue(value=owner_id),
                )
            ]
        ),
        limit=5,
        with_payload=True,
    )
    
    print(f"   With filter: {len(result_with_filter.points)} results")
    if result_with_filter.points:
        for p in result_with_filter.points:
            print(f"   - Score: {p.score:.4f}")
            print(f"     OCR: {p.payload.get('ocr_text', '')[:80]}...")
    else:
        print("   ⚠️ No results! Possible reasons:")
        print("      - Images don't have 'ocr' vector")
        print("      - Semantic mismatch")
        print("      - Wrong collection structure")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
