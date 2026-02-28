from typing import Optional
from pydantic import BaseModel, conint


class ReviewCreate(BaseModel):
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None


class ReviewRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    comment: Optional[str]
    sentiment_score: Optional[float]

    class Config:
        orm_mode = True
