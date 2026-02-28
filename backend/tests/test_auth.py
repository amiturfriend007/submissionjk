import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_signup_and_login(tmp_path, monkeypatch):
    # override database URL to sqlite in-memory for tests
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/auth/signup", json={
            "email": "test@example.com",
            "password": "secret",
            "full_name": "Tester",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"

        login = await ac.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "secret"},
        )
        assert login.status_code == 200
        token = login.json().get("access_token")
        assert token
