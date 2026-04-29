from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas, auth
from app.notifications import notify_all_users_about_new_route

router = APIRouter(prefix="/routes", tags=["routes"])

@router.get("/", response_model=List[schemas.RouteResponse]) # Не забыть добавить фото
def get_routes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    routes = db.query(models.Route).offset(skip).limit(limit).all()
    return routes

@router.get("/{route_id}", response_model=schemas.RouteResponse)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

@router.post("/", response_model=schemas.RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(
    route: schemas.RouteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_route = models.Route(**route.model_dump())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    
    # Отправляем уведомления пользователям
    notify_all_users_about_new_route(
        db=db,
        route_id=db_route.id,
        route_name=db_route.name,
        grade=db_route.grade
    )
    
    return db_route

@router.put("/{route_id}", response_model=schemas.RouteResponse)
def update_route(
    route_id: int,
    route_update: schemas.RouteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    for key, value in route_update.model_dump(exclude_unset=True).items():
        setattr(route, key, value)
    
    db.commit()
    db.refresh(route)
    return route

@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    route = db.query(models.Route).filter(models.Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    db.delete(route)
    db.commit()
    return None


