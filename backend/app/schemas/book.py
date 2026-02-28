from typing import Optional
from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: int
    summary: Optional[str] = None

    class Config:
        orm_mode = True


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None


class BookList(BaseModel):
    items: list[BookRead]
    page: int
