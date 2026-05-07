from sqlalchemy import Column, String, Boolean, Float
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="user")
    
    # Tipos de usuário
    user_type = Column(String(50), default="solicitante")
    specialty = Column(String(100), nullable=True)
    hourly_rate = Column(Float, default=0.0)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)