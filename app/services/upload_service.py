import uuid
from app.utils.chunking import chunk_text
from app.utils.loader import load_from_url, load_text
from app.services.vector_store_service import create_vector_store

async def handle_upload(data):
    bot_id = str(uuid.uuid4())

    if data.url:
        content = load_from_url(data.url)
    else:
        content = load_text(data.text)

    chunks = chunk_text(content)

    create_vector_store(chunks, bot_id)

    return {"bot_id": bot_id}