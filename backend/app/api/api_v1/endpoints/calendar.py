from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date, datetime, timedelta
from app.api.deps import get_current_user, get_planting_plan_service
from app.services.planting_plan_service import PlantingPlanService
from app.exceptions.service_exceptions import DatabaseOperationException
from pydantic import BaseModel

router = APIRouter()

class CalendarEvent(BaseModel):
    """カレンダーイベントモデル"""
    id: str
    title: str
    start: str
    end: Optional[str] = None
    allDay: bool = True
    type: str  # 'planting', 'harvest', 'workflow'
    planId: Optional[int] = None
    instanceId: Optional[int] = None
    cropName: Optional[str] = None
    fieldName: Optional[str] = None
    status: Optional[str] = None
    backgroundColor: Optional[str] = None
    borderColor: Optional[str] = None

@router.get("/events", response_model=List[CalendarEvent])
async def get_calendar_events(
    start_date: Optional[date] = Query(None, description="取得期間の開始日"),
    end_date: Optional[date] = Query(None, description="取得期間の終了日"),
    planting_plan_service: PlantingPlanService = Depends(get_planting_plan_service)
):
    """
    指定された期間のカレンダーイベントを取得します。
    期間が指定されない場合は、現在の月のイベントを返します。
    """
    try:
        if not start_date:
            today = date.today()
            start_date = date(today.year, today.month, 1)
        
        if not end_date:
            if start_date.month == 12:
                next_month = date(start_date.year + 1, 1, 1)
            else:
                next_month = date(start_date.year, start_date.month + 1, 1)
            end_date = next_month - timedelta(days=1)
        
        organization_id = 1  # テスト用の組織ID
        plans = await planting_plan_service.get_planting_plans(
            organization_id=organization_id
        )
        
        events = []
        
        def get_event_color(type: str) -> str:
            if type == 'planting':
                return '#4caf50'  # 緑色
            elif type == 'harvest':
                return '#ff9800'  # オレンジ色
            elif type == 'workflow':
                return '#2196f3'  # 青色
            else:
                return '#9e9e9e'  # グレー
        
        for plan in plans:
            if plan.planting_date:
                if start_date <= plan.planting_date <= end_date:
                    planting_color = get_event_color('planting')
                    events.append(CalendarEvent(
                        id=f"planting-{plan.id}",
                        title=f"定植: {plan.plan_name}",
                        start=plan.planting_date.isoformat(),
                        allDay=True,
                        type='planting',
                        planId=plan.id,
                        cropName=plan.crop_name if hasattr(plan, 'crop_name') else None,
                        status=plan.status,
                        backgroundColor=planting_color,
                        borderColor=planting_color
                    ))
            
            if plan.harvest_date:
                if start_date <= plan.harvest_date <= end_date:
                    harvest_color = get_event_color('harvest')
                    events.append(CalendarEvent(
                        id=f"harvest-{plan.id}",
                        title=f"収穫: {plan.plan_name}",
                        start=plan.harvest_date.isoformat(),
                        allDay=True,
                        type='harvest',
                        planId=plan.id,
                        cropName=plan.crop_name if hasattr(plan, 'crop_name') else None,
                        status=plan.status,
                        backgroundColor=harvest_color,
                        borderColor=harvest_color
                    ))
            
            if plan.workflow_instances:
                for instance in plan.workflow_instances:
                    if instance.planned_date:
                        if start_date <= instance.planned_date <= end_date:
                            workflow_color = get_event_color('workflow')
                            events.append(CalendarEvent(
                                id=f"workflow-{instance.id}",
                                title=f"{instance.step_name}: {plan.plan_name}",
                                start=instance.planned_date.isoformat(),
                                allDay=True,
                                type='workflow',
                                planId=plan.id,
                                instanceId=instance.id,
                                cropName=plan.crop_name if hasattr(plan, 'crop_name') else None,
                                status=instance.status,
                                backgroundColor=workflow_color,
                                borderColor=workflow_color
                            ))
        
        return events
    
    except DatabaseOperationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e.message}"
        )
