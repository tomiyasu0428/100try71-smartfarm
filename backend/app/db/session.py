from typing import Generator
from supabase import create_client, Client

from app.core.config import settings

def get_supabase_client() -> Client:
    """
    Supabaseクライアントを取得します
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_db() -> Generator:
    """
    データベースセッションを取得します
    """
    db = get_supabase_client()
    try:
        yield db
    finally:
        # Supabaseはセッションを明示的に閉じる必要はありません
        pass
