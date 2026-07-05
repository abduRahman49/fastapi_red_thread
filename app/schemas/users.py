from pydantic import BaseModel , Field , EmailStr
from typing import Optional

class UserCreate(BaseModel):
 # Champ obligatoire
 username : str
 # Optionnel ( peut être None )
 email : Optional[EmailStr]=None
 # Chaîne avec contraintes
 password : str = Field(min_length=8, max_length=100)
 # Avec valeur par dé faut
 is_active : bool=True


class UserUpdate(BaseModel):
    username : Optional[str] = None
    email : Optional[EmailStr] = None
    password : Optional[str] = Field(default=None, min_length=8, max_length=100)
    is_active : Optional[bool] = None
