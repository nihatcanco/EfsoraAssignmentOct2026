from tests.conftest import register


def test_register_and_login(client):
    register(client)

    res = client.post("/auth/login", json={"email": "Test@Example.com", "password": "password123"})
    assert res.status_code == 200
    token = res.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "test@example.com"


def test_register_duplicate_email(client):
    register(client)
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 409


def test_login_wrong_password(client):
    register(client)
    res = client.post("/auth/login", json={"email": "test@example.com", "password": "wrongpassword"})
    assert res.status_code == 401


def test_protected_routes_need_token(client):
    assert client.get("/notes").status_code == 401
    assert client.post("/notes", json={"content": "hi"}).status_code == 401
    assert client.delete("/notes/1").status_code == 401


def test_invalid_token_rejected(client):
    res = client.get("/notes", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401
