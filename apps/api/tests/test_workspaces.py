from fastapi.testclient import TestClient

from app.main import app


def test_create_and_list_workspaces() -> None:
    with TestClient(app) as client:
        create_response = client.post("/workspaces", json={"name": "Acme Knowledge Base"})
        list_response = client.get("/workspaces")

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Acme Knowledge Base"
    assert "id" in created

    assert list_response.status_code == 200
    assert any(workspace["id"] == created["id"] for workspace in list_response.json())
