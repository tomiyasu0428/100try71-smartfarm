import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.db.session import get_supabase_client
from app.models.planting_plan import PlantingPlan, PlantingPlanField, WorkflowInstance
from app.schemas.planting_plan import PlantingPlanCreate, PlantingPlanUpdate
from app.services.crop_service import CropService


class PlantingPlanService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.plan_table = "planting_plans"
        self.field_table = "planting_plan_fields"
        self.workflow_table = "workflow_instances"
        self.crop_service = CropService()

    async def get_planting_plans(
        self, organization_id: int, skip: int = 0, limit: int = 100
    ) -> List[PlantingPlan]:
        """
        組織に属する全ての作付け計画を取得します
        """
        response = self.supabase.table(self.plan_table).select("*").eq(
            "organization_id", organization_id
        ).range(skip, skip + limit - 1).execute()
        
        plans = []
        for plan_data in response.data:
            plan = PlantingPlan(**plan_data)
            
            # 関連する圃場情報を取得
            fields_response = self.supabase.table(self.field_table).select("*").eq(
                "planting_plan_id", plan.id
            ).order("sequence").execute()
            
            plan.fields = [PlantingPlanField(**field_data) for field_data in fields_response.data]
            
            # 関連する作業インスタンスを取得
            workflow_response = self.supabase.table(self.workflow_table).select("*").eq(
                "planting_plan_id", plan.id
            ).execute()
            
            plan.workflow_instances = []
            for instance_data in workflow_response.data:
                # 日付型に変換
                if instance_data.get("planned_date"):
                    instance_data["planned_date"] = datetime.fromisoformat(
                        instance_data["planned_date"].replace("Z", "+00:00")
                    ).date()
                if instance_data.get("actual_date"):
                    instance_data["actual_date"] = datetime.fromisoformat(
                        instance_data["actual_date"].replace("Z", "+00:00")
                    ).date()
                
                plan.workflow_instances.append(WorkflowInstance(**instance_data))
            
            plans.append(plan)
        
        return plans

    async def get_planting_plan(self, plan_id: int) -> Optional[PlantingPlan]:
        """
        特定のIDの作付け計画を取得します
        """
        response = self.supabase.table(self.plan_table).select("*").eq(
            "id", plan_id
        ).limit(1).execute()
        
        if not response.data:
            return None
        
        plan_data = response.data[0]
        plan = PlantingPlan(**plan_data)
        
        # 関連する圃場情報を取得
        fields_response = self.supabase.table(self.field_table).select("*").eq(
            "planting_plan_id", plan.id
        ).order("sequence").execute()
        
        plan.fields = [PlantingPlanField(**field_data) for field_data in fields_response.data]
        
        # 関連する作業インスタンスを取得
        workflow_response = self.supabase.table(self.workflow_table).select("*").eq(
            "planting_plan_id", plan.id
        ).execute()
        
        plan.workflow_instances = []
        for instance_data in workflow_response.data:
            # 日付型に変換
            if instance_data.get("planned_date"):
                instance_data["planned_date"] = datetime.fromisoformat(
                    instance_data["planned_date"].replace("Z", "+00:00")
                ).date()
            if instance_data.get("actual_date"):
                instance_data["actual_date"] = datetime.fromisoformat(
                    instance_data["actual_date"].replace("Z", "+00:00")
                ).date()
            
            plan.workflow_instances.append(WorkflowInstance(**instance_data))
        
        return plan

    async def create_planting_plan(
        self, plan_in: PlantingPlanCreate, organization_id: int
    ) -> PlantingPlan:
        """
        新しい作付け計画を作成します
        """
        now = datetime.utcnow()
        
        # 作付け計画の基本情報を作成
        plan_data = {
            "plan_name": plan_in.plan_name,
            "crop_id": plan_in.crop_id,
            "organization_id": organization_id,
            "season": plan_in.season,
            "status": plan_in.status,
            "notes": plan_in.notes,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        # 日付情報があれば追加
        if plan_in.planting_date:
            plan_data["planting_date"] = plan_in.planting_date.isoformat()
        if plan_in.harvest_date:
            plan_data["harvest_date"] = plan_in.harvest_date.isoformat()
        
        # 作付け計画を保存
        plan_response = self.supabase.table(self.plan_table).insert(plan_data).execute()
        
        if not plan_response.data:
            raise Exception("作付け計画の作成に失敗しました")
        
        created_plan = PlantingPlan(**plan_response.data[0])
        
        # 圃場情報を保存
        fields = []
        for field_in in plan_in.fields:
            field_data = {
                "planting_plan_id": created_plan.id,
                "field_id": field_in.field_id,
                "sequence": field_in.sequence,
                "area": field_in.area,
                "notes": field_in.notes,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            field_response = self.supabase.table(self.field_table).insert(field_data).execute()
            
            if field_response.data:
                fields.append(PlantingPlanField(**field_response.data[0]))
        
        created_plan.fields = fields
        
        # 作業インスタンスを生成・保存（作物マスターの作業フローから）
        if plan_in.workflow_instances:
            # ユーザーが指定した作業インスタンスを使用
            await self._create_workflow_instances(created_plan.id, plan_in.workflow_instances)
        else:
            # 作物マスターの作業フローから自動生成
            await self._generate_workflow_instances_from_crop(created_plan.id, plan_in.crop_id, plan_in.planting_date)
        
        # 作成した作付け計画を完全な形で取得して返す
        return await self.get_planting_plan(created_plan.id)

    async def update_planting_plan(
        self, plan_id: int, plan_in: PlantingPlanUpdate
    ) -> PlantingPlan:
        """
        作付け計画を更新します
        """
        now = datetime.utcnow()
        
        # 更新するフィールドを準備
        update_data = {"updated_at": now.isoformat()}
        
        if plan_in.plan_name is not None:
            update_data["plan_name"] = plan_in.plan_name
        
        if plan_in.crop_id is not None:
            update_data["crop_id"] = plan_in.crop_id
        
        if plan_in.season is not None:
            update_data["season"] = plan_in.season
        
        if plan_in.status is not None:
            update_data["status"] = plan_in.status
        
        if plan_in.notes is not None:
            update_data["notes"] = plan_in.notes
        
        if plan_in.planting_date is not None:
            update_data["planting_date"] = plan_in.planting_date.isoformat()
        
        if plan_in.harvest_date is not None:
            update_data["harvest_date"] = plan_in.harvest_date.isoformat()
        
        # 作付け計画を更新
        response = self.supabase.table(self.plan_table).update(
            update_data
        ).eq("id", plan_id).execute()
        
        if not response.data:
            raise Exception("作付け計画の更新に失敗しました")
        
        # 更新後の作付け計画を取得して返す
        return await self.get_planting_plan(plan_id)

    async def delete_planting_plan(self, plan_id: int) -> bool:
        """
        作付け計画を削除します（関連する圃場情報と作業インスタンスも削除）
        """
        # 関連する圃場情報を削除
        self.supabase.table(self.field_table).delete().eq("planting_plan_id", plan_id).execute()
        
        # 関連する作業インスタンスを削除
        self.supabase.table(self.workflow_table).delete().eq("planting_plan_id", plan_id).execute()
        
        # 作付け計画を削除
        response = self.supabase.table(self.plan_table).delete().eq("id", plan_id).execute()
        
        if not response.data:
            return False
        
        return True

    async def update_workflow_instance(
        self, instance_id: int, instance_data: Dict[str, Any]
    ) -> WorkflowInstance:
        """
        作業インスタンスを更新します
        """
        now = datetime.utcnow()
        
        # 更新するフィールドを準備
        update_data = {"updated_at": now.isoformat()}
        
        for key, value in instance_data.items():
            if value is not None:
                if isinstance(value, date):
                    update_data[key] = value.isoformat()
                else:
                    update_data[key] = value
        
        # 作業インスタンスを更新
        response = self.supabase.table(self.workflow_table).update(
            update_data
        ).eq("id", instance_id).execute()
        
        if not response.data:
            raise Exception("作業インスタンスの更新に失敗しました")
        
        instance_data = response.data[0]
        
        # 日付型に変換
        if instance_data.get("planned_date"):
            instance_data["planned_date"] = datetime.fromisoformat(
                instance_data["planned_date"].replace("Z", "+00:00")
            ).date()
        if instance_data.get("actual_date"):
            instance_data["actual_date"] = datetime.fromisoformat(
                instance_data["actual_date"].replace("Z", "+00:00")
            ).date()
        
        return WorkflowInstance(**instance_data)

    async def _create_workflow_instances(
        self, plan_id: int, instances: List[Any]
    ) -> List[WorkflowInstance]:
        """
        作業インスタンスを作成します
        """
        now = datetime.utcnow()
        created_instances = []
        
        for instance in instances:
            instance_data = {
                "planting_plan_id": plan_id,
                "step_name": instance.step_name,
                "status": instance.status,
                "notes": instance.notes,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            if instance.planned_date:
                instance_data["planned_date"] = instance.planned_date.isoformat()
            
            if instance.days_from_planting is not None:
                instance_data["days_from_planting"] = instance.days_from_planting
            
            if instance.parent_instance_id:
                instance_data["parent_instance_id"] = instance.parent_instance_id
            
            response = self.supabase.table(self.workflow_table).insert(instance_data).execute()
            
            if response.data:
                instance_data = response.data[0]
                
                # 日付型に変換
                if instance_data.get("planned_date"):
                    instance_data["planned_date"] = datetime.fromisoformat(
                        instance_data["planned_date"].replace("Z", "+00:00")
                    ).date()
                
                created_instances.append(WorkflowInstance(**instance_data))
        
        return created_instances

    async def _generate_workflow_instances_from_crop(
        self, plan_id: int, crop_id: int, planting_date: Optional[date]
    ) -> List[WorkflowInstance]:
        """
        作物マスターの作業フローから作業インスタンスを生成します
        """
        # 作物マスターから作業フローを取得
        crop = await self.crop_service.get_crop(crop_id)
        if not crop or not crop.workflow:
            return []
        
        now = datetime.utcnow()
        created_instances = []
        
        # 親作業インスタンスのIDマッピング（子作業のparent_instance_idを設定するため）
        parent_id_mapping = {}
        
        # 作業フローから作業インスタンスを生成
        for step in crop.workflow:
            # 親作業インスタンスを作成
            parent_instance_data = {
                "planting_plan_id": plan_id,
                "step_name": step.name,
                "status": "未着手",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            
            # 日数情報があり、定植日も指定されている場合は予定日を計算
            if step.days is not None and planting_date:
                planned_date = planting_date + timedelta(days=step.days)
                parent_instance_data["planned_date"] = planned_date.isoformat()
                parent_instance_data["days_from_planting"] = step.days
            
            # 親作業インスタンスを保存
            parent_response = self.supabase.table(self.workflow_table).insert(parent_instance_data).execute()
            
            if not parent_response.data:
                continue
            
            parent_instance = parent_response.data[0]
            parent_id = parent_instance["id"]
            parent_id_mapping[step.name] = parent_id
            
            # 日付型に変換
            if parent_instance.get("planned_date"):
                parent_instance["planned_date"] = datetime.fromisoformat(
                    parent_instance["planned_date"].replace("Z", "+00:00")
                ).date()
            
            created_instances.append(WorkflowInstance(**parent_instance))
            
            # 子作業がある場合は子作業インスタンスも作成
            if step.sub_steps:
                for sub_step in step.sub_steps:
                    sub_instance_data = {
                        "planting_plan_id": plan_id,
                        "step_name": sub_step.name,
                        "parent_instance_id": parent_id,
                        "status": "未着手",
                        "created_at": now.isoformat(),
                        "updated_at": now.isoformat()
                    }
                    
                    # 日数情報があり、定植日も指定されている場合は予定日を計算
                    if sub_step.days is not None and planting_date:
                        sub_planned_date = planting_date + timedelta(days=sub_step.days)
                        sub_instance_data["planned_date"] = sub_planned_date.isoformat()
                        sub_instance_data["days_from_planting"] = sub_step.days
                    
                    # 子作業インスタンスを保存
                    sub_response = self.supabase.table(self.workflow_table).insert(sub_instance_data).execute()
                    
                    if sub_response.data:
                        sub_instance = sub_response.data[0]
                        
                        # 日付型に変換
                        if sub_instance.get("planned_date"):
                            sub_instance["planned_date"] = datetime.fromisoformat(
                                sub_instance["planned_date"].replace("Z", "+00:00")
                            ).date()
                        
                        created_instances.append(WorkflowInstance(**sub_instance))
        
        return created_instances
