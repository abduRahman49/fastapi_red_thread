from pydantic import BaseModel , Field , EmailStr
from typing import Optional

class UserCreate(BaseModel):
 # Champ obligatoire
 username : str

 # Avec valeur par dé faut
 is_active : bool=True

 # Optionnel ( peut être None )
 email : Optional[EmailStr]=None

 # Avec Field pour mé tadonn ées et validation
 age : int = Field(default=18 , ge=18 , le=100 , title="Age", description="Age de l’utilisateur en annees", examples=[25 , 30])

 # Cha îne avec contraintes
 password : str = Field(min_length=8, max_length=100)



user = UserCreate(username="abdou", email="abdouseye@isi.com", age=20, password="passer1123")

print("Retour deserialisation: ", user.model_dump(), type(user.model_dump()))
print("Retour serialisation: ", user.model_dump_json(), type(user.model_dump_json()))

