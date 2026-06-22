from pydantic import BaseModel
from typing import Optional

# CREATE
class Item(BaseModel):
 id: int
 name: str
 price: float

# UPDATE
class ItemUpdate(BaseModel):
 name: Optional[str] = None
 price: Optional[float] = None
 description: Optional[str] = None