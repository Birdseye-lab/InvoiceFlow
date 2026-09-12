import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register():
    response = client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "password123",
        },
    )

    assert response.status_code in [200, 400]


def test_user_cannot_access_other_user_client():
    response = client.post(
        "/login",
        data={
            "username": "second@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/clients/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


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

    unique_email = f"pytest-{uuid.uuid4()}@example.com"

    response = client.post(
        "/clients",
        json={
            "name": "Pytest Client",
            "email": unique_email,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Pytest Client"
    assert data["email"] == unique_email


def test_user_cannot_access_other_user_project():
    response = client.post(
        "/login",
        data={
            "username": "second@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/projects/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_user_cannot_access_other_user_invoice():
    response = client.post(
        "/login",
        data={
            "username": "second@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/invoices/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404