# endpoints authentification
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings

from app.repositories.user import UserRepository
from app.schemas.auth import UserRegister, UserCreate, Token, TokenRefresh

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["Authentification"])
# Type alias pour la dépendance (DRY)
DBSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/register", status_code=201)
async def register(data: UserRegister, db: DBSession):
    """Inscription d'un nouvel utilisateur."""
    repo = UserRepository(db)
    # Vérifier l'unicité
    if await repo.get_by_email(data.email):
        raise HTTPException(409, "Email déjà utilisé")

    if await repo.get_by_username(data.username):
        raise HTTPException(409, "Nom d'utilisateur déjà pris")

    # Hacher le mot de passe AVANT de stocker
    hashed_pw = hash_password(data.password)
    data = UserCreate(
        username=data.username,
        email=data.email,
        hashed_password=hashed_pw,
    )
    user = await repo.create(data)
    return {"message": "Compte créé avec succès", "user_id": user.id}


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    """Connexion - retourne un token JWT (compatible OAuth2)."""
    repo = UserRepository(db)
    user = await repo.get_by_username(form_data.username)
    # IMPORTANT : ne pas révéler si c'est le username ou le password qui est faux
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(400, "Compte désactivé")

    access_token = create_access_token(subject=user.id, extra_data={"scopes": ["experiments:read"]})
    refresh_token = create_refresh_token(subject=user.id)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(data: TokenRefresh, db: DBSession):
    """Renouveler un token d'accès via le refresh token."""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Token de rafraîchissement invalide")

    user_id = payload["sub"]
    repo = UserRepository(db)
    user = await repo.get(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(401, "Utilisateur introuvable ou inactif")

    new_access = create_access_token(subject=user.id)
    new_refresh = create_refresh_token(subject=user.id)
    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
