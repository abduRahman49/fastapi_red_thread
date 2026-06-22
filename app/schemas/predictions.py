import datetime
from pydantic import BaseModel
from typing import Optional

# CREATE
class PredictionRequest(BaseModel):
 feature_1: float
 feature_2: float
 feature_3: Optional[float] = None


# RESPONSE
class PredictionResponse(BaseModel):
 prediction: float
 confidence: float
 model_version: str
 timestamp: datetime.datetime