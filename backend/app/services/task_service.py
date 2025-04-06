from typing import List, Optional
from datetime import datetime
import json

from app.db.session import get_supabase_client
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException
)


class TaskService:
    def __init__(self, supabase=None):
        self.supabase = supabase or get_supabase_client()
        self.table = "tasks"
        self.fields_table = "fields"

    async def get_tasks(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        """
        組織に属する全ての作業を取得します
        """
        try:
            response = self.supabase.table(self.table).select(
                "*"
            ).eq(
                "organization_id", organization_id
            ).order(
                "scheduled_date", desc=False
            ).range(
                skip, skip + limit - 1
            ).execute()
            
            if not response.data:
                return []
            
            field_ids = [item["field_id"] for item in response.data]
            fields_response = self.supabase.table(self.fields_table).select(
                "id, name"
            ).in_("id", field_ids).execute()
            
            field_map = {field["id"]: field["name"] for field in fields_response.data}
            
            tasks = []
            for item in response.data:
                if item.get("scheduled_date"):
                    item["scheduled_date"] = datetime.fromisoformat(item["scheduled_date"].replace("Z", "+00:00"))
                if item.get("completed_date"):
                    item["completed_date"] = datetime.fromisoformat(item["completed_date"].replace("Z", "+00:00"))
                if item.get("created_at"):
                    item["created_at"] = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                if item.get("updated_at"):
                    item["updated_at"] = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                
                task = Task(**item)
                task_dict = task.dict()
                task_dict["field_name"] = field_map.get(item["field_id"], "不明")
                
                tasks.append(Task(**task_dict))
            
            return tasks
        except Exception as e:
            raise DatabaseOperationException(f"作業の取得中にエラーが発生しました: {str(e)}")

    async def get_task(self, task_id: int) -> Optional[Task]:
        """
        特定の作業を取得します
        """
        try:
            response = self.supabase.table(self.table).select(
                "*"
            ).eq(
                "id", task_id
            ).execute()
            
            if not response.data:
                return None
            
            item = response.data[0]
            
            if item.get("scheduled_date"):
                item["scheduled_date"] = datetime.fromisoformat(item["scheduled_date"].replace("Z", "+00:00"))
            if item.get("completed_date"):
                item["completed_date"] = datetime.fromisoformat(item["completed_date"].replace("Z", "+00:00"))
            if item.get("created_at"):
                item["created_at"] = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            if item.get("updated_at"):
                item["updated_at"] = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            
            field_response = self.supabase.table(self.fields_table).select(
                "name"
            ).eq(
                "id", item["field_id"]
            ).execute()
            
            task = Task(**item)
            task_dict = task.dict()
            
            if field_response.data:
                task_dict["field_name"] = field_response.data[0]["name"]
            else:
                task_dict["field_name"] = "不明"
            
            return Task(**task_dict)
        except Exception as e:
            raise DatabaseOperationException(f"作業の取得中にエラーが発生しました: {str(e)}")

    async def create_task(
        self, task_in: TaskCreate, organization_id: int
    ) -> Task:
        """
        新しい作業を作成します
        """
        try:
            now = datetime.utcnow()
            
            field_response = self.supabase.table(self.fields_table).select(
                "id, name"
            ).eq(
                "id", task_in.field_id
            ).execute()
            
            if not field_response.data:
                raise ValidationException(f"指定された圃場ID {task_in.field_id} は存在しません")
            
            task_data = {
                "organization_id": organization_id,
                "field_id": task_in.field_id,
                "task_type": task_in.task_type,
                "status": task_in.status,
                "scheduled_date": task_in.scheduled_date.isoformat(),
                "assigned_to": task_in.assigned_to,
                "notes": task_in.notes,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            if task_in.completed_date:
                task_data["completed_date"] = task_in.completed_date.isoformat()
            
            response = self.supabase.table(self.table).insert(task_data).execute()
            
            if not response.data:
                raise DatabaseOperationException("作業の作成に失敗しました")
            
            created_task = response.data[0]
            
            if created_task.get("scheduled_date"):
                created_task["scheduled_date"] = datetime.fromisoformat(created_task["scheduled_date"].replace("Z", "+00:00"))
            if created_task.get("completed_date"):
                created_task["completed_date"] = datetime.fromisoformat(created_task["completed_date"].replace("Z", "+00:00"))
            if created_task.get("created_at"):
                created_task["created_at"] = datetime.fromisoformat(created_task["created_at"].replace("Z", "+00:00"))
            if created_task.get("updated_at"):
                created_task["updated_at"] = datetime.fromisoformat(created_task["updated_at"].replace("Z", "+00:00"))
            
            task = Task(**created_task)
            task_dict = task.dict()
            task_dict["field_name"] = field_response.data[0]["name"]
            
            return Task(**task_dict)
        except ValidationException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"作業の作成中にエラーが発生しました: {str(e)}")

    async def update_task(
        self, task_id: int, task_in: TaskUpdate
    ) -> Task:
        """
        作業を更新します
        """
        try:
            existing_task = await self.get_task(task_id)
            if not existing_task:
                raise ResourceNotFoundException(f"作業ID {task_id} は存在しません")
            
            now = datetime.utcnow()
            update_data = {"updated_at": now.isoformat()}
            
            if task_in.field_id is not None:
                field_response = self.supabase.table(self.fields_table).select(
                    "id"
                ).eq(
                    "id", task_in.field_id
                ).execute()
                
                if not field_response.data:
                    raise ValidationException(f"指定された圃場ID {task_in.field_id} は存在しません")
                
                update_data["field_id"] = task_in.field_id
            
            if task_in.task_type is not None:
                update_data["task_type"] = task_in.task_type
            
            if task_in.status is not None:
                update_data["status"] = task_in.status
            
            if task_in.scheduled_date is not None:
                update_data["scheduled_date"] = task_in.scheduled_date.isoformat()
            
            if task_in.completed_date is not None:
                update_data["completed_date"] = task_in.completed_date.isoformat()
            elif task_in.completed_date is None and task_in.status == "completed":
                update_data["completed_date"] = now.isoformat()
            
            if task_in.assigned_to is not None:
                update_data["assigned_to"] = task_in.assigned_to
            
            if task_in.notes is not None:
                update_data["notes"] = task_in.notes
            
            response = self.supabase.table(self.table).update(
                update_data
            ).eq(
                "id", task_id
            ).execute()
            
            if not response.data:
                raise DatabaseOperationException("作業の更新に失敗しました")
            
            updated_task = response.data[0]
            
            if updated_task.get("scheduled_date"):
                updated_task["scheduled_date"] = datetime.fromisoformat(updated_task["scheduled_date"].replace("Z", "+00:00"))
            if updated_task.get("completed_date"):
                updated_task["completed_date"] = datetime.fromisoformat(updated_task["completed_date"].replace("Z", "+00:00"))
            if updated_task.get("created_at"):
                updated_task["created_at"] = datetime.fromisoformat(updated_task["created_at"].replace("Z", "+00:00"))
            if updated_task.get("updated_at"):
                updated_task["updated_at"] = datetime.fromisoformat(updated_task["updated_at"].replace("Z", "+00:00"))
            
            field_response = self.supabase.table(self.fields_table).select(
                "name"
            ).eq(
                "id", updated_task["field_id"]
            ).execute()
            
            task = Task(**updated_task)
            task_dict = task.dict()
            
            if field_response.data:
                task_dict["field_name"] = field_response.data[0]["name"]
            else:
                task_dict["field_name"] = "不明"
            
            return Task(**task_dict)
        except ResourceNotFoundException as e:
            raise e
        except ValidationException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"作業の更新中にエラーが発生しました: {str(e)}")

    async def delete_task(self, task_id: int) -> None:
        """
        作業を削除します
        """
        try:
            existing_task = await self.get_task(task_id)
            if not existing_task:
                raise ResourceNotFoundException(f"作業ID {task_id} は存在しません")
            
            response = self.supabase.table(self.table).delete().eq(
                "id", task_id
            ).execute()
            
            if not response.data:
                raise DatabaseOperationException("作業の削除に失敗しました")
        except ResourceNotFoundException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"作業の削除中にエラーが発生しました: {str(e)}")
