from fastapi import Depends, APIRouter, HTTPException, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.experiment import ExperimentRepository
from app.schemas.experiment import ExperimentCreate, ExperimentResponse
from typing import Annotated
from app.dependencies.security import get_current_user


router = APIRouter(prefix="/experiments", tags=["Experiments"])
# Type alias pour la dépendance (DRY)
DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.get("/{exp_id}", response_model=ExperimentResponse)
async def get_experiment(exp_id: int, db: DBSession):
    repo = ExperimentRepository(db)
    exp = await repo.get(exp_id)
    if not exp:
        raise HTTPException(404, "Expérience introuvable")
    return exp


@router.post("/", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    data: ExperimentCreate,
    db: DBSession,
):
    repo = ExperimentRepository(db)
    return await repo.create(data)


@router.get("/", response_model=list[ExperimentResponse], status_code=200)
async def get_list_experiments(
    db: DBSession,
    skip: Annotated[int, Query(ge=0, le=50)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user=Security(get_current_user, scopes=["experiments:read"])
):
    repo = ExperimentRepository(db)
    return await repo.get_all(skip=skip, limit=limit)
