from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/workouts", tags=["workouts"])

@router.get("/", response_model=List[schemas.WorkoutResponse])
def get_workouts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    workouts = db.query(models.Workout).filter(
        models.Workout.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return workouts

@router.get("/{workout_id}", response_model=schemas.WorkoutResponse)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@router.post("/", response_model=schemas.WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout: schemas.WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    route = db.query(models.Route).filter(models.Route.id == workout.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    db_workout = models.Workout(
        user_id=current_user.id,
        route_id=workout.route_id,
        attempts=workout.attempts,
        success=workout.success,
        notes=workout.notes,
        date=workout.date or datetime.utcnow()
    )
    
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.put("/{workout_id}", response_model=schemas.WorkoutResponse)
def update_workout(
    workout_id: int,
    workout_update: schemas.WorkoutUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    update_data = workout_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workout, key, value)
    
    db.commit()
    db.refresh(workout)
    return workout

@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db.delete(workout)
    db.commit()
    return None