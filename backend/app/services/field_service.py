import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db.session import get_supabase_client
from app.models.field import Field
from app.schemas.field import FieldCreate, FieldUpdate, GeoCoordinate


class FieldService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.table = "fields"

    async def get_fields(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Field]:
        """
        組織に属する全ての圃場を取得します
        """
        response = self.supabase.table(self.table).select("*").eq(
            "organization_id", organization_id
        ).range(skip, skip + limit - 1).execute()
        
        fields = []
        for item in response.data:
            # coordinatesをJSON文字列からリストに変換
            coordinates_list = json.loads(item["coordinates"])
            item["coordinates"] = coordinates_list
            fields.append(Field(**item))
        
        return fields

    async def get_field(self, field_id: int) -> Optional[Field]:
        """
        特定のIDの圃場を取得します
        """
        response = self.supabase.table(self.table).select("*").eq(
            "id", field_id
        ).limit(1).execute()
        
        if not response.data:
            return None
        
        item = response.data[0]
        # coordinatesをJSON文字列からリストに変換
        coordinates_list = json.loads(item["coordinates"])
        item["coordinates"] = coordinates_list
        
        return Field(**item)

    async def create_field(
        self, field_in: FieldCreate, user_id: str, organization_id: int
    ) -> Field:
        """
        新しい圃場を作成します
        """
        now = datetime.utcnow()
        
        # coordinatesをJSON文字列に変換
        coordinates_json = json.dumps([coord.dict() for coord in field_in.coordinates])
        
        field_data = {
            "name": field_in.name,
            "organization_id": organization_id,
            "user_id": user_id,
            "coordinates": coordinates_json,
            "area": field_in.area,
            "soil_type": field_in.soil_type,
            "crop_type": field_in.crop_type,
            "notes": field_in.notes,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        response = self.supabase.table(self.table).insert(field_data).execute()
        
        if not response.data:
            raise Exception("圃場の作成に失敗しました")
        
        created_field = response.data[0]
        # coordinatesをJSON文字列からリストに変換
        created_field["coordinates"] = field_in.coordinates
        
        return Field(**created_field)

    async def update_field(self, field_id: int, field_in: FieldUpdate) -> Field:
        """
        圃場情報を更新します
        """
        now = datetime.utcnow()
        
        # 更新するフィールドを準備
        update_data = {"updated_at": now.isoformat()}
        
        if field_in.name is not None:
            update_data["name"] = field_in.name
        
        if field_in.coordinates is not None:
            # coordinatesをJSON文字列に変換
            update_data["coordinates"] = json.dumps([coord.dict() for coord in field_in.coordinates])
        
        if field_in.area is not None:
            update_data["area"] = field_in.area
        
        if field_in.soil_type is not None:
            update_data["soil_type"] = field_in.soil_type
        
        if field_in.crop_type is not None:
            update_data["crop_type"] = field_in.crop_type
        
        if field_in.notes is not None:
            update_data["notes"] = field_in.notes
        
        response = self.supabase.table(self.table).update(
            update_data
        ).eq("id", field_id).execute()
        
        if not response.data:
            raise Exception("圃場の更新に失敗しました")
        
        updated_field = response.data[0]
        # coordinatesをJSON文字列からリストに変換
        coordinates_list = json.loads(updated_field["coordinates"])
        updated_field["coordinates"] = coordinates_list
        
        return Field(**updated_field)

    async def delete_field(self, field_id: int) -> None:
        """
        圃場を削除します
        """
        self.supabase.table(self.table).delete().eq("id", field_id).execute()
