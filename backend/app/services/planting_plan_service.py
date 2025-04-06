import json
from typing import List, Optional, Dict, Any, cast, Tuple
from datetime import datetime, date, timedelta

from app.db.session import get_supabase_client
from app.models.planting_plan import PlantingPlan, PlantingPlanField, WorkflowInstance
from app.models.crop import WorkflowStep
from app.schemas.planting_plan import PlantingPlanCreate, PlantingPlanUpdate
from app.services.crop_service import CropService
from app.utils.date_utils import convert_iso_to_date
from app.utils.json_utils import parse_json_string, to_json_string
from app.exceptions.service_exceptions import (
    DatabaseOperationException,
    ResourceNotFoundException,
    ValidationException,
    WorkflowException
)


class PlantingPlanService:
    def __init__(self, crop_service: Optional[CropService] = None):
        self.supabase = get_supabase_client()
        self.plan_table = "planting_plans"
        self.field_table = "planting_plan_fields"
        self.workflow_table = "workflow_instances"
        self.crop_service = crop_service or CropService()

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
                    instance_data["planned_date"] = convert_iso_to_date(instance_data["planned_date"])
                if instance_data.get("actual_date"):
                    instance_data["actual_date"] = convert_iso_to_date(instance_data["actual_date"])
                
                plan.workflow_instances.append(WorkflowInstance(**instance_data))
            
            plans.append(plan)
        
        return plans

    async def get_planting_plan(self, plan_id: Optional[int]) -> Optional[PlantingPlan]:
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
                instance_data["planned_date"] = convert_iso_to_date(instance_data["planned_date"])
            if instance_data.get("actual_date"):
                instance_data["actual_date"] = convert_iso_to_date(instance_data["actual_date"])
            
            plan.workflow_instances.append(WorkflowInstance(**instance_data))
        
        return plan

    async def create_planting_plan(
        self, plan_in: PlantingPlanCreate, organization_id: int
    ) -> PlantingPlan:
        """
        新しい作付け計画を作成します
        
        Args:
            plan_in: 作成する作付け計画データ
            organization_id: 組織ID
            
        Returns:
            作成された作付け計画
            
        Raises:
            ValidationException: 入力データが不正な場合
            DatabaseOperationException: データベース操作に失敗した場合
        """
        if not plan_in.plan_name:
            raise ValidationException("作付け計画名は必須です")
            
        if not plan_in.crop_id:
            raise ValidationException("作物IDは必須です")
            
        try:
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
                raise DatabaseOperationException("作付け計画の作成に失敗しました")
            
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
                
                try:
                    field_response = self.supabase.table(self.field_table).insert(field_data).execute()
                    
                    if field_response.data:
                        fields.append(PlantingPlanField(**field_response.data[0]))
                except Exception as e:
                    continue
            
            created_plan.fields = fields
            
            # 作業インスタンスを生成・保存（作物マスターの作業フローから）
            try:
                if plan_in.workflow_instances:
                    # ユーザーが指定した作業インスタンスを使用
                    await self._create_workflow_instances(created_plan.id, plan_in.workflow_instances)
                else:
                    # 作物マスターの作業フローから自動生成
                    await self._generate_workflow_instances_from_crop(created_plan.id, plan_in.crop_id, plan_in.planting_date)
            except (ResourceNotFoundException, ValidationException) as e:
                raise
            except Exception as e:
                pass
            
            # 作成した作付け計画を完全な形で取得して返す
            return await self.get_planting_plan(created_plan.id)
        except (ResourceNotFoundException, ValidationException) as e:
            raise
        except Exception as e:
            raise DatabaseOperationException(
                f"作付け計画の作成に失敗しました: {str(e)}",
                {"plan_name": plan_in.plan_name, "crop_id": plan_in.crop_id, "error": str(e)}
            )

    async def update_planting_plan(
        self, plan_id: int, plan_in: PlantingPlanUpdate
    ) -> PlantingPlan:
        """
        作付け計画を更新します
        
        Args:
            plan_id: 更新する作付け計画のID
            plan_in: 更新データ
            
        Returns:
            更新された作付け計画
            
        Raises:
            ResourceNotFoundException: 作付け計画が見つからない場合
            ValidationException: 入力データが不正な場合
            DatabaseOperationException: データベース操作に失敗した場合
        """
        existing_plan = await self.get_planting_plan(plan_id)
        if not existing_plan:
            raise ResourceNotFoundException(
                f"作付け計画ID {plan_id} が見つかりません",
                {"plan_id": plan_id}
            )
            
        try:
            now = datetime.utcnow()
            
            # 更新するフィールドを準備
            update_data = {"updated_at": now.isoformat()}
            
            if plan_in.plan_name is not None:
                update_data["plan_name"] = plan_in.plan_name
            
            if plan_in.crop_id is not None:
                update_data["crop_id"] = str(plan_in.crop_id)
            
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
                raise DatabaseOperationException(
                    "作付け計画の更新に失敗しました",
                    {"plan_id": plan_id}
                )
            
            # 更新後の作付け計画を取得して返す
            return await self.get_planting_plan(plan_id)
        except (ResourceNotFoundException, ValidationException) as e:
            raise
        except Exception as e:
            raise DatabaseOperationException(
                f"作付け計画の更新に失敗しました: {str(e)}",
                {"plan_id": plan_id, "error": str(e)}
            )

    async def delete_planting_plan(self, plan_id: int) -> bool:
        """
        作付け計画を削除します（関連する圃場情報と作業インスタンスも削除）
        
        Args:
            plan_id: 削除する作付け計画のID
            
        Returns:
            削除が成功したかどうか
            
        Raises:
            ResourceNotFoundException: 作付け計画が見つからない場合
            DatabaseOperationException: データベース操作に失敗した場合
        """
        existing_plan = await self.get_planting_plan(plan_id)
        if not existing_plan:
            raise ResourceNotFoundException(
                f"作付け計画ID {plan_id} が見つかりません",
                {"plan_id": plan_id}
            )
            
        try:
            # 関連する圃場情報を削除
            self.supabase.table(self.field_table).delete().eq("planting_plan_id", plan_id).execute()
            
            # 関連する作業インスタンスを削除
            self.supabase.table(self.workflow_table).delete().eq("planting_plan_id", plan_id).execute()
            
            # 作付け計画を削除
            response = self.supabase.table(self.plan_table).delete().eq("id", plan_id).execute()
            
            if not response.data:
                raise DatabaseOperationException(
                    "作付け計画の削除に失敗しました",
                    {"plan_id": plan_id}
                )
            
            return True
        except (ResourceNotFoundException, ValidationException) as e:
            raise
        except Exception as e:
            raise DatabaseOperationException(
                f"作付け計画の削除に失敗しました: {str(e)}",
                {"plan_id": plan_id, "error": str(e)}
            )

    async def update_workflow_instance(
        self, instance_id: int, instance_data: Dict[str, Any]
    ) -> WorkflowInstance:
        """
        作業インスタンスを更新します
        
        Args:
            instance_id: 更新する作業インスタンスのID
            instance_data: 更新データ
            
        Returns:
            更新された作業インスタンス
            
        Raises:
            ResourceNotFoundException: 作業インスタンスが見つからない場合
            ValidationException: 入力データが不正な場合
            DatabaseOperationException: データベース操作に失敗した場合
        """
        instance_response = self.supabase.table(self.workflow_table).select("*").eq(
            "id", instance_id
        ).limit(1).execute()
        
        if not instance_response.data:
            raise ResourceNotFoundException(
                f"作業インスタンスID {instance_id} が見つかりません",
                {"instance_id": instance_id}
            )
            
        try:
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
                raise DatabaseOperationException(
                    "作業インスタンスの更新に失敗しました",
                    {"instance_id": instance_id}
                )
            
            instance_data = response.data[0]
            
            # 日付型に変換
            if instance_data.get("planned_date"):
                instance_data["planned_date"] = convert_iso_to_date(instance_data["planned_date"])
            if instance_data.get("actual_date"):
                instance_data["actual_date"] = convert_iso_to_date(instance_data["actual_date"])
            
            return WorkflowInstance(**instance_data)
        except (ResourceNotFoundException, ValidationException) as e:
            raise
        except Exception as e:
            raise DatabaseOperationException(
                f"作業インスタンスの更新に失敗しました: {str(e)}",
                {"instance_id": instance_id, "error": str(e)}
            )

    async def _create_workflow_instances(
        self, plan_id: Optional[int], instances: List[Any]
    ) -> List[WorkflowInstance]:
        """
        作業インスタンスを作成します
        
        Args:
            plan_id: 作付け計画ID
            instances: 作成する作業インスタンスのリスト
            
        Returns:
            作成された作業インスタンスのリスト
            
        Raises:
            ValidationException: 入力データが不正な場合
            DatabaseOperationException: データベース操作に失敗した場合
        """
        if not instances:
            return []
            
        if plan_id is None:
            raise ValidationException("作付け計画IDが指定されていません")
            
        now = datetime.utcnow()
        created_instances = []
        
        for instance in instances:
            try:
                instance_data = {
                    "planting_plan_id": plan_id,
                    "step_name": instance.step_name,
                    "status": instance.status or "未着手",
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
                        instance_data["planned_date"] = convert_iso_to_date(instance_data["planned_date"])
                    
                    created_instances.append(WorkflowInstance(**instance_data))
            except Exception as e:
                continue
        
        if not created_instances and instances:
            raise DatabaseOperationException(
                "作業インスタンスの作成に失敗しました",
                {"plan_id": plan_id}
            )
            
        return created_instances

    async def _get_crop_with_workflow(self, crop_id: Optional[int]) -> Tuple[bool, Optional[Any]]:
        """
        作物マスターとそのワークフローを取得します
        
        Args:
            crop_id: 作物ID
            
        Returns:
            (成功フラグ, 作物データ)のタプル
        
        Raises:
            ResourceNotFoundException: 作物が見つからない場合
        """
        if crop_id is None:
            raise ValidationException("作物IDが指定されていません")
            
        crop = await self.crop_service.get_crop(crop_id)
        if not crop:
            raise ResourceNotFoundException(
                f"作物ID {crop_id} が見つかりません", 
                {"crop_id": crop_id}
            )
        
        if not crop.workflow:
            return False, crop
            
        return True, crop
    
    async def _create_parent_workflow_instance(
        self, 
        plan_id: Optional[int], 
        step: WorkflowStep, 
        planting_date: Optional[date]
    ) -> Tuple[bool, Optional[int], Optional[Dict[str, Any]]]:
        """
        親ワークフローインスタンスを作成します
        
        Args:
            plan_id: 作付け計画ID
            step: ワークフローステップ
            planting_date: 定植日
            
        Returns:
            (成功フラグ, インスタンスID, インスタンスデータ)のタプル
        """
        now = datetime.utcnow()
        
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
        
        try:
            # 親作業インスタンスを保存
            parent_response = self.supabase.table(self.workflow_table).insert(parent_instance_data).execute()
            
            if not parent_response.data:
                return False, None, None
            
            parent_instance = parent_response.data[0]
            parent_id = parent_instance["id"]
            
            # 日付型に変換
            if parent_instance.get("planned_date"):
                parent_instance["planned_date"] = convert_iso_to_date(parent_instance["planned_date"])
                
            return True, parent_id, parent_instance
        except Exception as e:
            raise DatabaseOperationException(
                f"親ワークフローインスタンスの作成に失敗しました: {str(e)}",
                {"step_name": step.name, "error": str(e)}
            )
    
    async def _create_sub_workflow_instances(
        self, 
        plan_id: Optional[int], 
        parent_id: Optional[int], 
        sub_steps: List[WorkflowStep], 
        planting_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        """
        子ワークフローインスタンスを作成します
        
        Args:
            plan_id: 作付け計画ID
            parent_id: 親ワークフローインスタンスID
            sub_steps: 子ワークフローステップのリスト
            planting_date: 定植日
            
        Returns:
            作成された子ワークフローインスタンスのリスト
        """
        now = datetime.utcnow()
        created_sub_instances = []
        
        for sub_step in sub_steps:
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
            
            try:
                # 子作業インスタンスを保存
                sub_response = self.supabase.table(self.workflow_table).insert(sub_instance_data).execute()
                
                if sub_response.data:
                    sub_instance = sub_response.data[0]
                    
                    # 日付型に変換
                    if sub_instance.get("planned_date"):
                        sub_instance["planned_date"] = convert_iso_to_date(sub_instance["planned_date"])
                    
                    created_sub_instances.append(sub_instance)
            except Exception as e:
                continue
                
        return created_sub_instances
    
    async def _generate_workflow_instances_from_crop(
        self, plan_id: Optional[int], crop_id: Optional[int], planting_date: Optional[date]
    ) -> List[WorkflowInstance]:
        """
        作物マスターの作業フローから作業インスタンスを生成します
        
        Args:
            plan_id: 作付け計画ID
            crop_id: 作物ID
            planting_date: 定植日
            
        Returns:
            作成された作業インスタンスのリスト
            
        Raises:
            ResourceNotFoundException: 作物が見つからない場合
            DatabaseOperationException: データベース操作に失敗した場合
        """
        try:
            # 作物マスターから作業フローを取得
            has_workflow, crop = await self._get_crop_with_workflow(crop_id)
            if not has_workflow or not crop or not crop.workflow:
                return []
            
            created_instances = []
            parent_id_mapping = {}  # 親作業インスタンスのIDマッピング
            
            # 作業フローから作業インスタンスを生成
            for step in crop.workflow:
                # 親作業インスタンスを作成
                success, parent_id, parent_instance = await self._create_parent_workflow_instance(
                    plan_id, step, planting_date
                )
                
                if not success:
                    continue
                    
                parent_id_mapping[step.name] = parent_id
                created_instances.append(WorkflowInstance(**parent_instance))
                
                # 子作業がある場合は子作業インスタンスも作成
                if step.sub_steps:
                    sub_instances = await self._create_sub_workflow_instances(
                        plan_id, parent_id, step.sub_steps, planting_date
                    )
                    
                    for sub_instance in sub_instances:
                        created_instances.append(WorkflowInstance(**sub_instance))
            
            return created_instances
        except (ResourceNotFoundException, ValidationException) as e:
            raise
        except Exception as e:
            raise DatabaseOperationException(
                f"ワークフローインスタンスの生成に失敗しました: {str(e)}",
                {"plan_id": plan_id, "crop_id": crop_id, "error": str(e)}
            )
