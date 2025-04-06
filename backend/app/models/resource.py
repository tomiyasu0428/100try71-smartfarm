from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Resource(BaseModel):
    id: int
    organization_id: int
    name: str
    resource_type: str  # 資材 or 農機
    quantity: Optional[float] = None
    unit: Optional[str] = None
    status: str  # 利用可能, 使用中, 修理中, 廃棄
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode
