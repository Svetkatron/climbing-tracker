from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/users", tags=["users"])

# Папка для аватаров
AVATAR_DIR = "uploads/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

# НОВЫЙ ЭНДПОИНТ: Загрузка аватара
@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Загрузить аватар пользователя"""
    
    # Проверяем тип файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Генерируем уникальное имя файла
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"user_{current_user.id}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(AVATAR_DIR, unique_filename)
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Удаляем старый аватар, если был
    if current_user.avatar_url:
        old_avatar_path = os.path.join("uploads", current_user.avatar_url.replace("/uploads/", ""))
        if os.path.exists(old_avatar_path):
            os.remove(old_avatar_path)
    
    # Обновляем URL аватара в базе
    avatar_url = f"/uploads/avatars/{unique_filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    
    return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully"}

# НОВЫЙ ЭНДПОИНТ: Удаление аватара
@router.delete("/me/avatar")
def delete_avatar(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить аватар пользователя"""
    
    if not current_user.avatar_url:
        raise HTTPException(status_code=404, detail="No avatar found")
    
    # Удаляем файл
    avatar_path = os.path.join("uploads", current_user.avatar_url.replace("/uploads/", ""))
    if os.path.exists(avatar_path):
        os.remove(avatar_path)
    
    # Обнуляем URL в базе
    current_user.avatar_url = None
    db.commit()
    
    return {"message": "Avatar deleted successfully"}