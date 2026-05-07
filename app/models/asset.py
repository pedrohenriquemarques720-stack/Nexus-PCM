from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Asset(BaseModel):
    __tablename__ = "assets"
    
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    asset_type = Column(String(50), default="equipment")
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    location = Column(String(200))
    department = Column(String(100))
    installation_date = Column(DateTime)
    total_operating_hours = Column(Float, default=0)
    failure_count = Column(Integer, default=0)
    last_maintenance = Column(DateTime)
    status = Column(String(50), default="active")
    critical_level = Column(Integer, default=3)
    technical_specs = Column(Text)
    
    work_orders = relationship("WorkOrder", back_populates="asset")
    maintenance_plans = relationship("MaintenancePlan", back_populates="asset")