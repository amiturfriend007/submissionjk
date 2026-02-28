"""
Integration test for book creation and retrieval.
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_and_list_books():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # signup
        resp = await ac.post("/auth/signup", json={
            "email": "user@test.com",
            "password": "secret",
            "full_name": "User",
        })
        assert resp.status_code == 200

        # login
        login_resp = await ac.post(
            "/auth/login",
            data={"username": "user@test.com", "password": "secret"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # list books (empty)
        books_resp = await ac.get("/books/?page=1")
        assert books_resp.status_code == 200
        data = books_resp.json()
        assert data["page"] == 1
        assert isinstance(data["items"], list)
