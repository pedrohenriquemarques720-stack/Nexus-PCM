from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.asset import Asset
from app.models.work_order import WorkOrder
from app.models.user import User
from app.api import deps

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_system_stats(
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Retorna estatísticas do sistema para o dashboard"""
    from sqlalchemy import select, func
    
    # Total de ativos
    assets_result = await db.execute(select(func.count(Asset.id)).where(Asset.company_id == company["company_id"]))
    total_assets = assets_result.scalar() or 0
    
    # Total de OS abertas
    orders_result = await db.execute(
        select(func.count(WorkOrder.id)).where(
            WorkOrder.company_id == company["company_id"],
            WorkOrder.is_closed == False
        )
    )
    open_orders = orders_result.scalar() or 0
    
    # Total de usuários
    users_result = await db.execute(select(func.count(User.id)).where(User.company_id == company["company_id"]))
    total_users = users_result.scalar() or 0
    
    return {
        "total_assets": total_assets,
        "open_orders": open_orders,
        "total_users": total_users,
        "system_status": "online"
    }
