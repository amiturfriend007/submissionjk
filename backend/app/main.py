from fastapi import FastAPI
from app.api.routes import auth, books

app = FastAPI(title="LuminaLib API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(books.router, prefix="/books", tags=["books"])