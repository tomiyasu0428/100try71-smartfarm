from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel


class PlantingPlanField(BaseModel):
    """作付け計画と圃場の関連付けモデル"""
    id: Optional[int] = None
    planting_plan_id: int
    field_id: int
    sequence: int  # 圃場の使用順序
    area: float  # 作付け面積 (m²)
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WorkflowInstance(BaseModel):
    """作業インスタンスモデル"""
    id: Optional[int] = None
    planting_plan_id: int
    step_name: str  # 作業名
    planned_date: Optional[date] = None  # 予定日
    actual_date: Optional[date] = None  # 実績日
    days_from_planting: Optional[int] = None  # 定植日からの日数
    parent_instance_id: Optional[int] = None  # 親作業インスタンス（階層構造用）
    status: str = "未着手"  # 未着手/進行中/完了
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PlantingPlan(BaseModel):
    """作付け計画モデル"""
    id: Optional[int] = None
    plan_name: str  # 作付け名
    crop_id: int  # 作物ID
    organization_id: int  # 組織ID
    season: Optional[str] = None  # 作付けシーズン（春夏/秋冬など）
    planting_date: Optional[date] = None  # 定植予定日
    harvest_date: Optional[date] = None  # 収穫予定日
    status: str = "計画中"  # 計画中/進行中/完了
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # 以下はデータベースには保存されず、APIレスポンス用
    fields: Optional[List[PlantingPlanField]] = None
    workflow_instances: Optional[List[WorkflowInstance]] = None
