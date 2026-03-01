from typing import Literal, Optional
from pydantic import BaseModel, Field


class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookReviewSnippet(BaseModel):
    reviewer: str
    rating: int
    comment: str


class BookRead(BookBase):
    id: int
    summary: Optional[str] = None
    summary_status: Literal["pending", "ready", "failed"] = "pending"
    current_borrower: Optional[str] = None
    recent_reviews: list[BookReviewSnippet] = Field(default_factory=list)

    class Config:
        orm_mode = True


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None


class BookList(BaseModel):
    items: list[BookRead]
    page: int
