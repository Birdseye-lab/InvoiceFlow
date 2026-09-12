from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_requires_authentication():
    response = client.get("/dashboard")

    assert response.status_code == 401


def test_dashboard():
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
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_clients" in data
    assert "total_projects" in data
    assert "total_invoices" in data
    assert "paid_invoices" in data
    assert "unpaid_invoices" in data
    assert "total_revenue" in data