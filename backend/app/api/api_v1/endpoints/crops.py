from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.crop import CropCreate, CropUpdate, CropResponse
from app.services.crop_service import CropService
from app.api.deps import get_current_user, get_crop_service

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
    return await crop_service.get_crops(organization_id=current_user.organization_id, skip=skip, limit=limit)


@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    crop_in: CropCreate,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    新しい作物を作成します。
    """
    return await crop_service.create_crop(crop_in=crop_in, organization_id=current_user.organization_id)


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(
    crop_id: int,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    特定の作物の詳細を取得します。
    """
    crop = await crop_service.get_crop(crop_id=crop_id)
    if not crop or crop.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作物が見つかりません")
    return crop


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
    crop = await crop_service.get_crop(crop_id=crop_id)
    if not crop or crop.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作物が見つかりません")

    return await crop_service.update_crop(crop_id=crop_id, crop_in=crop_in)


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop(
    crop_id: int,
    current_user=Depends(get_current_user),
    crop_service: CropService = Depends(get_crop_service),
):
    """
    作物を削除します。
    """
    crop = await crop_service.get_crop(crop_id=crop_id)
    if not crop or crop.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="作物が見つかりません")

    success = await crop_service.delete_crop(crop_id=crop_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="作物の削除に失敗しました"
        )
