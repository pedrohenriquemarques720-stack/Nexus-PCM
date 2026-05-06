from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from typing import List
from app.core.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetResponse
from app.api import deps

router = APIRouter()

@router.post("/", response_model=AssetResponse, status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
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
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    query = select(Asset).where(
        Asset.company_id == company["company_id"],
        Asset.is_active == True
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return [AssetResponse.model_validate(a) for a in assets]

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
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
    
    return AssetResponse.model_validate(asset)