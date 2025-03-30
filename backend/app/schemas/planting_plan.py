from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class PlantingPlanFieldBase(BaseModel):
    field_id: int
    sequence: int = Field(..., description="圃場の使用順序")
    area: float = Field(..., description="作付け面積 (m²)")
    notes: Optional[str] = None


class PlantingPlanFieldCreate(PlantingPlanFieldBase):
    pass


class PlantingPlanFieldUpdate(PlantingPlanFieldBase):
    field_id: Optional[int] = None
    sequence: Optional[int] = None
    area: Optional[float] = None


class PlantingPlanFieldResponse(PlantingPlanFieldBase):
    id: int
    planting_plan_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True


class WorkflowInstanceBase(BaseModel):
    step_name: str
    planned_date: Optional[date] = None
    days_from_planting: Optional[int] = None
    parent_instance_id: Optional[int] = None
    status: str = "未着手"
    notes: Optional[str] = None


class WorkflowInstanceCreate(WorkflowInstanceBase):
    pass


class WorkflowInstanceUpdate(BaseModel):
    step_name: Optional[str] = None
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    days_from_planting: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class WorkflowInstanceResponse(WorkflowInstanceBase):
    id: int
    planting_plan_id: int
    actual_date: Optional[date] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True


class PlantingPlanBase(BaseModel):
    plan_name: str
    crop_id: int
    season: Optional[str] = None
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    status: str = "計画中"
    notes: Optional[str] = None


class PlantingPlanCreate(PlantingPlanBase):
    fields: List[PlantingPlanFieldCreate]
    workflow_instances: Optional[List[WorkflowInstanceCreate]] = None


class PlantingPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    crop_id: Optional[int] = None
    season: Optional[str] = None
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class PlantingPlanResponse(PlantingPlanBase):
    id: int
    organization_id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    fields: List[PlantingPlanFieldResponse]
    workflow_instances: Optional[List[WorkflowInstanceResponse]] = None

    class Config:
        orm_mode = True
