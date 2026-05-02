from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    climbing_level = Column(String, default="intermediate")
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    grade = Column(String, nullable=False)          # например "6a+"
    grade_value = Column(Float, nullable=False)     # числовое значение для сортировки
    location = Column(String, nullable=True)
    route_type = Column(String, default="difficulty")  # "difficulty" или "boulder"
    photo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workouts = relationship("Workout", back_populates="route")

class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    attempts = Column(Integer, default=1)          # количество попыток на этой тренировке
    success = Column(Boolean, default=False)      # пройдена ли трасса
    notes = Column(Text, nullable=True)           # комментарий пользователя к этой тренировке
    is_competition = Column(Boolean, default=False) # по умолчанию тренировка
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="workouts")
    route = relationship("Route", back_populates="workouts")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    type = Column(String, nullable=False)  # "new_route"
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")
    route = relationship("Route")