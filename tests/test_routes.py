from tests.test_auth import get_token

def test_create_route(client):
    token = get_token(client)
    response = client.post("/routes/", 
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Route",
            "grade": "6a+",
            "grade_value": 6.2,
            "location": "Test Gym",
            "route_type": "difficulty"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Route"

def test_update_route(client):
    token = get_token(client)
    # Создаём
    resp = client.post("/routes/", headers={"Authorization": f"Bearer {token}"},
                       json={"name": "Old Name", "grade": "5c", "grade_value": 5.2})
    route_id = resp.json()["id"]
    # Обновляем
    resp2 = client.put(f"/routes/{route_id}", headers={"Authorization": f"Bearer {token}"},
                       json={"name": "New Name"})
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "New Name"

def test_delete_route(client):
    token = get_token(client)
    resp = client.post("/routes/", headers={"Authorization": f"Bearer {token}"},
                       json={"name": "To Delete", "grade": "5c", "grade_value": 5.2})
    route_id = resp.json()["id"]
    resp2 = client.delete(f"/routes/{route_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 204
    
    # Проверяем, что удалилась
    resp3 = client.get(f"/routes/{route_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp3.status_code == 404

def test_get_routes(client):
    token = get_token(client)
    response = client.get("/routes/", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)