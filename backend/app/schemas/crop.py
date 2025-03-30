from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    name: str  # 作業名（例：播種、苗作り、圃場づくり、防除）
    days: Optional[int] = None  # 開始日からの日数
    sub_steps: Optional[List["WorkflowStep"]] = Field(default_factory=list)  # 子フロー（例：圃場づくり→ディスクハロー→肥料散布→ロータリー→畝立て）


# 循環参照を解決するための更新
WorkflowStep.update_forward_refs()


class CropBase(BaseModel):
    name: str  # 作物名
    category: str  # 種類（アブラナ科、ウリ科など）
    workflow: Optional[List[WorkflowStep]] = None  # 作業フロー（複数作成可能）
    notes: Optional[str] = None  # メモ


class CropCreate(CropBase):
    pass


class CropUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    workflow: Optional[List[WorkflowStep]] = None
    notes: Optional[str] = None


class CropInDBBase(CropBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CropResponse(CropInDBBase):
    pass
