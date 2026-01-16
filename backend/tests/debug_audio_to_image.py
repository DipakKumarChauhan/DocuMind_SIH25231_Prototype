#!/usr/bin/env python3
"""
Debug script to test audio_to_image retrieval
"""

import sys
sys.path.insert(0, '/home/dipak/SIH-25321_MVP/backend')

from app.asr.orchestrator import transcribe_audio
from app.retrieval.audio_to_image_retriever import retrieve_image_from_audio

# Test audio URL from the request
audio_url = "https://res.cloudinary.com/du3jktmzs/video/upload/v1768408831/sih/audio/temp/1584bf98-0ebb-4bff-b0ad-3d09f2f8043c/e6b1adda-2fbd-430a-b935-5c5c08f3ddff.3gp"
owner_id = "1584bf98-0ebb-4bff-b0ad-3d09f2f8043c"

print("=" * 70)
print("DEBUGGING AUDIO TO IMAGE SEARCH")
print("=" * 70)

# Step 1: Check transcription
print("\n1. Transcribing audio...")
try:
    result = transcribe_audio(audio_url)
    transcript = result.get("transcript", "")
    print(f"   ✓ Transcription successful")
    print(f"   Transcript: '{transcript}'")
    print(f"   Length: {len(transcript)} chars")
    
    if not transcript or len(transcript.strip()) < 5:
        print(f"   ⚠️ Transcript too short! (minimum 5 chars)")
except Exception as e:
    print(f"   ✗ Transcription failed: {e}")
    sys.exit(1)

# Step 2: Try retrieval without filtering
print("\n2. Retrieving images (no filtering)...")
try:
    results = retrieve_image_from_audio(
        audio_url=audio_url,
        owner_id=owner_id,
        top_k=10
    )
    print(f"   ✓ Retrieved {len(results)} results")
    
    if results:
        print("\n   Results (sorted by score):")
        for i, r in enumerate(results, 1):
            print(f"   {i}. Score: {r['score']:.4f} - {r['filename']} (page {r['page']})")
            print(f"      Text preview: {r['text'][:80]}...")
    else:
        print("   ⚠️ No results found!")
        
except Exception as e:
    import traceback
    print(f"   ✗ Retrieval failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Check filtering
print("\n3. Checking score filtering...")
MIN_SCORE = 0.28
filtered = [r for r in results if r["score"] >= MIN_SCORE]
print(f"   MIN_SCORE threshold: {MIN_SCORE}")
print(f"   Results after filtering: {len(filtered)}")

if len(results) > 0 and len(filtered) == 0:
    print(f"   ⚠️ All results filtered out! Highest score: {results[0]['score']:.4f}")
    print(f"   ⚠️ Consider lowering MIN_SCORE threshold")

# Step 4: Check if any images exist for this owner
print("\n4. Checking image collection...")
from app.db.qdrant_client import get_qdrant_client
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = get_qdrant_client()
try:
    # Check total images for this owner
    scroll_result = client.scroll(
        collection_name="image_collection",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="owner_id",
                    match=MatchValue(value=owner_id),
                )
            ]
        ),
        limit=1,
        with_payload=True,
    )
    
    if scroll_result[0]:
        print(f"   ✓ Images exist for owner_id: {owner_id}")
        sample = scroll_result[0][0]
        print(f"   Sample image: {sample.payload.get('filename', 'N/A')}")
        ocr_text = sample.payload.get('ocr_text', '')
        print(f"   Sample OCR text: {ocr_text[:100]}...")
    else:
        print(f"   ✗ NO images found for owner_id: {owner_id}")
        print(f"   ⚠️ You need to upload and index images first!")
        
except Exception as e:
    print(f"   ✗ Error checking collection: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
