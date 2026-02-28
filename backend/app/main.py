from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, books
from app.db.session import engine
from app.db.base import Base

app = FastAPI(title="LuminaLib API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],  # Allow frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(books.router, prefix="/books", tags=["books"])


@app.on_event("startup")
async def on_startup():
    # ensure database tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)