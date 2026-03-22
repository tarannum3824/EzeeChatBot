import uuid
import logging
from fastapi import HTTPException
from app.utils.chunking import chunk_text
from app.utils.loader import load_from_url, load_text, load_from_file
from app.services.vector_store_service import create_vector_store

logger = logging.getLogger(__name__)


async def handle_upload(data):
    if not data.text and not data.url:
        raise HTTPException(status_code=400, detail="Provide either 'text' or 'url'.")

    bot_id = str(uuid.uuid4())

    try:
        content = load_from_url(data.url) if data.url else load_text(data.text)
    except Exception as e:
        logger.error(f"Content loading failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to load content: {e}")

    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="Uploaded content is empty.")

    chunks = chunk_text(content)

    if not chunks:
        raise HTTPException(status_code=400, detail="Content too short to process.")

    try:
        create_vector_store(chunks, bot_id)
    except Exception as e:
        logger.error(f"Vector store creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create knowledge base.")

    return {"bot_id": bot_id, "chunks_created": len(chunks)}


async def handle_file_upload(file):
    bot_id = str(uuid.uuid4())

    try:
        content = load_from_file(file)
    except Exception as e:
        logger.error(f"File processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process file: {e}")

    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="File content is empty or unreadable.")

    chunks = chunk_text(content)

    if not chunks:
        raise HTTPException(status_code=400, detail="File content too short to process.")

    try:
        create_vector_store(chunks, bot_id)
    except Exception as e:
        logger.error(f"Vector store creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create knowledge base.")

    return {"bot_id": bot_id, "chunks_created": len(chunks), "filename": file.filename}
