import time
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.vector_store_service import load_vector_store
from app.services.stats_service import update_stats
from app.core.config import GOOGLE_API_KEY

# In-memory conversation history per bot
conversation_store = {}


async def chat(bot_id, query, history):
    start = time.time()

    # Initialize history for this bot if not exists
    if bot_id not in conversation_store:
        conversation_store[bot_id] = []

    # Use server-side history (ignore client history if empty)
    full_history = conversation_store[bot_id]

    db = load_vector_store(bot_id)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)

    if not docs:
        update_stats(bot_id, 0, False)
        full_history.append({"role": "user", "message": query})
        full_history.append({"role": "bot", "message": "I could not find the answer in the provided knowledge base."})
        return "I could not find the answer in the provided knowledge base.", full_history

    context = "\n".join([d.page_content for d in docs])

    # Format history for prompt
    history_text = "\n".join(
        [f"{h['role']}: {h['message']}" for h in full_history[-10:]]
    )

    prompt = f"""
    Answer ONLY from the context below.
    If not found, say you don't know.

    Context:
    {context}

    Conversation History:
    {history_text}

    Question:
    {query}
    """

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY
    )
    answer = llm.invoke(prompt)

    latency = (time.time() - start) * 1000
    update_stats(bot_id, latency, True)

    # Save to history
    full_history.append({"role": "user", "message": query})
    full_history.append({"role": "bot", "message": answer.content})

    return answer.content, full_history
