from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class AssetBase(BaseModel):
    code: str = Field(..., max_length=50, description="Código único do ativo")
    name: str = Field(..., max_length=200, description="Nome do ativo")
    description: Optional[str] = None
    asset_type: str = Field(default="equipment", description="equipment, machine, vehicle, tool")
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    installation_date: Optional[datetime] = None
    critical_level: int = Field(default=3, ge=1, le=5, description="1-Baixo a 5-Crítico")
    status: str = Field(default="active", description="active, maintenance, inactive")

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    """Schema para atualização parcial"""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    critical_level: Optional[int] = Field(None, ge=1, le=5)

class AssetResponse(AssetBase):
    id: UUID
    company_id: UUID
    total_operating_hours: float
    failure_count: int
    last_maintenance: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AssetWithMetrics(AssetResponse):
    """Ativo com métricas calculadas"""
    mtbf_hours: float = 0
    mttr_hours: float = 0
    availability_percentage: float = 0
    pending_work_orders: int = 0
