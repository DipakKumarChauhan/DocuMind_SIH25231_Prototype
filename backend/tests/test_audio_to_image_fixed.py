#!/usr/bin/env python3
"""
Test audio_to_image retrieval after fix
"""

import sys
sys.path.insert(0, '/home/dipak/SIH-25321_MVP/backend')

from app.retrieval.audio_to_image_retriever import retrieve_image_from_audio

audio_url = "https://res.cloudinary.com/du3jktmzs/video/upload/v1768408831/sih/audio/temp/1584bf98-0ebb-4bff-b0ad-3d09f2f8043c/e6b1adda-2fbd-430a-b935-5c5c08f3ddff.3gp"
owner_id = "1584bf98-0ebb-4bff-b0ad-3d09f2f8043c"

print("Testing audio_to_image retrieval...")
print("=" * 70)

try:
    results = retrieve_image_from_audio(
        audio_url=audio_url,
        owner_id=owner_id,
        top_k=5
    )
    
    print(f"\n✓ Success! Retrieved {len(results)} images")
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. Score: {r['score']:.4f}")
        print(f"   Image: {r['image_url']}")
        print(f"   File ID: {r['file_id']}")
        print(f"   OCR Text: {r['text'][:100]}...")
        
    # Test filtering
    MIN_SCORE = 0.28
    filtered = [r for r in results if r["score"] >= MIN_SCORE]
    print(f"\nAfter MIN_SCORE={MIN_SCORE} filtering: {len(filtered)} results")
    
except Exception as e:
    import traceback
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
