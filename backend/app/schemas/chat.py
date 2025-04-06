from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ChatMessageBase(BaseModel):
    content: str
    is_from_ai: bool = False


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageInDBBase(ChatMessageBase):
    id: int
    organization_id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class ChatMessageResponse(ChatMessageInDBBase):
    pass


class ChatSessionBase(BaseModel):
    title: str


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None


class ChatSessionInDBBase(ChatSessionBase):
    id: int
    organization_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class ChatSessionResponse(ChatSessionInDBBase):
    messages: List[ChatMessageResponse] = []
