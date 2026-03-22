from fastapi import APIRouter
from app.models.schema import UploadRequest, ChatRequest
from app.services.rag_service import chat
from app.services.upload_service import handle_upload
from app.services.stats_service import get_stats

router = APIRouter()

@router.post("/upload")
async def upload(data: UploadRequest):
    return await handle_upload(data)

@router.post("/chat")
async def chat_api(data: ChatRequest):
    answer, history = await chat(
        data.bot_id,
        data.user_message,
        data.conversation_history
    )
    return {"response": answer, "conversation_history": history}

@router.get("/stats/{bot_id}")
async def stats(bot_id: str):
    return get_stats(bot_id)
