from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_clients_requires_authentication():
    response = client.get("/clients")

    assert response.status_code == 401


def test_get_clients():
    response = client.post(
        "/login",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/clients",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_client():
    response = client.post(
        "/login",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.post(
        "/clients",
        json={
            "name": "Test Client",
            "email": "test-client@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Client"
    assert data["email"] == "test-client@example.com"