from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.asset import Asset
from app.models.work_order import WorkOrder
from app.api import deps

router = APIRouter()

@router.get("/summary")
async def get_metrics_summary(
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    # Total de ativos
    total_assets_query = select(func.count(Asset.id)).where(
        Asset.company_id == company["company_id"],
        Asset.is_active == True
    )
    total_assets = (await db.execute(total_assets_query)).scalar() or 0
    
    # OS abertas
    open_orders_query = select(func.count(WorkOrder.id)).where(
        WorkOrder.company_id == company["company_id"],
        WorkOrder.status.in_(["opened", "in_progress"]),
        WorkOrder.is_active == True
    )
    open_orders = (await db.execute(open_orders_query)).scalar() or 0
    
    # Calcular MTBF médio
    assets_query = select(Asset).where(
        Asset.company_id == company["company_id"],
        Asset.is_active == True
    )
    assets = (await db.execute(assets_query)).scalars().all()
    
    mtbf_total = 0
    mttr_total = 0
    asset_count = 0
    
    for asset in assets:
        if asset.failure_count > 0:
            mtbf = asset.total_operating_hours / asset.failure_count
            mtbf_total += mtbf
            asset_count += 1
        
        # Calcular MTTR
        wo_query = select(WorkOrder).where(
            WorkOrder.asset_id == asset.id,
            WorkOrder.maintenance_type == "corrective",
            WorkOrder.status == "completed"
        )
        work_orders = (await db.execute(wo_query)).scalars().all()
        
        if work_orders:
            total_downtime = sum(wo.downtime_hours for wo in work_orders)
            mttr = total_downtime / len(work_orders)
            mttr_total += mttr
    
    avg_mtbf = mtbf_total / asset_count if asset_count > 0 else 0
    avg_mttr = mttr_total / asset_count if asset_count > 0 else 0
    
    # Disponibilidade média
    availability = (avg_mtbf / (avg_mtbf + avg_mttr) * 100) if (avg_mtbf + avg_mttr) > 0 else 0
    
    return {
        "total_assets": total_assets,
        "open_orders": open_orders,
        "avg_mtbf": round(avg_mtbf, 2),
        "avg_mttr": round(avg_mttr, 2),
        "availability": round(availability, 2)
    }

@router.get("/mtbf/{asset_id}")
async def get_asset_mtbf(
    asset_id: str,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    query = select(Asset).where(
        Asset.id == asset_id,
        Asset.company_id == company["company_id"]
    )
    result = await db.execute(query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    mtbf = asset.total_operating_hours / asset.failure_count if asset.failure_count > 0 else 0
    
    return {
        "asset_id": asset_id,
        "asset_name": asset.name,
        "mtbf_hours": round(mtbf, 2),
        "mtbf_days": round(mtbf / 24, 2),
        "total_operating_hours": asset.total_operating_hours,
        "failure_count": asset.failure_count
    }

@router.get("/mttr/{asset_id}")
async def get_asset_mttr(
    asset_id: str,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    query = select(Asset).where(
        Asset.id == asset_id,
        Asset.company_id == company["company_id"]
    )
    result = await db.execute(query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    wo_query = select(WorkOrder).where(
        WorkOrder.asset_id == asset_id,
        WorkOrder.maintenance_type == "corrective",
        WorkOrder.status == "completed"
    )
    work_orders = (await db.execute(wo_query)).scalars().all()
    
    if not work_orders:
        return {"mttr_hours": 0, "total_repairs": 0, "total_downtime": 0}
    
    total_downtime = sum(wo.downtime_hours for wo in work_orders)
    mttr = total_downtime / len(work_orders)
    
    return {
        "asset_id": asset_id,
        "asset_name": asset.name,
        "mttr_hours": round(mttr, 2),
        "mttr_minutes": round(mttr * 60, 2),
        "total_repairs": len(work_orders),
        "total_downtime": round(total_downtime, 2)
    }