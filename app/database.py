from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Подключаемся к файлу базы данных climbing.db
engine = create_engine(
    "sqlite:///./climbing.db",
    connect_args={"check_same_thread": False}
)

# Фабрика сессий для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()

# Функция для получения сессии БД в каждом запросе
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()