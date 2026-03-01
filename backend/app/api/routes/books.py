import asyncio
from io import BytesIO
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    status,
)
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pypdf import PdfReader

from app.db import models
from app.db.session import get_db
from app.schemas import book as book_schemas, review as review_schemas
from app.api.deps.auth import get_current_user
from app.services.storage import get_storage, StorageBackend
from app.tasks.llm_tasks import generate_summary, analyze_review
from app.tasks.review_tasks import update_book_consensus

router = APIRouter()
ALLOWED_EXTENSIONS = {".txt", ".pdf"}
ALLOWED_CONTENT_TYPES = {"text/plain", "application/pdf"}


def _summary_status(summary: Optional[str]) -> str:
    if not summary:
        return "pending"
    if summary.strip() == "__SUMMARY_FAILED__":
        return "failed"
    return "ready"


def _extract_text(file_bytes: bytes, ext: str) -> str:
    if ext == ".pdf":
        try:
            reader = PdfReader(BytesIO(file_bytes))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception:
            return ""
    try:
        return file_bytes.decode("utf-8")
    except Exception:
        return ""


@router.post("/", response_model=book_schemas.BookRead)
async def create_book(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    file: UploadFile = File(...),
    author: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file content type")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    book = models.Book(title=title, author=author, description=description, file_path="")
    db.add(book)
    await db.commit()
    await db.refresh(book)

    path = await storage.save(BytesIO(file_bytes), file.filename or "book.txt")
    book.file_path = path
    await db.commit()
    await db.refresh(book)

    text = _extract_text(file_bytes, ext)
    asyncio.create_task(generate_summary(book.id, text))
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "summary": book.summary,
        "summary_status": "pending",
        "current_borrower": None,
        "recent_reviews": [],
    }


@router.get("/", response_model=book_schemas.BookList)
async def list_books(page: int = 1, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Book).offset((page - 1) * 10).limit(10)
    result = await db.execute(stmt)
    books = result.scalars().all()

    items = []
    for book in books:
        active_borrow_stmt = (
            select(models.User.full_name, models.User.email)
            .join(models.Borrow, models.Borrow.user_id == models.User.id)
            .where(
                models.Borrow.book_id == book.id,
                models.Borrow.returned_at.is_(None),
            )
            .order_by(models.Borrow.borrowed_at.desc())
            .limit(1)
        )
        active_borrow = (await db.execute(active_borrow_stmt)).first()
        current_borrower = None
        if active_borrow:
            current_borrower = active_borrow[0] or active_borrow[1]

        reviews_stmt = (
            select(models.User.full_name, models.User.email, models.Review.rating, models.Review.comment)
            .join(models.Review, models.Review.user_id == models.User.id)
            .where(
                models.Review.book_id == book.id,
                models.Review.comment.is_not(None),
                models.Review.comment != "",
            )
            .order_by(models.Review.created_at.desc())
            .limit(5)
        )
        review_rows = (await db.execute(reviews_stmt)).all()
        review_snippets = [
            {
                "reviewer": row[0] or row[1],
                "rating": row[2],
                "comment": row[3],
            }
            for row in review_rows
        ]

        items.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "summary": book.summary,
                "summary_status": _summary_status(book.summary),
                "current_borrower": current_borrower,
                "recent_reviews": review_snippets,
            }
        )

    return {"items": items, "page": page}


@router.put("/{book_id}", response_model=book_schemas.BookRead)
async def update_book(
    book_id: int, data: book_schemas.BookUpdate, db: AsyncSession = Depends(get_db)
):
    book = await db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(book, field, value)
    await db.commit()
    await db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    storage = get_storage()
    await storage.delete(book.file_path)
    await db.delete(book)
    await db.commit()
    return None


