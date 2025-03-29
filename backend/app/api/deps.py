from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenPayload
from app.services.field_service import FieldService
from app.services.user_service import UserService
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
