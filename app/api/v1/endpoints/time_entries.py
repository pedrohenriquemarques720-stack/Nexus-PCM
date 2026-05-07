from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import uuid4
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.time_entry import TimeEntry
from app.models.work_order import WorkOrder
from app.models.user import User
from app.schemas.time_entry import (
    TimeEntryCreate, TimeEntryUpdate, TimeEntryResponse, 
    TimeEntrySummary, WorkOrderCloseRequest
)
from app.api import deps

router = APIRouter(prefix="/time-entries", tags=["Time Entries"])


@router.post("/", response_model=TimeEntryResponse, status_code=201)
async def create_time_entry(
    entry_data: TimeEntryCreate,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Criar um novo lançamento de horas para uma OS"""
    
    # Verificar se a OS existe
    wo_query = select(WorkOrder).where(
        WorkOrder.id == str(entry_data.work_order_id),
        WorkOrder.company_id == company["company_id"]
    )
    wo_result = await db.execute(wo_query)
    work_order = wo_result.scalar_one_or_none()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
    
    # Verificar se o manutentor existe
    manutentor_query = select(User).where(
        User.id == str(entry_data.manutentor_id),
        User.company_id == company["company_id"],
        User.user_type == "manutentor"
    )
    manutentor_result = await db.execute(manutentor_query)
    manutentor = manutentor_result.scalar_one_or_none()
    
    if not manutentor:
        raise HTTPException(status_code=404, detail="Manutentor não encontrado")
    
    # Calcular custo
    hourly_rate = manutentor.hourly_rate or 0
    overtime_multiplier = entry_data.overtime_rate if entry_data.is_overtime else 1.0
    calculated_cost = entry_data.hours_worked * hourly_rate * overtime_multiplier
    
    # Criar o lançamento
    time_entry = TimeEntry(
        id=str(uuid4()),
        company_id=company["company_id"],
        work_order_id=str(entry_data.work_order_id),
        manutentor_id=str(entry_data.manutentor_id),
        entry_date=entry_data.entry_date,
        hours_worked=entry_data.hours_worked,
        description=entry_data.description,
        is_overtime=entry_data.is_overtime,
        overtime_rate=entry_data.overtime_rate,
        calculated_cost=calculated_cost
    )
    
    db.add(time_entry)
    
    # Atualizar a OS com as horas e custos reais
    # Somar todas as horas e custos da OS
    hours_sum_query = select(
        func.sum(TimeEntry.hours_worked).label("total_hours"),
        func.sum(TimeEntry.calculated_cost).label("total_cost")
    ).where(
        TimeEntry.work_order_id == str(entry_data.work_order_id),
        TimeEntry.company_id == company["company_id"]
    )
    hours_result = await db.execute(hours_sum_query)
    totals = hours_result.one()
    
    work_order.actual_hours = totals.total_hours or 0
    work_order.actual_cost = totals.total_cost or 0
    work_order.total_cost = (totals.total_cost or 0) + work_order.parts_cost
    
    await db.commit()
    await db.refresh(time_entry)
    
    return TimeEntryResponse.model_validate(time_entry)


@router.get("/work-order/{work_order_id}", response_model=List[TimeEntryResponse])
async def get_time_entries_by_work_order(
    work_order_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os lançamentos de uma OS"""
    
    query = select(TimeEntry).where(
        TimeEntry.work_order_id == work_order_id,
        TimeEntry.company_id == company["company_id"]
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return [TimeEntryResponse.model_validate(e) for e in entries]


@router.get("/manutentor/{manutentor_id}", response_model=List[TimeEntryResponse])
async def get_time_entries_by_manutentor(
    manutentor_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Listar todos os lançamentos de um manutentor"""
    
    query = select(TimeEntry).where(
        TimeEntry.manutentor_id == manutentor_id,
        TimeEntry.company_id == company["company_id"]
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return [TimeEntryResponse.model_validate(e) for e in entries]


@router.get("/summary/{work_order_id}", response_model=TimeEntrySummary)
async def get_time_entry_summary(
    work_order_id: str,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Obter resumo de horas e custos de uma OS"""
    
    # Buscar OS
    wo_query = select(WorkOrder).where(
        WorkOrder.id == work_order_id,
        WorkOrder.company_id == company["company_id"]
    )
    wo_result = await db.execute(wo_query)
    work_order = wo_result.scalar_one_or_none()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
    
    # Buscar estatísticas dos lançamentos
    stats_query = select(
        func.sum(TimeEntry.hours_worked).label("total_hours"),
        func.sum(TimeEntry.calculated_cost).label("total_cost"),
        func.sum(TimeEntry.hours_worked).filter(TimeEntry.is_overtime == True).label("overtime_hours"),
        func.count(TimeEntry.id).label("entries_count"),
        func.count(func.distinct(TimeEntry.manutentor_id)).label("manutentores_count"),
        func.max(TimeEntry.entry_date).label("last_entry")
    ).where(
        TimeEntry.work_order_id == work_order_id,
        TimeEntry.company_id == company["company_id"]
    )
    stats_result = await db.execute(stats_query)
    stats = stats_result.one()
    
    return TimeEntrySummary(
        work_order_id=work_order.id,
        work_order_code=work_order.code,
        work_order_title=work_order.title,
        total_hours=stats.total_hours or 0,
        total_cost=stats.total_cost or 0,
        total_overtime_hours=stats.overtime_hours or 0,
        manutentores_count=stats.manutentores_count or 0,
        entries_count=stats.entries_count or 0,
        last_entry_date=stats.last_entry
    )


@router.put("/{entry_id}", response_model=TimeEntryResponse)
async def update_time_entry(
    entry_id: str,
    entry_data: TimeEntryUpdate,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Atualizar um lançamento de horas"""
    
    query = select(TimeEntry).where(
        TimeEntry.id == entry_id,
        TimeEntry.company_id == company["company_id"]
    )
    result = await db.execute(query)
    time_entry = result.scalar_one_or_none()
    
    if not time_entry:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    update_data = entry_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(time_entry, key, value)
    
    # Recalcular custo se horas ou overtime mudaram
    if "hours_worked" in update_data or "is_overtime" in update_data or "overtime_rate" in update_data:
        # Buscar o manutentor para saber o valor da hora
        manutentor_query = select(User).where(User.id == time_entry.manutentor_id)
        manutentor_result = await db.execute(manutentor_query)
        manutentor = manutentor_result.scalar_one_or_none()
        
        hourly_rate = manutentor.hourly_rate or 0
        overtime_multiplier = time_entry.overtime_rate if time_entry.is_overtime else 1.0
        time_entry.calculated_cost = time_entry.hours_worked * hourly_rate * overtime_multiplier
    
    await db.commit()
    await db.refresh(time_entry)
    
    # Atualizar totais da OS
    hours_sum_query = select(
        func.sum(TimeEntry.hours_worked).label("total_hours"),
        func.sum(TimeEntry.calculated_cost).label("total_cost")
    ).where(
        TimeEntry.work_order_id == time_entry.work_order_id,
        TimeEntry.company_id == company["company_id"]
    )
    hours_result = await db.execute(hours_sum_query)
    totals = hours_result.one()
    
    wo_query = select(WorkOrder).where(WorkOrder.id == time_entry.work_order_id)
    wo_result = await db.execute(wo_query)
    work_order = wo_result.scalar_one_or_none()
    
    if work_order:
        work_order.actual_hours = totals.total_hours or 0
        work_order.actual_cost = totals.total_cost or 0
        work_order.total_cost = (totals.total_cost or 0) + work_order.parts_cost
        await db.commit()
    
    return TimeEntryResponse.model_validate(time_entry)


@router.delete("/{entry_id}", status_code=204)
async def delete_time_entry(
    entry_id: str,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Deletar um lançamento de horas"""
    
    query = select(TimeEntry).where(
        TimeEntry.id == entry_id,
        TimeEntry.company_id == company["company_id"]
    )
    result = await db.execute(query)
    time_entry = result.scalar_one_or_none()
    
    if not time_entry:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    work_order_id = time_entry.work_order_id
    
    await db.delete(time_entry)
    
    # Recalcular totais da OS após deletar
    hours_sum_query = select(
        func.sum(TimeEntry.hours_worked).label("total_hours"),
        func.sum(TimeEntry.calculated_cost).label("total_cost")
    ).where(
        TimeEntry.work_order_id == work_order_id,
        TimeEntry.company_id == company["company_id"]
    )
    hours_result = await db.execute(hours_sum_query)
    totals = hours_result.one()
    
    wo_query = select(WorkOrder).where(WorkOrder.id == work_order_id)
    wo_result = await db.execute(wo_query)
    work_order = wo_result.scalar_one_or_none()
    
    if work_order:
        work_order.actual_hours = totals.total_hours or 0
        work_order.actual_cost = totals.total_cost or 0
        work_order.total_cost = (totals.total_cost or 0) + work_order.parts_cost
    
    await db.commit()


@router.post("/close/{work_order_id}", response_model=TimeEntrySummary)
async def close_work_order(
    work_order_id: str,
    close_data: WorkOrderCloseRequest,
    company: dict = Depends(deps.get_current_company),
    db: AsyncSession = Depends(get_db)
):
    """Fechar uma Ordem de Serviço com relatório e soluções"""
    
    query = select(WorkOrder).where(
        WorkOrder.id == work_order_id,
        WorkOrder.company_id == company["company_id"]
    )
    result = await db.execute(query)
    work_order = result.scalar_one_or_none()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
    
    # Atualizar OS com dados de fechamento
    work_order.is_closed = True
    work_order.closed_at = datetime.now()
    work_order.closure_report = close_data.closure_report
    work_order.solution_applied = close_data.solution_applied
    work_order.downtime_hours = close_data.downtime_hours
    work_order.parts_cost = close_data.parts_cost
    work_order.status = "completed"
    
    # Recalcular total cost
    work_order.total_cost = work_order.actual_cost + close_data.parts_cost
    
    await db.commit()
    
    # Retornar resumo atualizado
    return await get_time_entry_summary(work_order_id, company, db)
