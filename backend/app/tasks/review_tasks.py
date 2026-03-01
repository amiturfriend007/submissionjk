import re
from collections import Counter

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal
from app.db import models
from app.services.llm import get_llm

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "this",
    "from",
    "have",
    "were",
    "been",
    "into",
    "about",
    "would",
    "could",
    "their",
    "there",
    "they",
    "them",
    "book",
    "story",
    "very",
    "really",
}


async def update_book_consensus(book_id: int):
    async with AsyncSessionLocal() as db:
        q = await db.execute(select(models.Review).where(models.Review.book_id == book_id))
        reviews = q.scalars().all()
        if not reviews:
            return

        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        scored = [r.sentiment_score for r in reviews if r.sentiment_score is not None]
        avg_sentiment = sum(scored) / len(scored) if scored else 0.0
        comments = [r.comment.strip() for r in reviews if r.comment and r.comment.strip()]
        llm_consensus = await _build_llm_consensus(comments)

        consensus_block = (
            "Consensus Summary:\n"
            f"- Reviews analyzed: {len(reviews)}\n"
            f"- Average rating: {avg_rating:.2f}/5\n"
            f"- Average sentiment: {avg_sentiment:.2f}\n"
            f"- User feedback: {llm_consensus}"
        )
        book = await db.get(models.Book, book_id)
        if book:
            base_description = (book.description or "").split("\n\nConsensus Summary:\n", 1)[0].strip()
            if base_description:
                book.description = f"{base_description}\n\n{consensus_block}"
            else:
                book.description = consensus_block
            await db.commit()
            await db.refresh(book)

        await _refresh_user_preferences(db, book_id)


async def _build_llm_consensus(comments: list[str]) -> str:
    if not comments:
        return "Not enough comments yet."
    llm = get_llm()
    joined = "\n".join(f"- {c}" for c in comments[:20])
    prompt = (
        "Create a 2-3 sentence rolling consensus of reader feedback from these comments. "
        "Focus on recurring likes/dislikes and tone.\n\n"
        f"{joined}"
    )
    try:
        return (await llm.summarize(prompt)).strip()
    except Exception:
        return "Consensus generation unavailable right now."


def _extract_keywords(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z]{4,}", (text or "").lower())
    return [w for w in words if w not in STOPWORDS]


async def _refresh_user_preferences(db, book_id: int) -> None:
    # Recompute lightweight preference profiles from user review history.
    rev_stmt = (
        select(models.Review.user_id, models.Review.rating, models.Review.comment, models.Book.author)
        .join(models.Book, models.Book.id == models.Review.book_id)
    )
    rows = (await db.execute(rev_stmt)).all()
    by_user: dict[int, list[tuple[int, str | None, str | None]]] = {}
    for user_id, rating, comment, author in rows:
        by_user.setdefault(user_id, []).append((rating, comment, author))

    for user_id, entries in by_user.items():
        liked_authors = [author for rating, _, author in entries if rating >= 4 and author]
        keyword_counter = Counter()
        for rating, comment, _ in entries:
            if rating >= 4 and comment:
                keyword_counter.update(_extract_keywords(comment))

        await db.execute(delete(models.UserPreference).where(models.UserPreference.user_id == user_id))

        if liked_authors:
            top_authors = ",".join([a for a, _ in Counter(liked_authors).most_common(5)])
            db.add(models.UserPreference(user_id=user_id, key="liked_authors", value=top_authors))

        if keyword_counter:
            top_keywords = ",".join([k for k, _ in keyword_counter.most_common(10)])
            db.add(models.UserPreference(user_id=user_id, key="liked_keywords", value=top_keywords))

    await db.commit()
