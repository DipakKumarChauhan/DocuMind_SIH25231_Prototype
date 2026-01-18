# from app.chat.session_store import get_session
# from app.chat.input_normalizer import normalize_chat_input
# from app.chat.router import route_query
# from app.chat.context_builder import build_context
# from app.llm.groq_client import call_llm


# async def run_chat_turn(
#         owner_id: str,
#         session_id: str | None,
#         message: str | None,
#         image,
#         audio,
# ): 
#     session_id, session = get_session(owner_id, session_id)

#     normalized = await normalize_chat_input(
#         message=message,
#         image=image,
#         audio=audio,
#         owner_id=owner_id,
#     )

#     retrieval_results = route_query(normalized)
#     print(f"[DEBUG] Retrieval results structure:")
#     for key, value in retrieval_results.items():
#         print(f"  {key}: {type(value)} - {len(value) if isinstance(value, list) else 'N/A'} items")
#         if isinstance(value, list) and value:
#             print(f"    First item: {value[0]}")
    
#     citations = []
#     citation_id = 1
#     for chunk in retrieval_results:
#         citations.append({
#             "citation_id": citation_id,
#             "source_type": chunk.source,
#             "file_id": chunk.file_id,
#             "filename": chunk.payload.get("filename"),
#             "page": chunk.payload.get("page"),
#             "image_url": chunk.payload.get("image_url"),
#             "audio_url": chunk.payload.get("audio_url"),
#             "timestamp": chunk.payload.get("timestamp"),
#             "snippet": (chunk.payload.get("text") or "")[:300],
#         })
#     citation_id += 1
#     context , citations = build_context(retrieval_results)
#     print(f"[DEBUG] Context length: {len(context)}, Citations count: {len(citations)}")

#     answer = call_llm(
#         question=normalized['text'],
#         context=context,
#         history=session['history'],
#     )

#     session['history'].append({
#         "role"  : "user",
#         "content": normalized['text'],
#     })

#     session["history"].append({"role": "assistant", "content": answer})
#     session["history"] = session["history"][-7:]

#     return {
#         "session_id": session_id,
#         "answer": answer,
#         "citations": citations,
#     }


from app.chat.session_store import get_session
from app.chat.input_normalizer import normalize_chat_input
from app.chat.router import route_query
from app.chat.context_builder import build_context
from app.llm.groq_client import call_llm


async def run_chat_turn(
    owner_id: str,
    session_id: str | None,
    message: str | None,
    image,
    audio,
):
    # 1️⃣ Session
    session_id, session = get_session(owner_id, session_id)

    # 2️⃣ Normalize input
    normalized = await normalize_chat_input(
        message=message,
        image=image,
        audio=audio,
        owner_id=owner_id,
        session=session,
    )

    if not normalized.get("text"):
        return {
            "session_id": session_id,
            "answer": "I couldn’t understand your query. Please try again.",
            "citations": [],
        }

    # 3️⃣ Retrieval
    retrieval_results = route_query(normalized)

    # 4️⃣ Context + citations
    context, citations = build_context(retrieval_results)

    # 👇 REQUIRED for citation resolver
    session["citations"] = citations

    # 5️⃣ LLM
    answer = call_llm(
        question=normalized["text"],
        context=context,
        history=session["history"],
    )

    # 6️⃣ History
    session["history"].extend([
        {"role": "user", "content": normalized["text"]},
        {"role": "assistant", "content": answer},
    ])
    session["history"] = session["history"][-7:]
    
    # session["temp_assets"]["images"].append(image_url)
    # session["temp_assets"]["audio"].append(audio_url)


    return {
        "session_id": session_id,
        "answer": answer,
        "citations": citations,
    }
