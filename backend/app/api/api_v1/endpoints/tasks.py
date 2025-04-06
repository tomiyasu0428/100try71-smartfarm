from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService
from app.api.deps import get_current_user, get_task_service
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException
)

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    task_service: TaskService = Depends(get_task_service)
):
    """
    組織に属する全ての作業を取得します。
    """
    try:
        organization_id = 1  # テスト用の組織ID
        return await task_service.get_tasks(
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    task_service: TaskService = Depends(get_task_service)
):
    """
    新しい作業を作成します。
    """
    try:
        organization_id = 1  # テスト用の組織ID
        return await task_service.create_task(
            task_in=task_in,
            organization_id=organization_id
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e.message}"
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service)
):
    """
    特定の作業の詳細を取得します。
    """
    try:
        task = await task_service.get_task(task_id=task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
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

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    task_service: TaskService = Depends(get_task_service)
):
    """
    作業情報を更新します。
    """
    try:
        return await task_service.update_task(
            task_id=task_id,
            task_in=task_in
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

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service)
):
    """
    作業を削除します。
    """
    try:
        await task_service.delete_task(task_id=task_id)
        return None
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
