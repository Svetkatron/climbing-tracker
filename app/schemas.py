from pydantic import BaseModel, EmailStr
from datetime import datetime

# Схема для регистрации (что приходит от пользователя)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Схема для ответа (что возвращает API)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True