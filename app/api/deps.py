from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from uuid import uuid4


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    """Retorna um usuário padrão para testes - SEM AUTENTICAÇÃO"""
    
    # Buscar ou criar usuário admin
    from sqlalchemy import select
    from app.core.security import get_password_hash
    
    query = select(User).where(User.username == "admin")
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            id=str(uuid4()),
            company_id=str(uuid4()),
            email="admin@nexus.com",
            username="admin",
            full_name="Administrador",
            hashed_password=get_password_hash("admin123"),
            is_superuser=True,
            role="admin"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user


async def get_current_company(user: User = Depends(get_current_user)) -> dict:
    return {"company_id": user.company_id, "user_id": user.id}
