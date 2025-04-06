import json
from typing import List, Optional, Any, Dict, cast
from datetime import datetime

from app.db.session import get_supabase_client
from app.models.crop import Crop, WorkflowStep
from app.schemas.crop import CropCreate, CropUpdate
from app.utils.json_utils import parse_json_string, to_json_string


class CropService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.table = "crops"

    async def get_crops(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[Crop]:
        """
        組織に属する全ての作物を取得します
        """
        response = self.supabase.table(self.table).select("*").eq(
            "organization_id", organization_id
        ).range(skip, skip + limit - 1).execute()
        
        crops = []
        for item in response.data:
            # workflowをJSON文字列からリストに変換（存在する場合）
            if item.get("workflow") and isinstance(item["workflow"], str):
                workflow_data = parse_json_string(item["workflow"])
                if workflow_data:
                    item["workflow"] = self._convert_workflow_data_to_steps(workflow_data)
                
            crops.append(Crop(**item))
        
        return crops

    async def get_crop(self, crop_id: Optional[int]) -> Optional[Crop]:
        """
        特定のIDの作物を取得します
        """
        response = self.supabase.table(self.table).select("*").eq(
            "id", crop_id
        ).limit(1).execute()
        
        if not response.data:
            return None
        
        item = response.data[0]
        # workflowをJSON文字列からリストに変換（存在する場合）
        if item.get("workflow") and isinstance(item["workflow"], str):
            workflow_data = parse_json_string(item["workflow"])
            if workflow_data:
                item["workflow"] = self._convert_workflow_data_to_steps(workflow_data)
        
        return Crop(**item)

    async def create_crop(
        self, crop_in: CropCreate, organization_id: int
    ) -> Crop:
        """
        新しい作物を作成します
        """
        now = datetime.utcnow()
        
        crop_data = {
            "name": crop_in.name,
            "organization_id": organization_id,
            "category": crop_in.category,
            "notes": crop_in.notes,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        # workflowが存在する場合、JSON文字列に変換して追加
        if crop_in.workflow:
            workflow_data = self._convert_workflow_steps_to_data(cast(List[Any], crop_in.workflow))
            crop_data["workflow"] = to_json_string(workflow_data)
        
        response = self.supabase.table(self.table).insert(crop_data).execute()
        
        if not response.data:
            raise Exception("作物の作成に失敗しました")
        
        created_crop = response.data[0]
        
        # workflowをセット（存在する場合）
        if crop_in.workflow:
            created_crop["workflow"] = crop_in.workflow
        
        return Crop(**created_crop)

    async def update_crop(self, crop_id: int, crop_in: CropUpdate) -> Crop:
        """
        作物情報を更新します
        """
        now = datetime.utcnow()
        
        # 更新するフィールドを準備
        update_data = {"updated_at": now.isoformat()}
        
        if crop_in.name is not None:
            update_data["name"] = crop_in.name
        
        if crop_in.category is not None:
            update_data["category"] = crop_in.category
        
        if crop_in.workflow is not None:
            # workflowをJSON文字列に変換
            workflow_data = self._convert_workflow_steps_to_data(cast(List[Any], crop_in.workflow))
            update_data["workflow"] = to_json_string(workflow_data)
        
        if crop_in.notes is not None:
            update_data["notes"] = crop_in.notes
        
        response = self.supabase.table(self.table).update(
            update_data
        ).eq("id", crop_id).execute()
        
        if not response.data:
            raise Exception("作物の更新に失敗しました")
        
        updated_crop = response.data[0]
        
        # workflowをJSON文字列からリストに変換（存在する場合）
        if updated_crop.get("workflow") and isinstance(updated_crop["workflow"], str):
            workflow_data = parse_json_string(updated_crop["workflow"])
            if workflow_data:
                updated_crop["workflow"] = self._convert_workflow_data_to_steps(workflow_data)
        
        return Crop(**updated_crop)

    async def delete_crop(self, crop_id: int) -> bool:
        """
        作物を削除します
        """
        response = self.supabase.table(self.table).delete().eq("id", crop_id).execute()
        
        if not response.data:
            return False
        
        return True
    
    def _convert_workflow_data_to_steps(self, workflow_data: List[dict]) -> List[WorkflowStep]:
        """
        JSONデータからWorkflowStepオブジェクトのリストに変換します
        子フローも再帰的に処理します
        """
        steps = []
        for step_data in workflow_data:
            # 古い形式（文字列のみ）の場合の互換性処理
            if isinstance(step_data, str):
                steps.append(WorkflowStep(name=step_data, days=None))
                continue
                
            # 子フローがある場合は再帰的に処理
            sub_steps = []
            if step_data.get("sub_steps"):
                sub_steps = self._convert_workflow_data_to_steps(step_data["sub_steps"])
                
            # WorkflowStepオブジェクトを作成
            step = WorkflowStep(
                name=step_data["name"],
                days=step_data.get("days"),
                sub_steps=sub_steps
            )
            steps.append(step)
            
        return steps
    
    def _convert_workflow_steps_to_data(self, workflow_steps: List[Any]) -> List[Dict[str, Any]]:
        """
        WorkflowStepオブジェクトのリストをJSONデータに変換します
        子フローも再帰的に処理します
        """
        data = []
        for step in workflow_steps:
            step_data = step.dict(exclude_none=True)
            
            # 子フローがある場合は再帰的に処理
            if step.sub_steps:
                step_data["sub_steps"] = self._convert_workflow_steps_to_data(cast(List[Any], step.sub_steps))
            elif "sub_steps" in step_data and not step_data["sub_steps"]:
                # 空のリストの場合は削除（JSONを小さくするため）
                del step_data["sub_steps"]
                
            data.append(step_data)
            
        return data
