from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from uuid import uuid4

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Versão de teste - cria usuário admin automaticamente se não existir"""
    
    # Se não tiver token, cria um usuário admin automaticamente
    if not credentials:
        # Buscar usuário admin existente
        query = select(User).where(User.username == "admin")
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            # Criar usuário admin automaticamente
            from app.core.security import get_password_hash
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
    
    # Se tiver token, valida normalmente
    from app.core.security import decode_token
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")
    query = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user


async def get_current_company(user: User = Depends(get_current_user)) -> dict:
    return {"company_id": user.company_id, "user_id": user.id}
