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
                {
                    "role":"user",
                    "content": prompt
                }
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

