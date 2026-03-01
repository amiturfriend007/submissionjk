"""Integration tests for book ingestion and library mechanics."""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_book_with_text_upload_and_list_books():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_resp = await ac.post(
            "/books/",
            data={
                "title": "Uploaded Book",
                "author": "Uploader",
                "description": "text upload",
            },
            files={"file": ("uploaded.txt", b"hello world", "text/plain")},
        )
        assert create_resp.status_code == 200
        created = create_resp.json()
        assert created["title"] == "Uploaded Book"
        assert created["author"] == "Uploader"

        books_resp = await ac.get("/books/?page=1")
        assert books_resp.status_code == 200
        payload = books_resp.json()
        assert payload["page"] == 1
        assert isinstance(payload["items"], list)
        assert any(item["title"] == "Uploaded Book" for item in payload["items"])


@pytest.mark.asyncio
async def test_review_requires_borrow_and_borrow_return_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        signup_resp = await ac.post(
            "/auth/signup",
            json={
                "email": "borrower@test.com",
                "password": "secret",
                "full_name": "Borrower",
            },
        )
        assert signup_resp.status_code == 200

        login_resp = await ac.post(
            "/auth/login",
            json={"email": "borrower@test.com", "password": "secret"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        create_resp = await ac.post(
            "/books/",
            data={"title": "Borrowable Book"},
            files={"file": ("book.txt", b"book content", "text/plain")},
        )
        assert create_resp.status_code == 200
        book_id = create_resp.json()["id"]

        review_without_borrow = await ac.post(
            f"/books/{book_id}/reviews",
            headers=auth_headers,
            json={"rating": 5, "comment": "great"},
        )
        assert review_without_borrow.status_code == 403

        borrow_resp = await ac.post(f"/books/{book_id}/borrow", headers=auth_headers)
        assert borrow_resp.status_code == 200

        duplicate_borrow_resp = await ac.post(f"/books/{book_id}/borrow", headers=auth_headers)
        assert duplicate_borrow_resp.status_code == 400

        review_after_borrow = await ac.post(
            f"/books/{book_id}/reviews",
            headers=auth_headers,
            json={"rating": 4, "comment": "solid"},
        )
        assert review_after_borrow.status_code == 200

        return_resp = await ac.post(f"/books/{book_id}/return", headers=auth_headers)
        assert return_resp.status_code == 200

        return_again_resp = await ac.post(f"/books/{book_id}/return", headers=auth_headers)
        assert return_again_resp.status_code == 400
