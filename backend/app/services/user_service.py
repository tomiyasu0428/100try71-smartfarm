from typing import Optional
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.db.session import get_supabase_client
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        パスワードを検証します
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        パスワードをハッシュ化します
        """
        return pwd_context.hash(password)
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        ユーザーIDからユーザーを取得します
        """
        response = self.supabase.table("users").select("*").eq(
            "id", user_id
        ).limit(1).execute()
        
        if not response.data:
            return None
        
        return User(**response.data[0])
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        メールアドレスからユーザーを取得します
        """
        response = self.supabase.table("users").select("*").eq(
            "email", email
        ).limit(1).execute()
        
        if not response.data:
            return None
        
        return User(**response.data[0])
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        ユーザーを認証します
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        # Supabaseの認証を使用する場合、パスワード検証はSupabaseに任せる
        # ここでは簡易的な実装としてパスワードを直接検証
        response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if not response.user:
            return None
        
        return user
    
    def create_access_token(self, user_id: str) -> str:
        """
        アクセストークンを作成します
        """
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"exp": expire, "sub": user_id}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
