from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    name: str  # 作業名（例：播種、苗作り、圃場づくり、防除）
    days: Optional[int] = None  # 開始日からの日数
    sub_steps: Optional[List["WorkflowStep"]] = Field(default_factory=list)  # 子フロー（例：圃場づくり→ディスクハロー→肥料散布→ロータリー→畝立て）


# 循環参照を解決するための更新
WorkflowStep.update_forward_refs()


class Crop(BaseModel):
    id: int
    organization_id: int
    name: str  # 作物名
    workflow: List[WorkflowStep]  # 作業フロー（複数作成可能）
    category: str  # 種類（アブラナ科、ウリ科など）
    notes: Optional[str] = None  # メモ
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
