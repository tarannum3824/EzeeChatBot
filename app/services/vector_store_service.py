import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.config import GOOGLE_API_KEY


def create_vector_store(chunks, bot_id):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", google_api_key=GOOGLE_API_KEY
    )
    db = FAISS.from_texts(chunks, embeddings)

    path = f"storage/bots/{bot_id}"
    os.makedirs(path, exist_ok=True)
    db.save_local(path)


def load_vector_store(bot_id):
    path = f"storage/bots/{bot_id}"
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", google_api_key=GOOGLE_API_KEY
    )
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
