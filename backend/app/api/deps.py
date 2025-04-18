from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.field_service import FieldService
from app.services.crop_service import CropService
from app.services.user_service import UserService
from app.services.planting_plan_service import PlantingPlanService
from app.services.task_service import TaskService
from app.services.resource_service import ResourceService
from app.services.chat_service import ChatService
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(lambda: UserService())
) -> User:
    """
    現在のユーザーを取得するための依存関係
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証情報が無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_service.get_user(user_id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません"
        )
    return user

def get_field_service() -> FieldService:
    """
    圃場サービスを取得するための依存関係
    """
    return FieldService()

def get_crop_service() -> CropService:
    """
    作物マスターサービスを取得するための依存関係
    """
    return CropService()

def get_planting_plan_service() -> PlantingPlanService:
    """
    作付け計画サービスを取得するための依存関係
    """
    return PlantingPlanService()

def get_task_service() -> TaskService:
    """
    作業サービスを取得するための依存関係
    """
    return TaskService()

def get_resource_service() -> ResourceService:
    """
    資材・農機サービスを取得するための依存関係
    """
    return ResourceService()

def get_chat_service() -> ChatService:
    """
    AIチャットサービスを取得するための依存関係
    """
    return ChatService()
