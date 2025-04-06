from typing import List, Optional
from datetime import datetime
import json

from app.db.session import get_supabase_client
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException
)


class ResourceService:
    def __init__(self, supabase=None):
        self.supabase = supabase or get_supabase_client()
        self.table = "resources"

    async def get_resources(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Resource]:
        """
        組織に属する全ての資材・農機を取得します
        """
        try:
            response = self.supabase.table(self.table).select(
                "*"
            ).eq(
                "organization_id", organization_id
            ).order(
                "name", desc=False
            ).range(
                skip, skip + limit - 1
            ).execute()
            
            if not response.data:
                return []
            
            resources = []
            for item in response.data:
                if item.get("created_at"):
                    item["created_at"] = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                if item.get("updated_at"):
                    item["updated_at"] = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                
                resources.append(Resource(**item))
            
            return resources
        except Exception as e:
            raise DatabaseOperationException(f"資材・農機の取得中にエラーが発生しました: {str(e)}")

    async def get_resource(self, resource_id: int) -> Optional[Resource]:
        """
        特定の資材・農機を取得します
        """
        try:
            response = self.supabase.table(self.table).select(
                "*"
            ).eq(
                "id", resource_id
            ).execute()
            
            if not response.data:
                return None
            
            item = response.data[0]
            
            if item.get("created_at"):
                item["created_at"] = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            if item.get("updated_at"):
                item["updated_at"] = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            
            return Resource(**item)
        except Exception as e:
            raise DatabaseOperationException(f"資材・農機の取得中にエラーが発生しました: {str(e)}")

    async def create_resource(
        self, resource_in: ResourceCreate, organization_id: int
    ) -> Resource:
        """
        新しい資材・農機を作成します
        """
        try:
            now = datetime.utcnow()
            
            resource_data = {
                "organization_id": organization_id,
                "name": resource_in.name,
                "resource_type": resource_in.resource_type,
                "status": resource_in.status,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            if resource_in.quantity is not None:
                resource_data["quantity"] = resource_in.quantity
            
            if resource_in.unit is not None:
                resource_data["unit"] = resource_in.unit
            
            if resource_in.location is not None:
                resource_data["location"] = resource_in.location
            
            if resource_in.notes is not None:
                resource_data["notes"] = resource_in.notes
            
            response = self.supabase.table(self.table).insert(resource_data).execute()
            
            if not response.data:
                raise DatabaseOperationException("資材・農機の作成に失敗しました")
            
            created_resource = response.data[0]
            
            if created_resource.get("created_at"):
                created_resource["created_at"] = datetime.fromisoformat(created_resource["created_at"].replace("Z", "+00:00"))
            if created_resource.get("updated_at"):
                created_resource["updated_at"] = datetime.fromisoformat(created_resource["updated_at"].replace("Z", "+00:00"))
            
            return Resource(**created_resource)
        except Exception as e:
            raise DatabaseOperationException(f"資材・農機の作成中にエラーが発生しました: {str(e)}")

    async def update_resource(
        self, resource_id: int, resource_in: ResourceUpdate
    ) -> Resource:
        """
        資材・農機を更新します
        """
        try:
            existing_resource = await self.get_resource(resource_id)
            if not existing_resource:
                raise ResourceNotFoundException(f"資材・農機ID {resource_id} は存在しません")
            
            now = datetime.utcnow()
            update_data = {"updated_at": now.isoformat()}
            
            if resource_in.name is not None:
                update_data["name"] = resource_in.name
            
            if resource_in.resource_type is not None:
                update_data["resource_type"] = resource_in.resource_type
            
            if resource_in.quantity is not None:
                update_data["quantity"] = resource_in.quantity
            
            if resource_in.unit is not None:
                update_data["unit"] = resource_in.unit
            
            if resource_in.status is not None:
                update_data["status"] = resource_in.status
            
            if resource_in.location is not None:
                update_data["location"] = resource_in.location
            
            if resource_in.notes is not None:
                update_data["notes"] = resource_in.notes
            
            response = self.supabase.table(self.table).update(
                update_data
            ).eq(
                "id", resource_id
            ).execute()
            
            if not response.data:
                raise DatabaseOperationException("資材・農機の更新に失敗しました")
            
            updated_resource = response.data[0]
            
            if updated_resource.get("created_at"):
                updated_resource["created_at"] = datetime.fromisoformat(updated_resource["created_at"].replace("Z", "+00:00"))
            if updated_resource.get("updated_at"):
                updated_resource["updated_at"] = datetime.fromisoformat(updated_resource["updated_at"].replace("Z", "+00:00"))
            
            return Resource(**updated_resource)
        except ResourceNotFoundException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"資材・農機の更新中にエラーが発生しました: {str(e)}")

    async def delete_resource(self, resource_id: int) -> None:
        """
        資材・農機を削除します
        """
        try:
            existing_resource = await self.get_resource(resource_id)
            if not existing_resource:
                raise ResourceNotFoundException(f"資材・農機ID {resource_id} は存在しません")
            
            response = self.supabase.table(self.table).delete().eq(
                "id", resource_id
            ).execute()
            
            if not response.data:
                raise DatabaseOperationException("資材・農機の削除に失敗しました")
        except ResourceNotFoundException as e:
            raise e
        except Exception as e:
            raise DatabaseOperationException(f"資材・農機の削除中にエラーが発生しました: {str(e)}")
