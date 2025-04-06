from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ResourceBase(BaseModel):
    name: str
    resource_type: str  # 資材 or 農機
    quantity: Optional[float] = None
    unit: Optional[str] = None
    status: str  # 利用可能, 使用中, 修理中, 廃棄
    location: Optional[str] = None
    notes: Optional[str] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    resource_type: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class ResourceInDBBase(ResourceBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class ResourceResponse(ResourceInDBBase):
    pass
