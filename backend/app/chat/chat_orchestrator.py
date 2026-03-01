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


from app.chat.session_store import get_session, MAX_TURNS
from app.chat.input_normalizer import normalize_chat_input
from app.chat.router import route_query
from app.chat.context_builder import build_context
from app.llm.groq_client import call_llm
from app.config import settings
import time


async def run_chat_turn(
    owner_id: str,
    session_id: str | None,
    message: str | None,
    image,
    audio,
):
    # Start timing
    start_time = time.time()
    
    # 1️⃣ Session
    session_id, session = get_session(owner_id, session_id)
    if settings.LOG_LATENCY:
        print(f"[TIMING] Session retrieval: {time.time() - start_time:.2f}s")

    # 2️⃣ Normalize input
    normalize_start = time.time()
    normalized = await normalize_chat_input(
        message=message,
        image=image,
        audio=audio,
        owner_id=owner_id,
        session=session,
    )
    if settings.LOG_LATENCY:
        print(f"[TIMING] Input normalization: {time.time() - normalize_start:.2f}s")

    if not normalized.get("text"):
        return {
            "session_id": session_id,
            "answer": "I couldn’t understand your query. Please try again.",
            "citations": [],
        }

    # 3️⃣ Follow-up awareness (one-time context reuse)
    text_lower = normalized["text"].strip().lower()
    reuse_followup = (
        "explain more" in text_lower
        and session.get("last_context")
        and session.get("last_context_reuse_count", 0) < 1
    )

    # Helper: assess retrieval confidence (simple heuristic)
    def _is_low_confidence(results: dict) -> bool:
        total_considered = 0
        max_score = 0.0
        for items in results.values():
            if not isinstance(items, list):
                continue
            for item in items:
                # Ignore synthetic upload markers that are not DB-grounding
                if item.get("filename") in ["[Uploaded Audio]", "[Uploaded Image]"]:
                    continue
                total_considered += 1
                s = item.get("score")
                if isinstance(s, (int, float)):
                    try:
                        max_score = max(max_score, float(s))
                    except Exception:
                        pass
        if total_considered == 0:
            # Results exist but none are DB-grounded → treat as low confidence
            return True
        return total_considered < 2 or max_score < 0.20

    if reuse_followup:
        # Reuse previous context (no re-retrieval)
        context = session.get("last_context", "")
        citations = session.get("citations", [])
        session["last_context_reuse_count"] = session.get("last_context_reuse_count", 0) + 1
        low_confidence = len(citations) < 2
    else:
        # 4️⃣ Retrieval (with timeouts inside router)
        retrieval_start = time.time()
        retrieval_results = await route_query(normalized)
        retrieval_time = time.time() - retrieval_start
        
        if settings.LOG_RETRIEVAL:
            print(f"[RETRIEVAL] Text results: {len(retrieval_results.get('text', []))}")
            print(f"[RETRIEVAL] Image results: {len(retrieval_results.get('image', []))}")
            print(f"[RETRIEVAL] Audio results: {len(retrieval_results.get('audio', []))}")
        if settings.LOG_LATENCY:
            print(f"[TIMING] Retrieval: {retrieval_time:.2f}s")

        # 5️⃣ Context + citations
        context, citations = build_context(retrieval_results)
        
        if settings.LOG_CONTEXT_SIZE:
            print(f"[CONTEXT] Size: {len(context)} chars, Citations: {len(citations)}")

        # Confidence flag for disclaimer logic
        low_confidence = _is_low_confidence(retrieval_results)

        # Save for single follow-up reuse
        session["last_context"] = context
        session["last_context_reuse_count"] = 0

        # 👇 REQUIRED for citation resolver
        session["citations"] = citations

    # 6️⃣ LLM with fallback strategy (VERY IMPORTANT)
    llm_start = time.time()
    if not context or not context.strip():
        # No grounding → let LLM answer without fake citations
        answer = call_llm(
            question=normalized["text"],
            context=None,
            history=session["history"],
            low_confidence=False,
        )
        citations = []  # avoid fake citations
    else:
        answer = call_llm(
            question=normalized["text"],
            context=context,
            history=session["history"],
            low_confidence=low_confidence,
        )
    if settings.LOG_LATENCY:
        print(f"[TIMING] LLM call: {time.time() - llm_start:.2f}s")

    # 7️⃣ History
    session["history"].extend([
        {"role": "user", "content": normalized["text"]},
        {"role": "assistant", "content": answer},
    ])
    session["history"] = session["history"][-MAX_TURNS:]
    
    # session["temp_assets"]["images"].append(image_url)
    # session["temp_assets"]["audio"].append(audio_url)


    return {
        "session_id": session_id,
        "answer": answer,
        "citations": citations,
    }
