import datetime
from pydantic import BaseModel, Field
# generate create and update schemas for the Experiment model

class ExperimentCreate(BaseModel):
    name: str = Field(..., max_length=200)
    algorithm: str = Field(..., max_length=50)
    description: str | None = Field(None, max_length=500)


class ExperimentUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    algorithm: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)
    status: str | None = Field(None, max_length=20)
    accuracy: float | None = None


class ExperimentResponse(BaseModel):
    id: int
    name: str
    algorithm: str
    status: str
    description: str | None
    accuracy: float | None
    created_at: datetime.datetime
    owner_id: int | None

    # class Config:
    #     from_attributes = True
