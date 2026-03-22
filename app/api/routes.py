from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schema import UploadRequest, ChatRequest
from app.services.rag_service import chat
from app.services.upload_service import handle_upload, handle_file_upload
from app.services.stats_service import get_stats

router = APIRouter()


@router.post("/upload")
async def upload(data: UploadRequest):
    return await handle_upload(data)


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    allowed = (".pdf", ".txt", ".docx")
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(status_code=400, detail=f"Only {', '.join(allowed)} files are supported.")
    return await handle_file_upload(file)


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
