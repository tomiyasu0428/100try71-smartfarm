from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, fields, crops, planting_plans, calendar, tasks
# 未実装のモジュールは一時的にコメントアウト

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["認証"])
api_router.include_router(fields.router, prefix="/fields", tags=["圃場"])
api_router.include_router(crops.router, prefix="/crops", tags=["作物"])
api_router.include_router(planting_plans.router, prefix="/planting_plans", tags=["作付け計画"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["カレンダー"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["作業"])
# 未実装のルーターは一時的にコメントアウト
# api_router.include_router(resources.router, prefix="/resources", tags=["資材・農機"])
# api_router.include_router(chat.router, prefix="/chat", tags=["AIチャット"])
