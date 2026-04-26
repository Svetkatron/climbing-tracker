from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from app.routers import auth

# Создаём все таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Climbing Tracker API", version="1.0.0")

# Подключаем роутеры
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy", "database": "connected"}