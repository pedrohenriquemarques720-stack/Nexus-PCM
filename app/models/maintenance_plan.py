from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class MaintenancePlan(BaseModel):
    __tablename__ = "maintenance_plans"
    
    code = Column(String(50), nullable=False, unique=True)
    asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    frequency_type = Column(String(50))
    frequency_value = Column(Integer)
    last_execution = Column(DateTime)
    next_execution = Column(DateTime)
    estimated_duration = Column(Float, default=0)
    estimated_cost = Column(Float, default=0)
    
    asset = relationship("Asset", back_populates="maintenance_plans")