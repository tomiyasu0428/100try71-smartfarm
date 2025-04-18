from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_planting_plan_service
from app.models.user import User
from app.services.planting_plan_service import PlantingPlanService
from app.schemas.planting_plan import (
    PlantingPlanCreate,
    PlantingPlanUpdate,
    PlantingPlanResponse,
    WorkflowInstanceUpdate
)
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException,
    WorkflowException
)


router = APIRouter()


@router.get("/", response_model=List[PlantingPlanResponse])
async def get_planting_plans(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    planting_plan_service: PlantingPlanService = Depends(get_planting_plan_service),
):
    """
    組織に属する全ての作付け計画を取得します。
    """
    return await planting_plan_service.get_planting_plans(
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=PlantingPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_planting_plan(
    plan_in: PlantingPlanCreate,
    current_user=Depends(get_current_user),
    planting_plan_service: PlantingPlanService = Depends(get_planting_plan_service),
):
    """
    新しい作付け計画を作成します。
    """
    try:
        return await planting_plan_service.create_planting_plan(
            plan_in=plan_in,
            organization_id=current_user.organization_id
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e.message}"
        )
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.message}"
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )


@router.get("/{plan_id}", response_model=PlantingPlanResponse)
async def get_planting_plan(
    plan_id: int,
    current_user=Depends(get_current_user),
    planting_plan_service: PlantingPlanService = Depends(get_planting_plan_service),
):
    """
    特定の作付け計画の詳細を取得します。
    """
    try:
        plan = await planting_plan_service.get_planting_plan(plan_id=plan_id)
        if not plan or plan.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作付け計画が見つかりません")
        return plan
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.message}"
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )


@router.put("/{plan_id}", response_model=PlantingPlanResponse)
async def update_planting_plan(
    plan_id: int,
    plan_in: PlantingPlanUpdate,
    current_user=Depends(get_current_user),
    planting_plan_service: PlantingPlanService = Depends(get_planting_plan_service),
):
    """
    作付け計画情報を更新します。
    """
    try:
        plan = await planting_plan_service.get_planting_plan(plan_id=plan_id)
        if not plan or plan.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作付け計画が見つかりません")

        return await planting_plan_service.update_planting_plan(plan_id=plan_id, plan_in=plan_in)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e.message}"
        )
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.message}"
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planting_plan(
    plan_id: int,
    current_user=Depends(get_current_user),
    planting_plan_service: PlantingPlanService = Depends(get_planting_plan_service),
):
    """
    作付け計画を削除します。
    """
    try:
        plan = await planting_plan_service.get_planting_plan(plan_id=plan_id)
        if not plan or plan.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作付け計画が見つかりません")

        await planting_plan_service.delete_planting_plan(plan_id=plan_id)
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.message}"
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )


@router.put("/workflow-instances/{instance_id}", response_model=Any)
async def update_workflow_instance(
    instance_id: int,
    instance_in: WorkflowInstanceUpdate,
    current_user=Depends(get_current_user),
    planting_plan_service: PlantingPlanService = Depends(get_planting_plan_service),
):
    """
    作業インスタンスを更新します。
    """
    # TODO: 権限チェック（この作業インスタンスが現在のユーザーの組織に属しているか）
    
    try:
        return await planting_plan_service.update_workflow_instance(
            instance_id=instance_id,
            instance_data=instance_in.dict(exclude_unset=True)
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e.message}"
        )
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.message}"
        )
    except WorkflowException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e.message}"
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )
