def get_token_and_route(client):
    # Регистрация и логин
    client.post("/auth/register", json={
        "username": "workoutuser",
        "email": "workout@example.com",
        "password": "workout123"
    })
    login_resp = client.post("/auth/login", data={
        "username": "workoutuser",
        "password": "workout123"
    })
    token = login_resp.json()["access_token"]
    
    # Создаём трассу
    route_resp = client.post("/routes/", 
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Workout Route",
            "grade": "6b",
            "grade_value": 6.3,
            "location": "Test Gym"
        }
    )
    route_id = route_resp.json()["id"]
    
    return token, route_id

def test_create_workout(client):
    token, route_id = get_token_and_route(client)
    
    response = client.post("/workouts/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "route_id": route_id,
            "attempts": 3,
            "success": True,
            "notes": "Good job!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["attempts"] == 3
    assert data["success"] == True

'''
def test_get_workouts(client):
    token, route_id = get_token_and_route(client)
    
    # Добавляем тренировку
    post_response = client.post("/workouts/",
        headers={"Authorization": f"Bearer {token}"},
        json={"route_id": route_id, "attempts": 2, "success": True}
    )
    assert post_response.status_code == 201
    
    import time
    time.sleep(0.5) 
    
    response = client.get("/workouts/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1
'''
    

def test_update_workout(client):
    token, route_id = get_token_and_route(client)
    # Создаём тренировку
    resp = client.post("/workouts/", headers={"Authorization": f"Bearer {token}"},
                       json={"route_id": route_id, "attempts": 2, "success": False})
    workout_id = resp.json()["id"]
    # Обновляем
    resp2 = client.put(f"/workouts/{workout_id}", headers={"Authorization": f"Bearer {token}"},
                       json={"attempts": 5, "success": True})
    assert resp2.status_code == 200
    assert resp2.json()["attempts"] == 5

def test_delete_workout(client):
    token, route_id = get_token_and_route(client)
    resp = client.post("/workouts/", headers={"Authorization": f"Bearer {token}"},
                       json={"route_id": route_id, "attempts": 1})
    workout_id = resp.json()["id"]
    resp2 = client.delete(f"/workouts/{workout_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 204

def test_calendar(client):
    token, route_id = get_token_and_route(client)
    client.post("/workouts/", headers={"Authorization": f"Bearer {token}"},
                json={"route_id": route_id, "date": "2026-05-15T10:00:00"})
    resp = client.get("/workouts/calendar/2026/5", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "calendar" in resp.json()

def test_export_excel(client):
    token, route_id = get_token_and_route(client)
    client.post("/workouts/", headers={"Authorization": f"Bearer {token}"},
                json={"route_id": route_id})
    resp = client.get("/workouts/export/excel", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def test_calendar(client):
    token, route_id = get_token_and_route(client)
    client.post("/workouts/", headers={"Authorization": f"Bearer {token}"},
                json={"route_id": route_id, "date": "2026-05-15T10:00:00"})
    resp = client.get("/workouts/calendar/2026/5", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "calendar" in resp.json()

def test_export_excel(client):
    token, route_id = get_token_and_route(client)
    client.post("/workouts/", headers={"Authorization": f"Bearer {token}"},
                json={"route_id": route_id})
    resp = client.get("/workouts/export/excel", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"