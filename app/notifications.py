from sqlalchemy.orm import Session
from app import models, schemas

def notify_all_users_about_new_route(db: Session, route_id: int, route_name: str, grade: str):
    """Отправить уведомление всем пользователям о новой трассе"""
    
    # Получаем всех пользователей
    users = db.query(models.User).all()
    
    message = f"🧗 Новая трасса добавлена: {route_name} (сложность {grade})!"
    
    for user in users:
        notification = models.Notification(
            user_id=user.id,
            route_id=route_id,
            type="new_route",
            message=message,
            is_read=False
        )
        db.add(notification)
    
    db.commit()
    return len(users)