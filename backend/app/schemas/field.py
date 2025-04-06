from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class GeoCoordinate(BaseModel):
    lat: float
    lng: float

class FieldBase(BaseModel):
    name: str
    soil_type: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None  # タグのリスト

class FieldCreate(FieldBase):
    coordinates: List[GeoCoordinate]  # GeoJSON形式のポリゴン座標
    area: float  # ヘクタール単位の面積（自動計算）
    crop_type: Optional[str] = None

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    coordinates: Optional[List[GeoCoordinate]] = None
    area: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None  # タグのリスト

class FieldInDBBase(FieldBase):
    id: int
    organization_id: int
    user_id: Optional[int] = None
    coordinates: List[GeoCoordinate]
    area: float
    crop_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class FieldResponse(FieldInDBBase):
    pass
