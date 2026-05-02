def test_progress_stats(client):
    # Регистрируем и логинимся
    client.post("/auth/register", json={
        "username": "analyticsuser",
        "email": "analytics@example.com",
        "password": "analytics123"
    })
    login_resp = client.post("/auth/login", data={
        "username": "analyticsuser",
        "password": "analytics123"
    })
    token = login_resp.json()["access_token"]
    
    # Создаём трассу
    route_resp = client.post("/routes/", 
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Analytics Route",
            "grade": "6a",
            "grade_value": 6.0
        }
    )
    route_id = route_resp.json()["id"]
    
    # Добавляем тренировки
    client.post("/workouts/",
        headers={"Authorization": f"Bearer {token}"},
        json={"route_id": route_id, "attempts": 3, "success": True}
    )
    client.post("/workouts/",
        headers={"Authorization": f"Bearer {token}"},
        json={"route_id": route_id, "attempts": 2, "success": False}
    )
    
    # Проверяем статистику
    response = client.get("/analytics/progress",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_workouts" in data
    assert "total_attempts" in data
    assert "success_rate" in data

def test_recommendations(client):
    # Аналогично: регистрация, логин, создание трассы, тренировки
    client.post("/auth/register", json={
        "username": "recuser",
        "email": "rec@example.com",
        "password": "rec123"
    })
    login_resp = client.post("/auth/login", data={
        "username": "recuser",
        "password": "rec123"
    })
    token = login_resp.json()["access_token"]
    
    response = client.get("/analytics/recommendations",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Может быть 200 или 404 (если нет рекомендаций)
    assert response.status_code in [200, 404]