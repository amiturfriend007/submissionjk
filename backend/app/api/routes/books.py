from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    BackgroundTasks,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import models
from app.db.session import get_db
from app.schemas import book as book_schemas, review as review_schemas
from app.api.deps.auth import get_current_user
from app.services.storage import get_storage, StorageBackend
from app.tasks.llm_tasks import generate_summary, analyze_review
from app.tasks.review_tasks import update_book_consensus

router = APIRouter()


@router.post("/", response_model=book_schemas.BookRead)
async def create_book(
    title: str,
    file: UploadFile = File(...),
    author: Optional[str] = None,
    description: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
):
    book = models.Book(title=title, author=author, description=description, file_path="")
    db.add(book)
    await db.commit()
    await db.refresh(book)

    path = await storage.save(file.file, file.filename)
    book.file_path = path
    await db.commit()
    await db.refresh(book)

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except Exception:
        text = ""
    background_tasks.add_task(generate_summary, book.id, text, db)
    return book


@router.get("/", response_model=book_schemas.BookList)
async def list_books(page: int = 1, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Book).offset((page - 1) * 10).limit(10)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return {"items": books, "page": page}


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
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
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
    background_tasks.add_task(analyze_review, review.id, text, db)
    background_tasks.add_task(update_book_consensus, book_id, db)
    return review


@router.get("/{book_id}/analysis")
async def book_analysis(book_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Review).where(models.Review.book_id == book_id)
    res = await db.execute(stmt)
    reviews = res.scalars().all()
    scores = [r.sentiment_score for r in reviews if r.sentiment_score is not None]
    avg = sum(scores) / len(scores) if scores else None
    return {"average_sentiment": avg, "review_count": len(reviews)}


from app.services.recommendation import get_recommendations_for_user


@router.get("/recommendations")
async def recommendations(user: models.User = Depends(get_current_user)):
    items = get_recommendations_for_user(user)
    return {"items": items}