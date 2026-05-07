from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class WorkOrder(BaseModel):
    __tablename__ = "work_orders"
    
    code = Column(String(50), nullable=False, unique=True)
    asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    maintenance_type = Column(String(50), default="corrective")
    priority = Column(Integer, default=1)
    requested_date = Column(DateTime)
    scheduled_date = Column(DateTime)
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    status = Column(String(50), default="opened")
    assigned_team = Column(String(200))
    assigned_technician = Column(String(100))
    labor_hours = Column(Float, default=0)
    labor_cost = Column(Float, default=0)
    parts_cost = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    downtime_hours = Column(Float, default=0)
    reported_problem = Column(Text)
    solution_applied = Column(Text)
    technician_notes = Column(Text)
    
    asset = relationship("Asset", back_populates="work_orders")