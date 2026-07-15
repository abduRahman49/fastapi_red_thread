from sqlalchemy import func, select

from .base import BaseRepository
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate


class ExperimentRepository(BaseRepository[Experiment, ExperimentCreate, ExperimentUpdate]):
    def __init__(self, db):
        super().__init__(Experiment, db)


    async def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 20) -> list[Experiment]:
        result = await self.db.execute(
        select(Experiment)
            .where(Experiment.owner_id == owner_id)
            .order_by(Experiment.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_best_by_algorithm(self, algorithm: str) -> Experiment | None:
        result = await self.db.execute(
        select(Experiment)
            .where(
                Experiment.algorithm == algorithm,
                Experiment.accuracy.is_not(None),
            )
            .order_by(Experiment.accuracy.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
        select(
            Experiment.status,
            func.count(Experiment.id).label("count")
        ).group_by(Experiment.status)
        )
        return {status: count for status, count in result.all()}
