from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from uuid import uuid4
from typing import List, Optional
from app.core.database import get_db
from app.models.asset import Asset
from app.models.work_order import WorkOrder
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetWithMetrics
from app.api import deps

router = APIRouter()

@router.post("/", response_model=AssetResponse, status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Criar um novo ativo"""
    
    # Verificar se código já existe
    existing = await db.execute(
        select(Asset).where(
            Asset.code == asset_data.code,
            Asset.company_id == company["company_id"]
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Código de ativo já existe")
    
    asset = Asset(
        id=str(uuid4()),
        company_id=company["company_id"],
        **asset_data.model_dump()
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return AssetResponse.model_validate(asset)


@router.get("/", response_model=List[AssetResponse])
async def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Buscar por código, nome ou localização"),
    asset_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Listar ativos com filtros e paginação"""
    
    query = select(Asset).where(
        Asset.company_id == company["company_id"],
        Asset.is_active == True
    )
    
    # Filtro de busca
    if search:
        query = query.where(
            or_(
                Asset.code.ilike(f"%{search}%"),
                Asset.name.ilike(f"%{search}%"),
                Asset.location.ilike(f"%{search}%")
            )
        )
    
    # Filtro por tipo
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    
    # Filtro por status
    if status:
        query = query.where(Asset.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return [AssetResponse.model_validate(a) for a in assets]


@router.get("/{asset_id}", response_model=AssetWithMetrics)
async def get_asset(
    asset_id: str,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Obter detalhes de um ativo com métricas"""
    
    query = select(Asset).where(
        Asset.id == asset_id,
        Asset.company_id == company["company_id"],
        Asset.is_active == True
    )
    result = await db.execute(query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Calcular métricas
    mtbf = asset.total_operating_hours / asset.failure_count if asset.failure_count > 0 else 0
    
    # Buscar OS pendentes
    wo_query = select(WorkOrder).where(
        WorkOrder.asset_id == asset_id,
        WorkOrder.status.in_(["opened", "in_progress"]),
        WorkOrder.is_active == True
    )
    wo_result = await db.execute(wo_query)
    pending_orders = wo_result.scalars().all()
    
    return AssetWithMetrics(
        **AssetResponse.model_validate(asset).model_dump(),
        mtbf_hours=round(mtbf, 2),
        mttr_hours=0,
        availability_percentage=0,
        pending_work_orders=len(pending_orders)
    )


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    asset_data: AssetUpdate,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Atualizar um ativo"""
    
    query = select(Asset).where(
        Asset.id == asset_id,
        Asset.company_id == company["company_id"],
        Asset.is_active == True
    )
    result = await db.execute(query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    update_data = asset_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)
    
    await db.commit()
    await db.refresh(asset)
    
    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: str,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete de um ativo"""
    
    query = select(Asset).where(
        Asset.id == asset_id,
        Asset.company_id == company["company_id"],
        Asset.is_active == True
    )
    result = await db.execute(query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    asset.is_active = False
    await db.commit()
