from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime

class WorkOrder(BaseModel):
    __tablename__ = "work_orders"
    
    # Código e identificação
    code = Column(String(50), nullable=False, unique=True)
    asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Classificação
    maintenance_type = Column(String(50), default="corrective")  # corrective, preventive, predictive, emergency
    priority = Column(Integer, default=1)  # 1-Low to 5-High
    color_code = Column(String(20), default="green")  # red (emergência), yellow (urgente), green (normal)
    
    # Solicitação
    requested_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # solicitante
    requested_date = Column(DateTime, default=datetime.utcnow)
    
    # Equipe designada
    assigned_manutentores = Column(Text, nullable=True)  # lista de IDs dos manutentores (JSON)
    
    # Datas do ciclo
    scheduled_date = Column(DateTime)  # data agendada
    start_date = Column(DateTime)  # início real
    completion_date = Column(DateTime)  # conclusão real
    
    # Status
    status = Column(String(50), default="opened")  # opened, in_progress, completed, cancelled, blocked
    
    # Planejamento (para preventivas)
    planned_hours = Column(Float, default=0.0)  # horas planejadas
    planned_cost = Column(Float, default=0.0)  # custo planejado
    
    # Execução (lançado pelos manutentores)
    actual_hours = Column(Float, default=0.0)  # horas reais (soma time_entries)
    actual_cost = Column(Float, default=0.0)  # custo real (soma time_entries)
    
    # Custos de materiais
    parts_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)  # actual_cost + parts_cost
    
    # Métricas de tempo
    downtime_hours = Column(Float, default=0.0)  # tempo que a máquina ficou parada
    
    # Fechamento
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime, nullable=True)
    closure_report = Column(Text, nullable=True)  # relatório de fechamento
    solution_applied = Column(Text, nullable=True)  # solução aplicada
    
    # Problemas relatados
    reported_problem = Column(Text, nullable=True)
    technician_notes = Column(Text, nullable=True)
    
    # Relacionamentos
    asset = relationship("Asset", back_populates="work_orders")
    time_entries = relationship("TimeEntry", back_populates="work_orders", cascade="all, delete-orphan")
    requester = relationship("User", foreign_keys=[requested_by])
