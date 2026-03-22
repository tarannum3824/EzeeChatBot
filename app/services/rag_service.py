import time
import logging
from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.vector_store_service import load_vector_store
from app.services.stats_service import update_stats
from app.core.config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

# In-memory conversation history per bot
conversation_store = {}

# Maximum FAISS distance — chunks above this are considered irrelevant
# Gemini embeddings typically return scores between 0.3-1.5
RELEVANCE_THRESHOLD = 1.2

SYSTEM_PROMPT = """You are a strict Q&A assistant. You must follow these rules:

1. Answer ONLY using the provided context below. Do not use any outside knowledge.
2. If the context does not contain enough information to answer, respond EXACTLY with:
   "I don't have enough information in the uploaded content to answer this question."
3. Do not guess, assume, or hallucinate any facts.
4. Keep answers concise and directly relevant to the question.
5. If the question is a follow-up, use the conversation history for context."""


async def chat(bot_id, query, history):
    start = time.time()

    if bot_id not in conversation_store:
        conversation_store[bot_id] = []

    full_history = conversation_store[bot_id]

    try:
        db = load_vector_store(bot_id)
    except Exception as e:
        logger.error(f"Failed to load vector store for bot {bot_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Bot '{bot_id}' not found.")

    # Retrieve with relevance scores to filter low-quality matches
    results = db.similarity_search_with_score(query, k=3)

    # Log scores for debugging
    for doc, score in results:
        logger.info(f"Score: {score:.4f} | Chunk: {doc.page_content[:80]}...")

    # Filter out chunks above distance threshold (lower score = more relevant in FAISS)
    relevant_docs = [(doc, score) for doc, score in results if score <= RELEVANCE_THRESHOLD]

    if not relevant_docs:
        no_answer = "I don't have enough information in the uploaded content to answer this question."
        update_stats(bot_id, (time.time() - start) * 1000, False)
        full_history.append({"role": "user", "message": query})
        full_history.append({"role": "bot", "message": no_answer})
        return no_answer, full_history

    context = "\n---\n".join([doc.page_content for doc, _ in relevant_docs])

    history_text = "\n".join(
        [f"{h['role']}: {h['message']}" for h in full_history[-10:]]
    )

    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Conversation History:
{history_text}

Question:
{query}"""

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0,
        )
        answer = llm.invoke(prompt)
    except Exception as e:
        logger.error(f"LLM call failed for bot {bot_id}: {e}")
        raise HTTPException(status_code=502, detail="AI model request failed. Please try again.")

    latency = (time.time() - start) * 1000
    update_stats(bot_id, latency, True)

    full_history.append({"role": "user", "message": query})
    full_history.append({"role": "bot", "message": answer.content})

    return answer.content, full_history
