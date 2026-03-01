from collections import defaultdict
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import models


def _split_csv(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def _book_text(book: models.Book) -> str:
    return f"{book.title or ''} {book.author or ''} {book.description or ''} {book.summary or ''}".lower()


async def get_recommendations_for_user(db: AsyncSession, user: models.User) -> List[models.Book]:
    books = (await db.execute(select(models.Book))).scalars().all()
    if not books:
        return []

    pref_rows = (
        await db.execute(
            select(models.UserPreference.key, models.UserPreference.value).where(
                models.UserPreference.user_id == user.id
            )
        )
    ).all()
    pref_map = {k: v for k, v in pref_rows}
    liked_authors = _split_csv(pref_map.get("liked_authors"))
    liked_keywords = _split_csv(pref_map.get("liked_keywords"))

    reviewed_rows = (
        await db.execute(
            select(models.Review.book_id, models.Review.rating).where(models.Review.user_id == user.id)
        )
    ).all()
    already_seen = {book_id for book_id, _ in reviewed_rows}

    # Collaborative signal: users who liked the same books as current user.
    my_liked_book_ids = {book_id for book_id, rating in reviewed_rows if rating >= 4}
    similar_user_ids = set()
    if my_liked_book_ids:
        similar_rows = (
            await db.execute(
                select(models.Review.user_id)
                .where(models.Review.book_id.in_(my_liked_book_ids), models.Review.rating >= 4)
                .distinct()
            )
        ).all()
        similar_user_ids = {uid for (uid,) in similar_rows if uid != user.id}

    collaborative_scores = defaultdict(float)
    if similar_user_ids:
        collab_rows = (
            await db.execute(
                select(models.Review.book_id, models.Review.rating).where(
                    models.Review.user_id.in_(similar_user_ids), models.Review.rating >= 4
                )
            )
        ).all()
        for book_id, rating in collab_rows:
            collaborative_scores[book_id] += float(rating)

    scored = []
    for book in books:
        if book.id in already_seen:
            continue

        score = 0.0
        author_lower = (book.author or "").lower()
        if author_lower and author_lower in liked_authors:
            score += 3.0

        text = _book_text(book)
        if liked_keywords:
            keyword_hits = sum(1 for kw in liked_keywords if kw in text)
            score += min(3.0, keyword_hits * 0.5)

        score += min(4.0, collaborative_scores.get(book.id, 0.0) / 5.0)

        if score > 0:
            scored.append((score, book))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = [book for _, book in scored[:10]]
    if top:
        return top

    # Cold-start fallback
    return books[:10]
