from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class Field(BaseModel):
    id: int
    organization_id: int
    user_id: str
    name: str
    coordinates: str  # GeoJSON形式のポリゴン座標をJSON文字列として保存
    area: float  # ヘクタール単位の面積
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
