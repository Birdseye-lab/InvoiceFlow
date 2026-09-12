from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_projects_requires_authentication():
    response = client.get("/projects")

    assert response.status_code == 401


def test_get_projects():
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
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_project():
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
        "/projects",
        json={
            "name": "Pytest Project",
            "description": "Project created by automated test",
            "client_id": 12,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Pytest Project"
    assert data["client_id"] == 12