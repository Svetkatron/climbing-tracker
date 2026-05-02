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
    avatar_url: str | None = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    height: Optional[float] = None
    weight: Optional[float] = None
    climbing_level: Optional[str] = None
    avatar_url: str | None = None

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
    location: str | None = None
    route_type: str = "difficulty"
    photo_url: str | None = None  

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    name: str | None = None
    grade: str | None = None
    grade_value: float | None = None
    location: str | None = None
    route_type: str | None = None
    photo_url: str | None = None 

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
    is_competition: bool = False
    reminder_sent: bool = False

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    attempts: Optional[int] = None
    success: Optional[bool] = None
    notes: Optional[str] = None
    date: Optional[datetime] = None
    is_competition: bool | None = None
    reminder_sent: bool | None = None

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

# ========== Analytics schemas ==========
class GradeStat(BaseModel):
    grade: str
    total_attempts: int
    successful_attempts: int
    success_rate: float

class ProgressStats(BaseModel):
    total_workouts: int
    total_attempts: int
    success_rate: float
    best_grade: str
    improvement_rate: float
    grade_breakdown: List[GradeStat]

class RouteRecommendation(BaseModel):
    route_id: int
    name: str
    grade: str
    grade_value: float
    difficulty_increase: float
    success_rate_others: float
    recommendation_score: float

# ========== Notification schemas ==========
class NotificationBase(BaseModel):
    type: str
    message: str
    route_id: int | None = None
    is_read: bool = False

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationMarkRead(BaseModel):
    notification_id: int