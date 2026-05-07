from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.work_order import WorkOrder
from app.schemas.work_order import WorkOrderCreate, WorkOrderResponse
from app.api import deps

router = APIRouter()

@router.post("/", response_model=WorkOrderResponse, status_code=201)
async def create_work_order(
    wo_data: WorkOrderCreate,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    work_order = WorkOrder(
        id=str(uuid4()),
        company_id=company["company_id"],
        requested_date=datetime.now(),
        **wo_data.model_dump()
    )
    db.add(work_order)
    await db.commit()
    await db.refresh(work_order)
    return WorkOrderResponse.model_validate(work_order)

@router.get("/", response_model=List[WorkOrderResponse])
async def get_work_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    query = select(WorkOrder).where(
        WorkOrder.company_id == company["company_id"],
        WorkOrder.is_active == True
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return [WorkOrderResponse.model_validate(o) for o in orders]

@router.get("/{wo_id}", response_model=WorkOrderResponse)
async def get_work_order(
    wo_id: str,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    query = select(WorkOrder).where(
        WorkOrder.id == wo_id,
        WorkOrder.company_id == company["company_id"]
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    return WorkOrderResponse.model_validate(order)