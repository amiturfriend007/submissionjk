from app.services.llm import get_llm
from app.db.session import AsyncSession, get_db
from app.db import models


async def generate_summary(book_id: int, text: str, db: AsyncSession):
    llm = get_llm()
    summary = await llm.summarize(text)
    book = await db.get(models.Book, book_id)
    if book:
        book.summary = summary
        await db.commit()
        await db.refresh(book)


async def analyze_review(review_id: int, text: str, db: AsyncSession):
    llm = get_llm()
    result = await llm.analyze_sentiment(text)
    review = await db.get(models.Review, review_id)
    if review:
        review.sentiment_score = result.get("score")
        await db.commit()
        await db.refresh(review)