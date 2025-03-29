from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.services.user_service import UserService
from app.schemas.token import Token
from app.models.user import UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(lambda: UserService())
) -> Any:
    """
    OAuth2 互換のトークンログインを取得します
    """
    user = await user_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = user_service.create_access_token(user_id=str(user.id))
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    user_service: UserService = Depends(lambda: UserService())
) -> Any:
    """
    新しいユーザーを登録します
    """
    # メールアドレスが既に使用されているか確認
    try:
        existing_user = await user_service.get_user_by_email(email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に使用されています"
            )
        
        # 開発用の簡易実装：Supabase認証をバイパスして直接ユーザーを作成
        import uuid
        auth_id = str(uuid.uuid4())
        
        # ユーザーテーブルに直接情報を保存
        user_data = {
            # idはBIGSERIALなので自動生成される
            "name": user_in.name,
            "email": user_in.email,
            "organization_id": user_in.organization_id,
            "role": user_in.role,
            "auth_id": auth_id  # 開発用に仮のauth_idを設定
        }
        
        result = user_service.supabase.table("users").insert(user_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ユーザー登録に失敗しました"
            )
        
        # 作成されたユーザーのIDを取得
        user_id = result.data[0]['id'] if result.data and len(result.data) > 0 else None
        
        return {"message": "ユーザー登録が完了しました", "user_id": user_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ユーザー登録に失敗しました: {str(e)}"
        )
