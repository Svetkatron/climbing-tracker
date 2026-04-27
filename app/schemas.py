from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ========== User schemas ==========
class UserBase(BaseModel):
    username: str
    email: EmailStr
    height: Optional[float] = None
    weight: Optional[float] = None
    climbing_level: str = "intermediate"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    height: Optional[float] = None
    weight: Optional[float] = None
    climbing_level: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== Route schemas ==========
class RouteBase(BaseModel):
    name: str
    grade: str
    grade_value: float
    location: Optional[str] = None
    route_type: str = "difficulty"  # "difficulty" или "boulder"

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    grade_value: Optional[float] = None
    location: Optional[str] = None
    route_type: Optional[str] = None

class RouteResponse(RouteBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== Workout schemas ==========
class WorkoutBase(BaseModel):
    route_id: int
    date: Optional[datetime] = None
    attempts: int = 1
    success: bool = False
    notes: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    attempts: Optional[int] = None
    success: Optional[bool] = None
    notes: Optional[str] = None
    date: Optional[datetime] = None

class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime
    route: Optional[RouteResponse] = None
    
    class Config:
        from_attributes = True

# ========== Auth schemas ==========
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ========== Analytics schemas ==========
class ProgressStats(BaseModel):
    total_workouts: int
    total_attempts: int
    success_rate: float
    avg_grade_success: float
    best_grade: str
    improvement_rate: float

class RouteRecommendation(BaseModel):
    route_id: int
    name: str
    grade: str
    grade_value: float
    difficulty_increase: float
    success_rate_others: float
    recommendation_score: float

# ========== Auth schemas ==========
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None