#!/usr/bin/env python3
"""
Debug script to test audio_to_text retrieval
"""

import sys
sys.path.insert(0, '/home/dipak/SIH-25321_MVP/backend')

from app.retrieval.audio_to_text_retriever import retrieve_text_from_audio

# Test the function
print("Testing retrieve_text_from_audio...")

try:
    results = retrieve_text_from_audio(
        audio_url="https://res.cloudinary.com/du3jktmzs/video/upload/v1768392217/sih/audio/dataset/1584bf98-0ebb-4bff-b0ad-3d09f2f8043c/df7c2230-a8c4-4f26-937a-4d63c3715222.3gp",
        owner_id="1584bf98-0ebb-4bff-b0ad-3d09f2f8043c",
        top_k=3,
    )
    print(f"\nSuccess! Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['filename']} (page {result['page']})")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Text: {result['text'][:100]}...")
        
except Exception as e:
    import traceback
    print(f"\nError: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
