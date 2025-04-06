from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

from app.db.session import get_supabase_client
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate, ChatSessionUpdate
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException
)


class ChatService:
    def __init__(self, supabase=None):
        self.supabase = supabase or get_supabase_client()
        self.sessions_table = "chat_sessions"
        self.messages_table = "chat_messages"

    async def get_chat_sessions(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatSession]:
        """
        組織に属する全てのチャットセッションを取得します
        """
        try:
            response = self.supabase.table(self.sessions_table).select(
                "*"
            ).eq(
                "organization_id", organization_id
            ).order(
                "updated_at", desc=True
            ).range(
                skip, skip + limit - 1
            ).execute()
            
            if not response.data:
                return []
            
            sessions = []
            for item in response.data:
                if item.get("created_at"):
                    item["created_at"] = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                if item.get("updated_at"):
                    item["updated_at"] = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                
                item["messages"] = []
                sessions.append(ChatSession(**item))
            
            return sessions
        except Exception as e:
            raise DatabaseOperationException(f"チャットセッションの取得中にエラーが発生しました: {str(e)}")

    async def get_chat_session(self, session_id: int, with_messages: bool = True) -> Optional[ChatSession]:
        """
        特定のチャットセッションを取得します
        """
        try:
            response = self.supabase.table(self.sessions_table).select(
                "*"
            ).eq(
                "id", session_id
            ).execute()
            
            if not response.data:
                return None
            
            session_data = response.data[0]
            
            if session_data.get("created_at"):
                session_data["created_at"] = datetime.fromisoformat(session_data["created_at"].replace("Z", "+00:00"))
            if session_data.get("updated_at"):
                session_data["updated_at"] = datetime.fromisoformat(session_data["updated_at"].replace("Z", "+00:00"))
            
            session = ChatSession(**session_data)
            
            if with_messages:
                messages_response = self.supabase.table(self.messages_table).select(
                    "*"
                ).eq(
                    "session_id", session_id
                ).order(
                    "created_at", desc=False
                ).execute()
                
                messages = []
                for msg in messages_response.data:
                    if msg.get("created_at"):
                        msg["created_at"] = datetime.fromisoformat(msg["created_at"].replace("Z", "+00:00"))
                    messages.append(ChatMessage(**msg))
                
                session.messages = messages
            
            return session
        except Exception as e:
            raise DatabaseOperationException(f"チャットセッションの取得中にエラーが発生しました: {str(e)}")

    async def create_chat_session(
        self, session_in: ChatSessionCreate, organization_id: int, user_id: Optional[int] = None
    ) -> ChatSession:
        """
        新しいチャットセッションを作成します
        """
        try:
            now = datetime.utcnow()
            
            session_data = {
                "organization_id": organization_id,
                "title": session_in.title,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            if user_id is not None:
                session_data["user_id"] = user_id
            
            response = self.supabase.table(self.sessions_table).insert(session_data).execute()
            
            if not response.data:
                raise DatabaseOperationException("チャットセッションの作成に失敗しました")
            
            created_session = response.data[0]
            
            if created_session.get("created_at"):
                created_session["created_at"] = datetime.fromisoformat(created_session["created_at"].replace("Z", "+00:00"))
            if created_session.get("updated_at"):
                created_session["updated_at"] = datetime.fromisoformat(created_session["updated_at"].replace("Z", "+00:00"))
            
            created_session["messages"] = []
            
            return ChatSession(**created_session)
        except Exception as e:
            raise DatabaseOperationException(f"チャットセッションの作成中にエラーが発生しました: {str(e)}")

    async def update_chat_session(
        self, session_id: int, session_in: ChatSessionUpdate
    ) -> ChatSession:
        """
        チャットセッションを更新します
        """
        try:
            existing_session = await self.get_chat_session(session_id, with_messages=False)
            if not existing_session:
                raise ResourceNotFoundException(f"チャットセッションID {session_id} は存在しません")
            
            now = datetime.utcnow()
            update_data = {"updated_at": now.isoformat()}
            
            if session_in.title is not None:
                update_data["title"] = session_in.title
            
            response = self.supabase.table(self.sessions_table).update(
                update_data
            ).eq(
                "id", session_id
            ).execute()
            
            if not response.data:
                raise DatabaseOperationException("チャットセッションの更新に失敗しました")
            
            updated_session = await self.get_chat_session(session_id)
            return updated_session
        except ResourceNotFoundException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"チャットセッションの更新中にエラーが発生しました: {str(e)}")

    async def delete_chat_session(self, session_id: int) -> None:
        """
        チャットセッションを削除します
        """
        try:
            existing_session = await self.get_chat_session(session_id, with_messages=False)
            if not existing_session:
                raise ResourceNotFoundException(f"チャットセッションID {session_id} は存在しません")
            
            self.supabase.table(self.messages_table).delete().eq(
                "session_id", session_id
            ).execute()
            
            response = self.supabase.table(self.sessions_table).delete().eq(
                "id", session_id
            ).execute()
            
            if not response.data:
                raise DatabaseOperationException("チャットセッションの削除に失敗しました")
        except ResourceNotFoundException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"チャットセッションの削除中にエラーが発生しました: {str(e)}")

    async def add_message(
        self, session_id: int, message_in: ChatMessageCreate, organization_id: int, user_id: Optional[int] = None
    ) -> ChatMessage:
        """
        チャットセッションにメッセージを追加します
        """
        try:
            existing_session = await self.get_chat_session(session_id, with_messages=False)
            if not existing_session:
                raise ResourceNotFoundException(f"チャットセッションID {session_id} は存在しません")
            
            now = datetime.utcnow()
            
            message_data = {
                "session_id": session_id,
                "organization_id": organization_id,
                "content": message_in.content,
                "is_from_ai": message_in.is_from_ai,
                "created_at": now.isoformat()
            }
            
            if user_id is not None:
                message_data["user_id"] = user_id
            
            response = self.supabase.table(self.messages_table).insert(message_data).execute()
            
            if not response.data:
                raise DatabaseOperationException("メッセージの追加に失敗しました")
            
            created_message = response.data[0]
            
            if created_message.get("created_at"):
                created_message["created_at"] = datetime.fromisoformat(created_message["created_at"].replace("Z", "+00:00"))
            
            await self.update_chat_session(
                session_id=session_id,
                session_in=ChatSessionUpdate()
            )
            
            return ChatMessage(**created_message)
        except ResourceNotFoundException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"メッセージの追加中にエラーが発生しました: {str(e)}")

    async def get_ai_response(self, user_message: str, session_history: List[Dict[str, Any]]) -> str:
        """
        ユーザーのメッセージに対するAI応答を生成します
        """
        try:
            farming_responses = {
                "こんにちは": "こんにちは！SmartFarm AIアシスタントです。農業に関するご質問があればお気軽にどうぞ。",
                "天気": "現在の天気予報データにはアクセスできませんが、地域の気象情報を確認することをお勧めします。農作業の計画に役立ちます。",
                "作物": "どのような作物についてお知りになりたいですか？栽培方法、病害虫対策、収穫時期など具体的にお聞かせください。",
                "肥料": "適切な肥料選びは作物の成長に重要です。土壌検査を行い、作物に合った肥料を選ぶことをお勧めします。",
                "病害虫": "病害虫の早期発見と対策が重要です。定期的な観察と予防的な対策を行いましょう。具体的な症状があれば教えてください。",
                "水やり": "水やりは作物によって適切な量と頻度が異なります。過剰な水やりは根腐れの原因になるため注意が必要です。",
                "収穫": "収穫のタイミングは作物の品質に大きく影響します。適切な収穫時期を見極めることが重要です。",
                "土壌": "健康な土壌は農業の基本です。定期的な土壌検査と適切な管理を行いましょう。",
                "有機栽培": "有機栽培は環境に優しく、安全な作物を生産できます。輪作や天敵の利用など総合的な管理が重要です。",
                "スマート農業": "IoTセンサーやデータ分析を活用することで、効率的な農業経営が可能になります。具体的な導入方法についてご質問ください。"
            }
            
            for keyword, response in farming_responses.items():
                if keyword in user_message:
                    return response
            
            return "申し訳ありませんが、もう少し具体的に農業に関するご質問をいただけますか？作物の栽培方法、病害虫対策、肥料、水やりなどについてお答えできます。"
            
        except Exception as e:
            raise Exception(f"AI応答の生成中にエラーが発生しました: {str(e)}")
