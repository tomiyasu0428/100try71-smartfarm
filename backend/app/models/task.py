from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Task(BaseModel):
    id: int
    organization_id: int
    field_id: int
    task_type: str
    status: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode
