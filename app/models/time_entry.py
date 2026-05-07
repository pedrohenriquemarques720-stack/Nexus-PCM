from sqlalchemy import Column, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime

class TimeEntry(BaseModel):
    """Registro de horas trabalhadas por manutentor em uma OS"""
    __tablename__ = "time_entries"
    
    # Relacionamentos
    work_order_id = Column(String(36), ForeignKey("work_orders.id"), nullable=False)
    manutentor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Dados do lançamento
    entry_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    hours_worked = Column(Float, nullable=False, default=0.0)  # horas trabalhadas no dia
    description = Column(Text, nullable=True)  # descrição do trabalho realizado
    
    # Controle
    is_overtime = Column(Boolean, default=False)  # se é hora extra
    overtime_rate = Column(Float, default=1.0)  # multiplicador da hora extra (1.5 = 50% a mais)
    
    # Custos calculados
    calculated_cost = Column(Float, default=0.0)  # horas * valor_hora (automático)
    
    # Relacionamentos ORM
    work_order = relationship("WorkOrder", back_populates="time_entries")
    manutentor = relationship("User", foreign_keys=[manutentor_id])
