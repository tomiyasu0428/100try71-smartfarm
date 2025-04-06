from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: int
    organization_id: int
    user_id: Optional[int] = None
    content: str
    is_from_ai: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class ChatSession(BaseModel):
    id: int
    organization_id: int
    user_id: Optional[int] = None
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode
