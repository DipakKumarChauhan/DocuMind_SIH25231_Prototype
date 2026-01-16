#!/usr/bin/env python3
"""
Check actual payload structure of images
"""

import sys
sys.path.insert(0, '/home/dipak/SIH-25321_MVP/backend')

from app.db.qdrant_client import get_qdrant_client
from qdrant_client.models import Filter, FieldCondition, MatchValue
import json

owner_id = "1584bf98-0ebb-4bff-b0ad-3d09f2f8043c"

print("Checking image payload structure...")

client = get_qdrant_client()

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
    point = scroll_result[0][0]
    print("\nSample point payload keys:")
    print(json.dumps(list(point.payload.keys()), indent=2))
    print("\nFull payload:")
    print(json.dumps(point.payload, indent=2, default=str))
else:
    print("No points found")
