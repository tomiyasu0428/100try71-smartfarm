from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.crop import CropCreate, CropUpdate, CropResponse
from app.services.crop_service import CropService
from app.api.deps import get_current_user, get_crop_service
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException
)

router = APIRouter()


@router.get("/", response_model=List[CropResponse])
async def get_crops(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    組織に属する全ての作物を取得します。
    """
    try:
        return await crop_service.get_crops(organization_id=current_user.organization_id, skip=skip, limit=limit)
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )


@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    crop_in: CropCreate,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    新しい作物を作成します。
    """
    try:
        return await crop_service.create_crop(crop_in=crop_in, organization_id=current_user.organization_id)
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


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(
    crop_id: int,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    特定の作物の詳細を取得します。
    """
    try:
        crop = await crop_service.get_crop(crop_id=crop_id)
        if not crop or crop.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作物が見つかりません")
        return crop
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


@router.put("/{crop_id}", response_model=CropResponse)
async def update_crop(
    crop_id: int,
    crop_in: CropUpdate,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    作物情報を更新します。
    """
    try:
        crop = await crop_service.get_crop(crop_id=crop_id)
        if not crop or crop.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作物が見つかりません")

        return await crop_service.update_crop(crop_id=crop_id, crop_in=crop_in)
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


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop(
    crop_id: int,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    作物を削除します。
    """
    try:
        crop = await crop_service.get_crop(crop_id=crop_id)
        if not crop or crop.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作物が見つかりません")

        await crop_service.delete_crop(crop_id=crop_id)
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
