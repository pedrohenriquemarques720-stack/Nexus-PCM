from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkOrderBase(BaseModel):
    code: str
    asset_id: str
    title: str
    description: Optional[str] = None
    maintenance_type: str = "corrective"
    priority: int = 1
    scheduled_date: Optional[datetime] = None
    assigned_team: Optional[str] = None
    reported_problem: Optional[str] = None

class WorkOrderCreate(WorkOrderBase):
    pass

class WorkOrderResponse(WorkOrderBase):
    id: str
    status: str
    labor_hours: float
    total_cost: float
    downtime_hours: float
    created_at: datetime