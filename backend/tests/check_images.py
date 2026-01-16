#!/usr/bin/env python3
"""
Quick check: Do images exist for this owner?
"""

import sys
sys.path.insert(0, '/home/dipak/SIH-25321_MVP/backend')

from app.db.qdrant_client import get_qdrant_client
from qdrant_client.models import Filter, FieldCondition, MatchValue

owner_id = "1584bf98-0ebb-4bff-b0ad-3d09f2f8043c"

print("Checking image collection for owner:", owner_id)

client = get_qdrant_client()

try:
    # Count total points in collection
    collection_info = client.get_collection("image_collection")
    print(f"\nTotal images in collection: {collection_info.points_count}")
    
    # Check images for this specific owner
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
        limit=5,
        with_payload=True,
    )
    
    points = scroll_result[0]
    
    if points:
        print(f"\n✓ Found {len(points)} images for owner {owner_id}:")
        for i, p in enumerate(points, 1):
            filename = p.payload.get('filename', 'N/A')
            page = p.payload.get('page', 'N/A')
            ocr_text = p.payload.get('ocr_text', '')[:100]
            print(f"\n{i}. {filename} (page {page})")
            print(f"   OCR: {ocr_text}...")
    else:
        print(f"\n✗ NO images found for owner {owner_id}")
        print("\nPossible reasons:")
        print("1. No images have been uploaded/indexed yet")
        print("2. Images were uploaded with a different owner_id")
        print("\nTo upload images, use: POST /api/image/upload")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
