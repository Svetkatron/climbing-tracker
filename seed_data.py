"""
Скрипт для заполнения базы данных тестовыми данными
Запуск: python seed_data.py
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app import models
from app.auth import get_password_hash

def seed_database():
    print("Начинаем заполнение базы данных...")
    
    # Удаляем старые данные и создаём таблицы заново
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # ========== 1. ПОЛЬЗОВАТЕЛИ ==========
    print("Создаём пользователей...")
    
    users = [
        {
            "username": "alex_climber",
            "email": "alex@example.com",
            "password": "alex123",
            "height": 175,
            "weight": 68,
            "climbing_level": "intermediate"
        },
        {
            "username": "maria_rock",
            "email": "maria@example.com",
            "password": "maria123",
            "height": 162,
            "weight": 55,
            "climbing_level": "advanced"
        },
        {
            "username": "dmitry_crush",
            "email": "dmitry@example.com",
            "password": "dmitry123",
            "height": 182,
            "weight": 78,
            "climbing_level": "beginner"
        },
        {
            "username": "elena_peak",
            "email": "elena@example.com",
            "password": "elena123",
            "height": 168,
            "weight": 60,
            "climbing_level": "expert"
        },
    ]
    
    db_users = []
    for user_data in users:
        hashed = get_password_hash(user_data["password"])
        user = models.User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed,
            height=user_data["height"],
            weight=user_data["weight"],
            climbing_level=user_data["climbing_level"]
        )
        db.add(user)
        db.flush()
        db_users.append(user)
    
    db.commit()
    print(f"   ✅ Создано {len(users)} пользователей")
    
    # ========== 2. ТРАССЫ ==========
    print("🧗 Создаём трассы...")
    
    routes_data = [
        {"name": "Лёгкая стенка", "grade": "5a", "grade_value": 5.0, "location": "Зал 'Высота'", "route_type": "difficulty"},
        {"name": "Зелёный дракон", "grade": "5c", "grade_value": 5.2, "location": "Скалодром 'Стена'", "route_type": "boulder"},
        {"name": "Классика", "grade": "6a", "grade_value": 6.0, "location": "Зал 'Высота'", "route_type": "difficulty"},
        {"name": "Кандидат", "grade": "6a+", "grade_value": 6.2, "location": "Скалодром 'Стена'", "route_type": "difficulty"},
        {"name": "Драконья пасть", "grade": "6b", "grade_value": 6.3, "location": "Зал 'Высота'", "route_type": "difficulty"},
        {"name": "Зеркало", "grade": "6b+", "grade_value": 6.5, "location": "Скалодром 'Стена'", "route_type": "boulder"},
        {"name": "Атлант", "grade": "6c", "grade_value": 6.7, "location": "Зал 'Высота'", "route_type": "difficulty"},
        {"name": "Титан", "grade": "7a", "grade_value": 7.0, "location": "Скалодром 'Стена'", "route_type": "difficulty"},
    ]
    
    db_routes = []
    for route_data in routes_data:
        route = models.Route(**route_data)
        db.add(route)
        db.flush()
        db_routes.append(route)
    
    db.commit()
    print(f"   ✅ Создано {len(routes_data)} трасс")
    
    # ========== 3. ТРЕНИРОВКИ ==========
    print("Добавляем тренировки...")
    
    start_date = datetime.now() - timedelta(days=60)
    workout_count = 0
    
    for user in db_users:
        # Определяем, какие трассы подходят уровню пользователя
        level_map = {
            "beginner": ["5a", "5c", "6a"],
            "intermediate": ["5c", "6a", "6a+", "6b", "6b+"],
            "advanced": ["6a+", "6b", "6b+", "6c", "7a"],
            "expert": ["6b+", "6c", "7a", "7a+", "7b"]
        }
        
        level_routes = [r for r in db_routes if r.grade in level_map.get(user.climbing_level, ["6a", "6a+"])]
        
        for day in range(0, 60, 3):  # тренировка каждые 3 дня
            date = start_date + timedelta(days=day)
            if date > datetime.now():
                continue
            
            # Выбираем случайную трассу из подходящих
            if not level_routes:
                continue
            
            route = random.choice(level_routes)
            attempts = random.randint(1, 5)
            
            # Вероятность успеха зависит от сложности трассы
            grade_value = route.grade_value
            success_prob = max(0.2, min(0.9, 0.9 - (grade_value - 6.0) * 0.15))
            success = random.random() < success_prob
            
            workout = models.Workout(
                user_id=user.id,
                route_id=route.id,
                date=date,
                attempts=attempts,
                success=success,
                notes=f"Тренировка от {date.strftime('%d.%m.%Y')}",
                is_competition=random.random() < 0.1
            )
            db.add(workout)
            workout_count += 1
    
    db.commit()
    print(f"   Создано {workout_count} тренировок")
    
    # ========== 4. УВЕДОМЛЕНИЯ ==========
    print(" Создаём уведомления...")
    
    # Уведомление о новой трассе для всех пользователей
    for user in db_users:
        notification = models.Notification(
            user_id=user.id,
            route_id=db_routes[0].id,
            type="new_route",
            message=f"🧗 Новая трасса добавлена: {db_routes[0].name} (сложность {db_routes[0].grade})!",
            is_read=False
        )
        db.add(notification)
    
    db.commit()
    print(f"   ✅ Создано {len(db_users)} уведомлений")
    
    # ========== ИТОГ ==========
    print("\n" + "="*50)
    print("🎉 БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!")
    print("="*50)
    print(f"📊 Итоговая статистика:")
    print(f"   👥 Пользователей: {len(db_users)}")
    print(f"   🧗 Трасс: {len(db_routes)}")
    print(f"   📝 Тренировок: {workout_count}")
    print(f"   🔔 Уведомлений: {len(db_users)}")
    print("="*50)
    print("\n📋 Данные для тестового входа:")
    for user in db_users:
        print(f"   🔑 {user.username} / {user.username.split('_')[0]}123")
    
    db.close()

if __name__ == "__main__":
    seed_database()