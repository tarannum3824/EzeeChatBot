import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="EzeeChatBot API",
    description="RAG chatbot powered by Google Gemini AI",
    version="1.0.0",
)

app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
