from sqlalchemy import Column, String, Boolean, Float
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    # Dados básicos
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="user")  # admin, manutentor, solicitante
    
    # NOVOS CAMPOS PARA MANUTENTORES
    user_type = Column(String(50), default="solicitante")  # 'manutentor', 'solicitante', 'admin'
    specialty = Column(String(100), nullable=True)  # especialidade: elétrica, mecânica, etc.
    hourly_rate = Column(Float, default=0.0)  # valor da hora (R$/hora)
    
    # Dados de contato adicionais
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)  # departamento
    position = Column(String(100), nullable=True)  # cargo
    
    company_name = Column(String(200), nullable=True)
