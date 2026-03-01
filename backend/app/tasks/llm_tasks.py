import logging
import asyncio

from app.services.llm import get_llm
from app.db.session import AsyncSessionLocal
from app.db import models
from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_summary(book_id: int, text: str):
    summary = "__SUMMARY_FAILED__"
    try:
        llm = get_llm()
        max_chars = getattr(settings, "llm_max_input_chars", 12000)
        safe_text = (text or "")[: max_chars]
        summary = await llm.summarize(safe_text)
    except Exception:
        logger.exception("Summary generation task failed for book_id=%s", book_id)

    await _persist_summary_with_retry(book_id, summary)


async def analyze_review(review_id: int, text: str):
    score = 0.0
    try:
        llm = get_llm()
        max_chars = getattr(settings, "llm_max_input_chars", 12000)
        safe_text = (text or "")[: max_chars]
        result = await llm.analyze_sentiment(safe_text)
        score = result.get("score")
    except Exception:
        logger.exception("Review sentiment task failed for review_id=%s", review_id)

    await _persist_sentiment_with_retry(review_id, score)


async def _persist_summary_with_retry(book_id: int, summary: str, attempts: int = 5) -> None:
    for attempt in range(1, attempts + 1):
        async with AsyncSessionLocal() as db:
            try:
                book = await db.get(models.Book, book_id)
                if not book:
                    return
                book.summary = summary
                await db.commit()
                await db.refresh(book)
                return
            except Exception:
                logger.exception(
                    "Failed persisting summary for book_id=%s (attempt %s/%s)",
                    book_id,
                    attempt,
                    attempts,
                )
        await asyncio.sleep(0.5 * attempt)


async def _persist_sentiment_with_retry(review_id: int, score: float, attempts: int = 5) -> None:
    for attempt in range(1, attempts + 1):
        async with AsyncSessionLocal() as db:
            try:
                review = await db.get(models.Review, review_id)
                if not review:
                    return
                review.sentiment_score = score
                await db.commit()
                await db.refresh(review)
                return
            except Exception:
                logger.exception(
                    "Failed persisting sentiment for review_id=%s (attempt %s/%s)",
                    review_id,
                    attempt,
                    attempts,
                )
        await asyncio.sleep(0.5 * attempt)
