from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse, ChatMessageCreate, ChatMessageResponse
from app.services.chat_service import ChatService
from app.api.deps import get_current_user, get_chat_service
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException
)

router = APIRouter()

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    組織に属する全てのチャットセッションを取得します。
    """
    try:
        organization_id = 1  # テスト用の組織ID
        return await chat_service.get_chat_sessions(
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_in: ChatSessionCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    新しいチャットセッションを作成します。
    """
    try:
        organization_id = 1  # テスト用の組織ID
        user_id = None  # テスト用のユーザーID
        return await chat_service.create_chat_session(
            session_in=session_in,
            organization_id=organization_id,
            user_id=user_id
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

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    特定のチャットセッションの詳細を取得します。
    """
    try:
        session = await chat_service.get_chat_session(session_id=session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        return session
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

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: int,
    session_in: ChatSessionUpdate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    チャットセッション情報を更新します。
    """
    try:
        return await chat_service.update_chat_session(
            session_id=session_id,
            session_in=session_in
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

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: int,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    チャットセッションを削除します。
    """
    try:
        await chat_service.delete_chat_session(session_id=session_id)
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

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def add_message(
    session_id: int,
    message_in: ChatMessageCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    チャットセッションにメッセージを追加します。
    """
    try:
        organization_id = 1  # テスト用の組織ID
        user_id = None  # テスト用のユーザーID
        
        user_message = await chat_service.add_message(
            session_id=session_id,
            message_in=message_in,
            organization_id=organization_id,
            user_id=user_id
        )
        
        if not message_in.is_from_ai:
            session = await chat_service.get_chat_session(session_id=session_id)
            session_history = [
                {"content": msg.content, "is_from_ai": msg.is_from_ai}
                for msg in session.messages
            ]
            
            ai_response = await chat_service.get_ai_response(
                user_message=message_in.content,
                session_history=session_history
            )
            
            ai_message_in = ChatMessageCreate(
                content=ai_response,
                is_from_ai=True
            )
            
            await chat_service.add_message(
                session_id=session_id,
                message_in=ai_message_in,
                organization_id=organization_id,
                user_id=user_id
            )
        
        return user_message
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{e.message}"
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
