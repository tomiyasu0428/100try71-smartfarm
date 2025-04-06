from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    field_id: int
    task_type: str
    status: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    field_id: Optional[int] = None
    task_type: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class TaskInDBBase(TaskBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class TaskResponse(TaskInDBBase):
    field_name: str = ""  # 圃場名を含める
