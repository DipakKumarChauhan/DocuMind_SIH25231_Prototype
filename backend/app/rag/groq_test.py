from groq import Groq
from app.config import settings

def verify_groq():
    if not settings.GROQ_API_KEY:
        print("GROQ_API_KEY is not set in environment variables.")
        return
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        response =  client.chat.completions.create(
            model = "llama-3.1-8b-instant",
            messages = [{
                "role": "user",
                "content": "Say Ok if you can read this "
            }], max_tokens=5,
        )

        text = response.choices[0].message.content
        print("Groq APi is working")
        print("Response: ",text)


    except Exception as e:
        print(f"Failed to create Groq client:")
        print(e)

if __name__ == "__main__":
    verify_groq()