import logging
from fastapi import FastAPI
from app.api.routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="EzeeChatBot API",
    description="RAG chatbot powered by Google Gemini AI",
    version="1.0.0",
)

app.include_router(router)
