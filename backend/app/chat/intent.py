def classify_intent(normalized: dict) -> str:
    """Classify user intent from normalized input.
    
    Returns:
        'chitchat' - greetings, small talk (no retrieval needed)
        'meta' - questions about chat history (use session history, no retrieval)
        'multimodal' - has image or audio upload
        'knowledge' - needs database retrieval
    """
    if normalized.get("image_url") or normalized.get("audio_url"):
        return "multimodal"

    text = (normalized.get("text") or "").strip().lower()

    # Chitchat patterns (no retrieval needed)
    chitchat_patterns = [
        "hi", "hello", "hey", "thanks", "thank you", 
        "bye", "goodbye", "ok", "okay"
    ]
    if any(pattern in text for pattern in chitchat_patterns):
        return "chitchat"

    # Meta-questions about conversation (use history, no retrieval)
    meta_patterns = [
        "what have we discussed",
        "what did we talk about",
        "tell me about our conversation",
        "summarize our chat",
        "recap of our discussion",
        "what have you told me",
        "remind me what we discussed",
        "our conversation",
    ]
    if any(pattern in text for pattern in meta_patterns):
        return "meta"

    if len(text.split()) <= 4:
        return "short_query"

    return "knowledge"
