from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "backend"


def test_api_health_endpoint() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_requires_prompt() -> None:
    response = client.post("/api/chat", json={"prompt": ""})

    assert response.status_code == 422


def test_chat_returns_model_response(monkeypatch) -> None:
    async def fake_call_ollama(prompt: str) -> dict[str, str]:
        assert prompt == "Hola"
        return {
            "model": "tinyllama",
            "response": "Respuesta simulada",
        }

    monkeypatch.setattr("app.main.call_ollama", fake_call_ollama)

    response = client.post("/api/chat", json={"prompt": "Hola"})

    assert response.status_code == 200
    assert response.json() == {
        "model": "tinyllama",
        "response": "Respuesta simulada",
    }
