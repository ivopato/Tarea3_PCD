from fastapi import FastAPI, HTTPException, Depends, Security
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import APIKeyHeader

import models
from database import engine, SessionLocal

# cargar las variables de entorno (.env)
load_dotenv()
API_KEY = os.getenv("API_KEY")

# app
app = FastAPI()

# crear las tablas
models.Base.metadata.create_all(bind=engine)

# dependencia DB
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# esquema pydantic (del body request que vamos a enviar)
class User(BaseModel):
    user_name: str
    user_id: int
    user_email: str
    age: int = None
    recomendations: list[str]
    ZIP: str = None

# seguridad por header (validar el api key en el .env)
api_key_header = APIKeyHeader(name="X-API-Key", description="API key por header", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    if API_KEY and api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Could not validate credentials")


# ENDPOINTS

@app.get("/")
def root():
    return {"message": "Users API up. See /docs"}

# crear nuevo user 
@app.post('/api/v1/users', tags=['users'])
def create_user(user: User, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    # Verificar si email ya existe
    existing = db.query(models.Users).filter(models.Users.user_email == user.user_email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user_model = models.Users(
        user_id=user.user_id,
        user_name=user.user_name,
        user_email=user.user_email,
        age=user.age,
        ZIP=user.ZIP,
        recommendations=user.recommendations,
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return {"status": f"User {user.user_id} created"}

# actualizar el user
@app.put("/api/v1/users/{user_id}", tags=["users"])
def update_user(user_id: int, user: User, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    user_model = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    for field, value in user.dict(exclude_unset=True).items():
        setattr(user_model, field, value)

    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return {"status": f"User {user_id} updated"}

# obtener user
@app.get("/api/v1/users/{user_id}", tags=["users"])
def get_user(user_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    user_model = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user_model

# eliminar user
@app.delete("/api/v1/users/{user_id}", tags=["users"])
def delete_user(user_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    user_model = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    db.delete(user_model)
    db.commit()
    return {"deleted_id": user_id}