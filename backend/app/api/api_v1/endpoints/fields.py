from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.field import FieldCreate, FieldUpdate, FieldResponse
from app.services.field_service import FieldService
from app.api.deps import get_current_user, get_field_service

router = APIRouter()

@router.get("/", response_model=List[FieldResponse])
async def get_fields(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    field_service: FieldService = Depends(get_field_service)
):
    """
    組織に属する全ての圃場を取得します。
    """
    return await field_service.get_fields(
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(
    field_in: FieldCreate,
    current_user = Depends(get_current_user),
    field_service: FieldService = Depends(get_field_service)
):
    """
    新しい圃場を作成します。
    """
    return await field_service.create_field(
        field_in=field_in,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )

@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: int,
    current_user = Depends(get_current_user),
    field_service: FieldService = Depends(get_field_service)
):
    """
    特定の圃場の詳細を取得します。
    """
    field = await field_service.get_field(field_id=field_id)
    if not field or field.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    return field

@router.put("/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: int,
    field_in: FieldUpdate,
    current_user = Depends(get_current_user),
    field_service: FieldService = Depends(get_field_service)
):
    """
    圃場情報を更新します。
    """
    field = await field_service.get_field(field_id=field_id)
    if not field or field.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    return await field_service.update_field(
        field_id=field_id,
        field_in=field_in
    )

@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(
    field_id: int,
    current_user = Depends(get_current_user),
    field_service: FieldService = Depends(get_field_service)
):
    """
    圃場を削除します。
    """
    field = await field_service.get_field(field_id=field_id)
    if not field or field.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    await field_service.delete_field(field_id=field_id)
    return None
