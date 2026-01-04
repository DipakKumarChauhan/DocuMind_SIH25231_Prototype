from typing import List, Dict
from app.llm.groq_client import generate_completion


def build_rag_prompt(query: str, chunks: List[Dict]) -> str:
    sources = []

    for i, ch in enumerate(chunks, start=1):
        meta = ch["metadata"]
        sources.append(
            f"""
[Source {i}]
Filename: {meta.get("filename")}
Page: {meta.get("page")}
Text:
{ch["text"]}
""".strip()
        )

    context = "\n\n".join(sources)

    return f"""
You are an expert educator answering a student's question.

Answer clearly and directly using ONLY the information in the CONTEXT below.
Explain concepts naturally by synthesizing the information into connected paragraphs.

STRICT RULES:
1. Start with a direct definition or explanation - no meta-commentary
2. Do NOT mention: "sources", "documents", "context", "curricula", "modules", "syllabus"
3. Do NOT use phrases like: "according to", "the text says", "provided information"
4. Synthesize related facts into flowing sentences; avoid bullet lists unless the question explicitly asks for one
5. Do NOT add external knowledge or speculate
6. If the answer cannot be found in the context, respond with exactly: "I cannot answer this based on the available information."

QUESTION:
{query}

CONTEXT:
{context}

Your answer:
""".strip()


def generate_rag_answer(query: str, chunks: List[Dict]) -> Dict:
    if not chunks:
        return {
            "answer": "I don't know based on the provided documents.",
            "citations": [],
        }

    prompt = build_rag_prompt(query, chunks)
    answer = generate_completion(prompt)

    citations = []
    for ch in chunks:
        meta = ch["metadata"]
        citations.append({
            "chunk_id": ch["id"],
            "filename": meta.get("filename"),
            "page": meta.get("page"),
            "score": ch["score"],
        })

    return {
        "answer": answer,
        "citations": citations,
    }
   
