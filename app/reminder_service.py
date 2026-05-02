import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

def check_upcoming_workouts():
    """Проверяет тренировки, которые будут через 24 часа, и отправляет уведомления"""
    
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        
        # Ищем тренировки, которые:
        # 1. Будут через 24 часа (± 1 час, чтобы не пропустить)
        # 2. Ещё не отправлено напоминание
        # 3. Дата в будущем
        upcoming_workouts = db.query(models.Workout).filter(
            models.Workout.date >= tomorrow - timedelta(hours=1),
            models.Workout.date <= tomorrow + timedelta(hours=1),
            models.Workout.date > now,
            models.Workout.reminder_sent == False
        ).all()
        
        for workout in upcoming_workouts:
            # Создаём уведомление для пользователя
            notification = models.Notification(
                user_id=workout.user_id,
                route_id=workout.route_id,
                type="workout_reminder",
                message=f"🔔 Напоминание: у вас запланирована {'тренировка' if not workout.is_competition else 'соревнование'} на {workout.date.strftime('%d.%m.%Y в %H:%M')}!",
                is_read=False
            )
            db.add(notification)
            
            # Отмечаем, что напоминание отправлено
            workout.reminder_sent = True
        
        db.commit()
        
    except Exception as e:
        print(f"Error in reminder service: {e}")
    finally:
        db.close()


def reminder_scheduler():
    """Запускает проверку каждые 30 минут"""
    while True:
        check_upcoming_workouts()
        time.sleep(1800)  # 30 минут


def start_reminder_service():
    """Запускает сервис напоминаний в фоновом потоке"""
    thread = threading.Thread(target=reminder_scheduler, daemon=True)
    thread.start()
    print("Reminder service started")