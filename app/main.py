from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models
from app.routers import auth, routes, workouts, analytics

# Создаём все таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Climbing Tracker API",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)

# Настройка OAuth2 для Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(routes.router)
app.include_router(workouts.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "Hello climber"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy", "database": "connected"}