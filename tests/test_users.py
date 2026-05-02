def get_token(client):
    client.post("/auth/register", json={
        "username": "avataruser",
        "email": "avatar@example.com",
        "password": "avatar123"
    })
    resp = client.post("/auth/login", data={
        "username": "avataruser",
        "password": "avatar123"
    })
    return resp.json()["access_token"]

def test_upload_avatar(client):
    token = get_token(client)
    files = {"file": ("avatar.jpg", b"fakeimagecontent", "image/jpeg")}
    resp = client.post("/users/me/avatar", headers={"Authorization": f"Bearer {token}"}, files=files)
    assert resp.status_code == 200
    assert "avatar_url" in resp.json()

def test_delete_avatar(client):
    token = get_token(client)
    files = {"file": ("avatar.jpg", b"fakeimagecontent", "image/jpeg")}
    client.post("/users/me/avatar", headers={"Authorization": f"Bearer {token}"}, files=files)
    resp = client.delete("/users/me/avatar", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200