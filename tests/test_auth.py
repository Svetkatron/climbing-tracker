def test_register(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "climbing_level": "intermediate"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_register_duplicate(client):
    # Первая регистрация
    client.post("/auth/register", json={
        "username": "duplicate",
        "email": "dup@example.com",
        "password": "test123"
    })
    # Вторая регистрация (дубликат)
    response = client.post("/auth/register", json={
        "username": "duplicate",
        "email": "dup@example.com",
        "password": "test123"
    })
    assert response.status_code == 400

def test_login(client):
    # Сначала регистрируем
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpass"
    })
    # Тестируем логин
    response = client.post("/auth/login", data={
        "username": "loginuser",
        "password": "loginpass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def get_token(client):
    """Вспомогательная функция для получения токена в тестах"""
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123"
    })
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "test123"
    })
    return response.json()["access_token"]