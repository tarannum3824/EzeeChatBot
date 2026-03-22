from pydantic import BaseModel
from typing import List, Optional

class UploadRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None

class ChatRequest(BaseModel):
    bot_id: str
    user_message: str
    conversation_history: List[str] = []