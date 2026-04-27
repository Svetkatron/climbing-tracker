from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from app.database import engine, Base, get_db
from app import models
from app.routers import auth, routes, workouts, analytics
from app.auth import get_current_active_user 

# Создаём папку для загрузок, если ее нет
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Создаём папку для статики, если её нет
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Climbing Tracker API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Статические файлы (фото и HTML)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

@app.post("/upload-route-photo")
async def upload_route_photo(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user)  # <-- ИСПРАВЛЕНО
):
    """Загрузить фото для трассы"""
    
    # Проверяем тип файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Генерируем уникальное имя файла
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Возвращаем URL для доступа к фото
    photo_url = f"/uploads/{unique_filename}"
    
    return {"photo_url": photo_url}

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