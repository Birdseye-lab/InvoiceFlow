import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_invoices_requires_authentication():
    response = client.get("/invoices")

    assert response.status_code == 401


def test_get_invoices():
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
        "/invoices",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_invoice():
    response = client.post(
        "/login",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    unique_number = f"TEST-INV-{uuid.uuid4()}"

    response = client.post(
        "/invoices",
        json={
            "number": unique_number,
            "amount": 500.00,
            "status": "unpaid",
            "project_id": 5,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["number"] == unique_number
    assert data["amount"] == 500.00
    assert data["status"] == "unpaid"
    assert data["project_id"] == 5