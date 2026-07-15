import datetime
from fastapi import FastAPI, HTTPException, Path, Query, Body
from fastapi import Response
from fastapi.responses import RedirectResponse
from typing import Optional, Annotated
from enum import Enum
from app.schemas.predictions import PredictionRequest, PredictionResponse
from app.schemas.items import Item, ItemUpdate
from app.schemas.dataset import DatasetCreate, DatasetResponse
from app.routes.experiment import router as experiment_router
from app.routes.auth import router as auth_router
from app.middlewares.cors import configure_cors
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware


predictions_db: list[PredictionResponse] = []
items_db: list[Item] = []
fake_items = [
    {"name": "Foo"}, {"name": "Bar"}, {"name": "Baz"},
    {"name": "Alice"}, {"name": "Bob"}
]


# Enum
class ModelName(str, Enum):
    """Enum pour restreindre les valeurs autorisées."""
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI(
    title="Mon API FastAPI",
    description="Une API construite avec le framework FastAPI",
    version="1.0.0"
)

app.include_router(experiment_router)  # Inclure le routeur des expériences
app.include_router(auth_router)
app = configure_cors(app)  # Configurer CORS pour l'application
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=20, period=60)

# Endpoints de l'app
@app.get("/")
def read_root():
    """Endpoint racine-verifie que l’API est operationnelle."""
    return {"message": "Bienvenue sur mon API FastAPI !"}

@app.get("/health")
def health_check():
    """Endpoint de vérification de santé."""
    return {"status": "healthy"}


@app.post(
"/predictions",
response_model=PredictionResponse,
status_code=201,
summary="Effectuer une prédiction",
tags=["Prédictions"],
)
def predict(request: PredictionRequest):
    """
    Soumet des features et retourne une prédiction
    - **feature_1** : première variable explicative
    - **feature_2** : deuxième variable explicative
    - **feature_3** : troisième variable (optionnelle)
    """
    # simulation du calcul avec le model fictif
    score = (request.feature_1 * 0.4 + request.feature_2 * 0.6)
    if request.feature_3:
       score += request.feature_3 * 0.1

    result = PredictionResponse(
       prediction=round(score, 4),
       confidence=0.87,
       model_version="v1.0",
       timestamp=datetime.datetime.utcnow()
    )
    predictions_db.append(result)
    return result


@app.get(
"/predictions",
response_model=list[PredictionResponse],
tags=["Prédictions"],
)
def list_predictions():
    """Retourne l’historique de toutes les prédictions."""
    return predictions_db


@app.post(
path="/items",
response_model=Item, # Schéma de la réponse
status_code=201, # Code HTTP de succès
tags=["Items"], # Groupement dans la doc
summary="Créer un item", # Titre court
description="Crée un nouvel item dans le catalogue.",
response_description="L’item créé",
deprecated=False, # Marquer comme déprécié
operation_id="create_item", # ID OpenAPI unique
include_in_schema=True, # Inclure dans la doc
)
async def create_item(item: Item):
 items_db.append(item)
 return item


@app.get("/items", tags=["Items"])
async def list_items(
 skip: int = 0, # Obligatoire par défaut
 limit: int = 10, # Avec valeur par défaut
 q: Optional[str] = None, # Optionnel
 active: bool = True, # Booléen (true/false/1/0/on/off)
):
 """
 GET /items?skip=0&limit=10&q=foo&active=true
 """
 result = fake_items[skip : skip + limit]
 if q:
    result = [item for item in result if q.lower() in item["name"].lower()]
 return result


@app.get(
"/items",
response_model=list[Item],
tags=["Items"],
include_in_schema=False
)
def list_created_items():
    """Retourne la liste des items."""
    return items_db


@app.get(
"/items/{id}",
response_model=Item,
tags=['Items']
)
def get_item(id: Annotated[int, Path(ge=1, le=1000)], response: Response):
 """item_id est automatiquement converti en int et validé."""
 # traitement pour récupérer l'item en fonction de son id

 response.headers["Cache-Control"] = "20"
 for item in items_db:
    if item.id == id:
       return item
 
 raise HTTPException(status_code=404, detail="Item introuvable")


@app.get("/search")
async def search(
 q: Annotated[str | None, Query(
 title="Terme de recherche",
 min_length=2,
 max_length=100,
 pattern=r"^[a-zA-Z0-9\s]+$",
 example="machine learning",
 )] = None,
 page: Annotated[int, Query(ge=1)] = 1,
 per_page: Annotated[int, Query(ge=1, le=100)] = 20,
 sort_by: Annotated[str, Query(
 enum=["name", "date", "relevance"]
 )] = "relevance",
 ):
 return {
 "query": q,
 "page": page,
 "per_page": per_page,
 "sort_by": sort_by,
 }

@app.post("/datasets", response_model=DatasetResponse, status_code=201)
async def create_dataset(dataset: DatasetCreate):
 """
 FastAPI lit automatiquement le corps JSON et le valide
 contre le schéma DatasetCreate.
 """
 # Simuler la persistance
 return DatasetResponse(
 **dataset.model_dump(),
 id=1,
 created_at=datetime.datetime.utcnow(),
 )


@app.put(
"/shops/{shop_id}/items/{item_id}",
tags=["Items"]
)
async def update_item(
shop_id: int, # Path parameter
item_id: Annotated[int, Path(ge=1)], # Path + validation
q: Optional[str] = None, # Query parameter
item: ItemUpdate = Body(...), # Request body (obligatoire)
note: str = Body(default=""), # Champ body supplémentaire
):
 result = {
 "shop_id": shop_id,
 "item_id": item_id,
 "update": item.model_dump(exclude_none=True),
 }
 if q:
    result["query"] = q
 if note:
    result["note"] = note
 return result


@app.post("/create-and-redirect")
async def create_and_redirect():
 """Redirection après création."""
 return RedirectResponse(url="/items", status_code=303)
