from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str
    organization_id: int
    name: str
    email: EmailStr
    role: str = "worker"
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    organization_id: int
    role: Optional[str] = "worker"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
