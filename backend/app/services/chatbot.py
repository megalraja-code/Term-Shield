from groq import Groq
from app.config import settings
from app.services.embedder import search_index
import logging

logger  = logging.getLogger(__name__)
_client = Groq(api_key=settings.GROQ_API_KEY)
_MODEL  = "llama-3.1-8b-instant"

def answer_question(aid: int, question: str) -> dict:
    results = search_index(aid, question, top_k=4)
    if not results:
        return {"answer": "I couldn't find relevant information in this document.", "sources": []}
    ctx  = "\n\n".join(f"[Clause {i+1}]: {c}" for i, (c, _) in enumerate(results))
    srcs = [{"clause_number": i+1,
              "text": c[:220] + ("..." if len(c) > 220 else ""),
              "relevance": round(s, 3)} for i, (c, s) in enumerate(results)]
    prompt = f"""You are TermShield AI. Answer ONLY from the clauses below. Cite clause numbers. Never invent info.

Clauses:
{ctx}

Question: {question}
Answer:"""
    try:
        r = _client.chat.completions.create(model=_MODEL,
              messages=[{"role":"user","content":prompt}], temperature=0.15, max_tokens=500)
        return {"answer": r.choices[0].message.content.strip(), "sources": srcs}
    except Exception as e:
        logger.error(f"Chatbot: {e}")
        return {"answer": "Error processing request. Please try again.", "sources": []}
