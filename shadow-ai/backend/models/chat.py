from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Message(BaseModel):
    role: str # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str = "New Chat"
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    image_data: Optional[str] = None # Base64 encoded image
    message: str
    response_mode: Optional[str] = "direct"
    preferred_model: Optional[str] = "auto"
