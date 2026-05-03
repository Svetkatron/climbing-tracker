from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas, auth
from app.notifications import notify_all_users_about_new_route
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import io
from datetime import datetime

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

@router.get("/export/excel")
def export_routes_excel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Экспорт всех трасс в Excel с процентом успешных пролазов"""
    
    routes = db.query(models.Route).all()
    
    # Считаем успешность по каждой трассе
    routes_data = []
    for route in routes:
        # Все тренировки на этой трассе
        workouts = db.query(models.Workout).filter(
            models.Workout.route_id == route.id
        ).all()
        
        total_attempts = sum(w.attempts for w in workouts)
        successful_attempts = sum(w.attempts for w in workouts if w.success)
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        routes_data.append({
            "id": route.id,
            "name": route.name,
            "grade": route.grade,
            "grade_value": route.grade_value,
            "location": route.location or "",
            "route_type": route.route_type,
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "success_rate": round(success_rate, 2),
            "created_at": route.created_at.strftime("%d.%m.%Y") if route.created_at else ""
        })
    
    # Сортируем по популярности (по убыванию успешности)
    routes_data.sort(key=lambda x: x["success_rate"], reverse=True)
    
    # Создаём Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Трассы"
    
    # Заголовки
    headers = ["ID", "Название", "Сложность", "Grade Value", "Локация", 
               "Тип", "Всего попыток", "Успешных попыток", "Успешность (%)", "Дата создания"]
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    
    # Заполняем данными
    for row, route in enumerate(routes_data, 2):
        ws.cell(row=row, column=1, value=route["id"])
        ws.cell(row=row, column=2, value=route["name"])
        ws.cell(row=row, column=3, value=route["grade"])
        ws.cell(row=row, column=4, value=route["grade_value"])
        ws.cell(row=row, column=5, value=route["location"])
        ws.cell(row=row, column=6, value=route["route_type"])
        ws.cell(row=row, column=7, value=route["total_attempts"])
        ws.cell(row=row, column=8, value=route["successful_attempts"])
        
        # Ячейка с успешностью (процент)
        cell = ws.cell(row=row, column=9, value=route["success_rate"])
        if route["success_rate"] >= 70:
            cell.fill = PatternFill(start_color="92d050", end_color="92d050", fill_type="solid")
        elif route["success_rate"] >= 40:
            cell.fill = PatternFill(start_color="ffc000", end_color="ffc000", fill_type="solid")
        else:
            cell.fill = PatternFill(start_color="ff6666", end_color="ff6666", fill_type="solid")
        
        ws.cell(row=row, column=10, value=route["created_at"])
    
    # Настраиваем ширину колонок
    column_widths = [8, 25, 12, 12, 20, 12, 14, 16, 14, 14]
    for i, width in enumerate(column_widths, 1):
        col_letter = chr(64 + i) if i <= 26 else f"A{chr(64 + i - 26)}"
        ws.column_dimensions[col_letter].width = width
    
    # Сохраняем
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=routes_export_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )