from app.db.session import AsyncSession
from app.db import models


async def update_book_consensus(book_id: int, db: AsyncSession):
    # simple average rating
    q = await db.execute(
        models.Review.__table__.select().where(models.Review.book_id == book_id)
    )
    reviews = q.scalars().all()
    if not reviews:
        return
    avg = sum([r.rating for r in reviews]) / len(reviews)
    book = await db.get(models.Book, book_id)
    if book:
        book.description = (book.description or "") + f"\n\nAverage rating: {avg:.2f}"
        await db.commit()
        await db.refresh(book)