from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse
from app.services.resource_service import ResourceService
from app.api.deps import get_current_user, get_resource_service
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException
)

router = APIRouter()

@router.get("/", response_model=List[ResourceResponse])
async def get_resources(
    skip: int = 0,
    limit: int = 100,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    組織に属する全ての資材・農機を取得します。
    """
    try:
        organization_id = 1  # テスト用の組織ID
        return await resource_service.get_resources(
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )

@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_in: ResourceCreate,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    新しい資材・農機を作成します。
    """
    try:
        organization_id = 1  # テスト用の組織ID
        return await resource_service.create_resource(
            resource_in=resource_in,
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

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    特定の資材・農機の詳細を取得します。
    """
    try:
        resource = await resource_service.get_resource(resource_id=resource_id)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )
        return resource
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

@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_in: ResourceUpdate,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    資材・農機情報を更新します。
    """
    try:
        return await resource_service.update_resource(
            resource_id=resource_id,
            resource_in=resource_in
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

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: int,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    資材・農機を削除します。
    """
    try:
        await resource_service.delete_resource(resource_id=resource_id)
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
