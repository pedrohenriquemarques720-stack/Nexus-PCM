from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class TimeEntryBase(BaseModel):
    """Base schema para lançamento de horas"""
    work_order_id: UUID
    manutentor_id: UUID
    entry_date: datetime = Field(default_factory=datetime.now)
    hours_worked: float = Field(..., gt=0, description="Horas trabalhadas (maior que 0)")
    description: Optional[str] = None
    is_overtime: bool = False
    overtime_rate: float = Field(default=1.0, ge=1.0, le=2.0)


class TimeEntryCreate(TimeEntryBase):
    """Schema para criar um lançamento"""
    pass


class TimeEntryUpdate(BaseModel):
    """Schema para atualizar um lançamento"""
    hours_worked: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    is_overtime: Optional[bool] = None
    overtime_rate: Optional[float] = Field(None, ge=1.0, le=2.0)


class TimeEntryResponse(TimeEntryBase):
    """Schema para resposta do lançamento"""
    id: UUID
    calculated_cost: float
    created_at: datetime
    
    # Informações adicionais do manutentor
    manutentor_name: Optional[str] = None
    manutentor_hourly_rate: Optional[float] = None
    
    class Config:
        from_attributes = True


class TimeEntrySummary(BaseModel):
    """Resumo de horas por OS"""
    work_order_id: UUID
    work_order_code: str
    work_order_title: str
    total_hours: float
    total_cost: float
    total_overtime_hours: float
    manutentores_count: int
    entries_count: int
    last_entry_date: Optional[datetime]


class WorkOrderCloseRequest(BaseModel):
    """Schema para fechamento de OS"""
    closure_report: str = Field(..., min_length=10, description="Relatório de fechamento")
    solution_applied: str = Field(..., min_length=10, description="Solução aplicada")
    downtime_hours: float = Field(default=0.0, ge=0, description="Horas de parada da máquina")
    parts_cost: float = Field(default=0.0, ge=0, description="Custo de peças/materiais")