@router.post("/{book_id}/borrow")
async def borrow_book(
    book_id: int, user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    book = await db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    active_borrow_stmt = select(models.Borrow).where(
        models.Borrow.book_id == book_id,
        models.Borrow.returned_at.is_(None),
    )
    existing = (await db.execute(active_borrow_stmt)).scalar_one_or_none()
    if existing:
        if existing.user_id == user.id:
            raise HTTPException(status_code=400, detail="Book is already borrowed by user")

        borrower = await db.get(models.User, existing.user_id)
        borrower_name = borrower.full_name if borrower and borrower.full_name else (borrower.email if borrower else "another user")
        raise HTTPException(status_code=400, detail=f"Book is currently borrowed by {borrower_name}")

    borrow = models.Borrow(user_id=user.id, book_id=book_id)
    db.add(borrow)
    await db.commit()
    await db.refresh(borrow)
    return {"message": "borrowed"}


@router.post("/{book_id}/return")
async def return_book(
    book_id: int, user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    stmt = select(models.Borrow).where(
        models.Borrow.book_id == book_id,
        models.Borrow.user_id == user.id,
        models.Borrow.returned_at.is_(None),
    )
    result = await db.execute(stmt)
    borrow = result.scalar_one_or_none()
    if not borrow:
        raise HTTPException(status_code=400, detail="No active borrow record")
    borrow.returned_at = func.now()
    await db.commit()
    return {"message": "returned"}


@router.post("/{book_id}/reviews", response_model=review_schemas.ReviewRead)
async def create_review(
    book_id: int,
    review_in: review_schemas.ReviewCreate,
    background_tasks: BackgroundTasks,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    book = await db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    stmt = select(models.Borrow).where(
        models.Borrow.book_id == book_id,
        models.Borrow.user_id == user.id,
    )
    res = await db.execute(stmt)
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Must borrow book before reviewing")
    review = models.Review(
        user_id=user.id, book_id=book_id, rating=review_in.rating, comment=review_in.comment
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    text = review_in.comment or ""
    asyncio.create_task(analyze_review(review.id, text))
    asyncio.create_task(update_book_consensus(book_id))
    return review


@router.get("/{book_id}/analysis")
async def book_analysis(book_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Review).where(models.Review.book_id == book_id)
    res = await db.execute(stmt)
    reviews = res.scalars().all()
    scores = [r.sentiment_score for r in reviews if r.sentiment_score is not None]
    avg = sum(scores) / len(scores) if scores else None
    return {"average_sentiment": avg, "review_count": len(reviews)}


@router.post("/{book_id}/summary/refresh")
async def refresh_summary(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    book = await db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    file_path = Path(book.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Book file not found")

    ext = file_path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type for summarization")

    file_bytes = file_path.read_bytes()
    text = _extract_text(file_bytes, ext)
    await generate_summary(book.id, text)

    await db.refresh(book)
    return {
        "book_id": book.id,
        "summary_status": _summary_status(book.summary),
        "summary": book.summary,
    }


@router.get("/{book_id}/download")
async def download_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
):
    book = await db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    file_path = Path(book.file_path)
    file_name = file_path.name.split("_", 1)[1] if "_" in file_path.name else file_path.name
    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "text/plain"

    signed_url = await storage.get_download_url(
        book.file_path,
        disposition="attachment",
        content_type=media_type,
    )
    if signed_url:
        return RedirectResponse(url=signed_url, status_code=307)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Book file not found")

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/{book_id}/view")
async def view_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
):
    book = await db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    file_path = Path(book.file_path)
    file_name = file_path.name.split("_", 1)[1] if "_" in file_path.name else file_path.name
    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "text/plain"

    signed_url = await storage.get_download_url(
        book.file_path,
        disposition="inline",
        content_type=media_type,
    )
    if signed_url:
        return RedirectResponse(url=signed_url, status_code=307)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Book file not found")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{file_name}"'},
    )


from app.services.recommendation import get_recommendations_for_user


@router.get("/recommendations")
async def recommendations(
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await get_recommendations_for_user(db, user)
    return {"items": items}
