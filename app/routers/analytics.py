from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas, auth, algorithms

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/progress", response_model=schemas.ProgressStats)
def get_progress_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Получить статистику прогресса пользователя"""
    return algorithms.calculate_progress_stats(current_user.id, db)

@router.get("/recommendations", response_model=List[schemas.RouteRecommendation])
def get_route_recommendations(
    limit: int = 3,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Получить рекомендации трасс на основе уровня и истории"""
    recommendations = algorithms.recommend_routes(current_user.id, db, limit)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations available")
    return recommendations