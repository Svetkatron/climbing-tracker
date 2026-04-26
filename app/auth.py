from passlib.context import CryptContext

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Превращает пароль в хеш (необратимо)"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли пароль с хешем"""
    return pwd_context.verify(plain_password, hashed_password)