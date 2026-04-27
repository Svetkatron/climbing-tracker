from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from collections import defaultdict
from app import models, schemas

def calculate_progress_stats(user_id: int, db: Session) -> schemas.ProgressStats:
    """Рассчитывает статистику прогресса пользователя"""
    
    workouts = db.query(models.Workout).filter(models.Workout.user_id == user_id).all()
    
    if not workouts:
        return schemas.ProgressStats(
            total_workouts=0,
            total_attempts=0,
            success_rate=0.0,
            best_grade="N/A",
            improvement_rate=0.0,
            grade_breakdown=[]
        )
    
    # Статистика по категориям сложности
    grade_stats = defaultdict(lambda: {"total": 0, "success": 0})
    
    for workout in workouts:
        route = workout.route
        if route:
            grade = route.grade
            grade_stats[grade]["total"] += workout.attempts
            if workout.success:
                grade_stats[grade]["success"] += workout.attempts
    
    # Формируем breakdown по категориям
    breakdown = []
    for grade, stats in sorted(grade_stats.items()):
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        breakdown.append(schemas.GradeStat(
            grade=grade,
            total_attempts=stats["total"],
            successful_attempts=stats["success"],
            success_rate=round(success_rate, 2)
        ))
    
    # Общая статистика по попыткам
    total_attempts = sum(stats["total"] for stats in grade_stats.values())
    total_success = sum(stats["success"] for stats in grade_stats.values())
    overall_success_rate = (total_success / total_attempts * 100) if total_attempts > 0 else 0
    
    # Лучшая категория (максимальная сложность с успешными попытками)
    best_grade = "N/A"
    for stat in reversed(breakdown):  # идём от сложных к простым
        if stat.successful_attempts > 0:
            best_grade = stat.grade
            break
    
    # Улучшение за последние 30 дней (по успешности попыток)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_attempts = 0
    recent_success = 0
    older_attempts = 0
    older_success = 0
    
    for workout in workouts:
        if workout.date >= thirty_days_ago:
            recent_attempts += workout.attempts
            if workout.success:
                recent_success += workout.attempts
        else:
            older_attempts += workout.attempts
            if workout.success:
                older_success += workout.attempts
    
    recent_rate = (recent_success / recent_attempts * 100) if recent_attempts > 0 else 0
    older_rate = (older_success / older_attempts * 100) if older_attempts > 0 else 0
    improvement_rate = recent_rate - older_rate if older_attempts > 0 else 0
    
    return schemas.ProgressStats(
        total_workouts=len(workouts),
        total_attempts=total_attempts,
        success_rate=round(overall_success_rate, 2),
        best_grade=best_grade,
        improvement_rate=round(improvement_rate, 2),
        grade_breakdown=breakdown
    )


def recommend_routes(user_id: int, db: Session, limit: int = 3) -> List[schemas.RouteRecommendation]:
    """Рекомендует трассы на основе уровня пользователя и успешности других"""
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    
    # Преобразуем уровень пользователя в число
    level_map = {
        "beginner": 5.0,
        "intermediate": 6.0,
        "advanced": 7.0,
        "expert": 8.0
    }
    user_level_value = level_map.get(user.climbing_level, 6.0)
    
    # Получаем ID трасс, которые пользователь уже проходил
    completed_route_ids = set()
    user_workouts = db.query(models.Workout).filter(models.Workout.user_id == user_id).all()
    for w in user_workouts:
        if w.route_id:
            completed_route_ids.add(w.route_id)
    
    # Получаем доступные трассы
    if completed_route_ids:
        available_routes = db.query(models.Route).filter(
            models.Route.id.notin_(completed_route_ids)
        ).all()
    else:
        available_routes = db.query(models.Route).all()
    
    recommendations = []
    
    for route in available_routes:
        # Насколько трасса сложнее уровня пользователя
        difficulty_increase = route.grade_value - user_level_value
        
        # Оценка сложности
        if difficulty_increase < -0.5:
            difficulty_score = 0.3
        elif -0.5 <= difficulty_increase <= 0.5:
            difficulty_score = 1.0
        elif 0.5 < difficulty_increase <= 1.5:
            difficulty_score = 1.2
        else:
            difficulty_score = 0.8
        
        # Успешность у других пользователей (по попыткам)
        other_workouts = db.query(models.Workout).filter(
            models.Workout.route_id == route.id,
            models.Workout.user_id != user_id
        ).all()
        
        success_rate_others = 0
        if other_workouts:
            total_attempts = sum(w.attempts for w in other_workouts)
            successful_attempts = sum(w.attempts for w in other_workouts if w.success)
            success_rate_others = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Итоговый score
        recommendation_score = (difficulty_score * 0.6) + (success_rate_others / 100 * 0.4)
        
        recommendations.append(schemas.RouteRecommendation(
            route_id=route.id,
            name=route.name,
            grade=route.grade,
            grade_value=route.grade_value,
            difficulty_increase=round(difficulty_increase, 2),
            success_rate_others=round(success_rate_others, 2),
            recommendation_score=round(recommendation_score, 3)
        ))
    
    recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
    return recommendations[:limit]