#!/usr/bin/env python3
"""
Proper way to test audio_to_text retrieval in an interactive session.

This ensures all modules are freshly loaded.
"""

import sys
import importlib

# Clear any cached imports
if 'app' in sys.modules:
    # Remove all app.* modules from cache
    to_remove = [key for key in sys.modules.keys() if key.startswith('app.')]
    for key in to_remove:
        del sys.modules[key]

# Add backend to path if not already there
backend_path = '/home/dipak/SIH-25321_MVP/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Now import (will be fresh)
from app.retrieval.audio_to_text_retriever import retrieve_text_from_audio

print("Module loaded successfully. You can now call:")
print()
print("results = retrieve_text_from_audio(")
print("    audio_url='https://res.cloudinary.com/du3jktmzs/video/upload/v1768392217/sih/audio/dataset/1584bf98-0ebb-4bff-b0ad-3d09f2f8043c/df7c2230-a8c4-4f26-937a-4d63c3715222.3gp',")
print("    owner_id='1584bf98-0ebb-4bff-b0ad-3d09f2f8043c',")
print("    top_k=3")
print(")")
print()
print("Or test now:")

# Run test
try:
    results = retrieve_text_from_audio(
        audio_url="https://res.cloudinary.com/du3jktmzs/video/upload/v1768392217/sih/audio/dataset/1584bf98-0ebb-4bff-b0ad-3d09f2f8043c/df7c2230-a8c4-4f26-937a-4d63c3715222.3gp",
        owner_id="1584bf98-0ebb-4bff-b0ad-3d09f2f8043c",
        top_k=3
    )
    
    print(f"\n✓ Success! Retrieved {len(results)} text documents:")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['filename']} (page {r['page']}) - Score: {r['score']:.4f}")
        print(f"   {r['text'][:80]}...")
        
except Exception as e:
    import traceback
    print(f"\n✗ Error occurred:")
    traceback.print_exc()
