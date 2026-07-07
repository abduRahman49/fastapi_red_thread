# app.dependencies.security.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.security import decode_token
from app.core.database import get_db
from app.repositories.user import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "read": "Lecture des donnees",
        "write": "Ecriture des donnees",
        "admin": "Administration systeme",
    }
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Vérifie le token et retourne l'utilisateur courant."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        credentials_exception = HTTPException(
        status_code=401,
            detail="Impossible de valider les credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    repo = UserRepository(db)
    user = await repo.get(int(user_id))
    if not user:
        raise credentials_exception

    # Vérification des scopes
    token_scopes = payload.get("scopes", [])
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=403,
                detail=f"Permission insuffisante. Scope requis: '{scope}'",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user
