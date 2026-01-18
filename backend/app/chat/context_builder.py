

# def build_context(results):
#     context_blocks = []
#     citations = []
#     idx = 1

#     for modality, items in results.items():
#         if not items:  # Skip empty result lists
#             continue
            
#         for item in items[:3]:
#             # Skip items without content
#             text_content = item.get('text') or item.get('ocr_text') or item.get('transcript')
#             if not text_content:
#                 continue
                
#             context_blocks.append(
#                 f"[SOURCE {idx} | {modality.upper()}]\n{text_content}"
#             )

#             # Extract file_id based on modality
#             if modality == 'text':
#                 file_id = item.get('metadata', {}).get('filename')
#                 page = item.get('metadata', {}).get('page')
#             elif modality == 'image':
#                 file_id = item.get('file_id')
#                 page = None
#             elif modality == 'audio':
#                 file_id = item.get('audio_url')
#                 page = None
#             else:
#                 file_id = item.get('file_id')
#                 page = item.get('page_number')

#             citations.append({
#                 "id": idx,
#                 "file_id": file_id,
#                 "page": page,
#                 'timestamp': item.get('timestamps') if modality == 'audio' else item.get('timestamp'),
#             })
#             idx += 1

#     return "\n\n".join(context_blocks), citations

def build_context(results):
    context_blocks = []
    citations = []
    idx = 1

    # Enforce modality priority + include extracted text from temp uploads
    # image_text = OCR from uploaded image, audio_text = transcript from uploaded audio
    modality_order = ["image_text", "audio_text", "text", "image", "audio"]

    for modality in modality_order:
        items = results.get(modality, [])
        if not items:
            continue

        for item in items[:3]:
            # Unified content extraction
            text_content = (
                item.get("text")
                or item.get("ocr_text")
                or item.get("transcript")
            )
            if not text_content:
                continue

            # Cap context length (VERY IMPORTANT)
            snippet = text_content[:400]

            # Context block (citation-friendly)
            context_blocks.append(
                f"[{idx}] {snippet}"
            )

            # --- Citation metadata normalization ---
            file_id = (
                item.get("file_id")
                or item.get("filename")
                or item.get("metadata", {}).get("filename")
                or item.get("audio_url")
            )

            page = (
                item.get("page")
                or item.get("metadata", {}).get("page")
            )

            timestamp = (
                item.get("timestamp")
                or item.get("timestamps")
            )
            
            # Map modality names for citations (image_text → image, audio_text → audio)
            citation_modality = modality.replace("_text", "") if "_text" in modality else modality

            citations.append({
                "id": idx,
                "modality": citation_modality,
                "file_id": file_id,
                "page": page,
                "timestamp": timestamp,
            })

            idx += 1

    return "\n\n".join(context_blocks), citations
