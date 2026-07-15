import datetime
from pydantic import BaseModel, field_validator
from typing import Optional

# CREATE
class DatasetCreate(BaseModel):
 name: str
 description: Optional[str] = None
 num_rows: int
 num_features: int
 format: str

 @field_validator("name")
 @classmethod
 def name_must_be_snake_case(cls, v):
   import re
   if not re.match("^[a-z][a-z0-9_]*$", v):
     raise ValueError("Le nom du dataset doit être au format snake_cas")
   
   return v.strip()
 
 @field_validator("format")
 @classmethod
 def extension_should_be_restricted(cls, v):
   accepted = {"csv", "parquet", "json"}
   normalized_value = v.lower()
   if normalized_value not in accepted:
     raise ValueError("Le format n'est pas supporté")
   
   return normalized_value


# RESPONSE
class DatasetResponse(DatasetCreate):
 id: int
 created_at: datetime.datetime

#  class Config:
#     from_attributes = True # Pydantic v2

