from groq import Groq
from typing import Optional
from app.config import settings



#-------------- Client Initialization --------------#

_client = Groq(
    api_key=settings.GROQ_API_KEY,
    timeout= 15.0,
)

class LLMServiceError(Exception):
    """Raised when LLM call fails safely"""

def generate_completion(
        prompt:str,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.2,
        max_token: int = 512,
) -> str:
    """ 
    Safe Groq LLM call with timeout and Error Handling is done here..
    """
    try:
        response = _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_token,
        )
        return response.choices[0].message.content
    
    except Exception as e:
        # Handle all errors
        raise LLMServiceError(
            f"LLM Error: {str(e)}"
        )


def call_llm(question: str, context: Optional[str], history: list, low_confidence: bool = False) -> str:
    """
    Format question, context, and history into a prompt and call LLM.
    Designed for chat orchestration with multi-turn conversations.
    Handles knowledge queries (with context), chitchat, and meta-questions.
    """
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-3:]]) if history else ""
    question_lower = question.lower().strip()
    
    # 💬 Meta-question mode: summarize conversation history
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
    
    is_meta_question = any(pattern in question_lower for pattern in meta_patterns)
    
    if context is None and is_meta_question:
        prompt = f"""You are a helpful AI assistant.

CONVERSATION HISTORY (from this chat session):
{history_text if history_text else "No previous messages in this session"}

USER IS ASKING YOU TO:
{question}

INSTRUCTIONS:
- Summarize what we have discussed in this conversation
- List the main topics or questions that were asked
- Be concise and organized
- Use bullet points if helpful
- Don't make up topics we didn't discuss

Provide a clear summary of our conversation:"""
        return generate_completion(prompt=prompt)
    
    # 💬 Chitchat mode: no retrieval, conversational responses
    if context is None:
        prompt = f"""You are a friendly and helpful AI assistant.

USER MESSAGE:
{question}

CONVERSATION HISTORY:
{history_text if history_text else "No previous messages"}

INSTRUCTIONS:
- Respond naturally and conversationally
- For greetings (hi, hello, hey), respond warmly
- For thanks, acknowledge politely
- Keep responses brief and friendly
- Don't mention documents or retrieval

Respond to the user:"""
        return generate_completion(prompt=prompt)
    
    # 📚 Knowledge mode: use retrieved context
    disclaimer_note = (
        "\n\nNOTE: Retrieved context appears limited; include a brief one-line disclaimer that the answer may be incomplete."
        if low_confidence else ""
    )
    prompt = f"""You are a helpful AI assistant answering questions based on provided documents.

CURRENT QUESTION (THIS IS WHAT YOU MUST ANSWER):
{question}

DOCUMENT CONTEXT RETRIEVED FOR THIS QUESTION:
{context if context.strip() else "No documents found for this question"}

CONVERSATION HISTORY (only for reference, NOT to change the topic):
{history_text if history_text else "No previous messages"}

CRITICAL INSTRUCTIONS:
1. **FOCUS ON THE CURRENT QUESTION** - Answer EXACTLY what is being asked right now
2. **Use only the current context** - Reference documents retrieved for THIS question, not previous conversations
3. **Don't redirect the topic** - Even if history mentions other topics, stay focused on the current question
4. **If context is provided, use it** - If documents are retrieved, base your answer on them
5. **If no context, use your knowledge** - But stay focused on the specific question
6. **Be direct and comprehensive** - Provide thorough answers with examples when relevant
7. **Availability checks** - When the user asks if an item (image/document/audio) is present, inspect the retrieved context:
    - If you see any IDs/URLs in context, answer "Yes, found" and list them
    - If none are present, answer "No, not found" and say what would be needed

ANSWER FORMAT:
- Start with a clear yes/no if the question is about presence/availability
- If yes, list the IDs/URLs you see in the retrieved context (prefer exact IDs from context)
- If no, state that nothing was found in the retrieved context

WHAT NOT TO DO:
- Do NOT assume the user is asking the same thing as before
- Do NOT use old conversation topics to reinterpret the current question
- Do NOT provide information about previous questions unless the user explicitly refers to them
- Do NOT hallucinate or invent document sources

Answer the current question based on the provided context:{disclaimer_note}"""
    
    return generate_completion(prompt=prompt)

