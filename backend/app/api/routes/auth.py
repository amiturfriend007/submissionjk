from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session import get_db
from app.core import security
from app.schemas import user as user_schemas
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.post("/signup", response_model=user_schemas.UserRead)
async def signup(user_in: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    email = user_in.email.lower().strip()

    # check existing user
    q = await db.execute(
        select(models.User).where(func.lower(models.User.email) == email)
    )
    existing = q.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = security.get_password_hash(user_in.password)
    user = models.User(
        email=email, hashed_password=hashed, full_name=user_in.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login")
async def login(
    login_in: user_schemas.UserLogin,
    db: AsyncSession = Depends(get_db),
):
    email = login_in.email.lower().strip()

    result = await db.execute(
        select(models.User).where(func.lower(models.User.email) == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not security.verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = security.create_access_token(
        data={"sub": str(user.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/me", response_model=user_schemas.UserRead)
async def read_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=user_schemas.UserRead)
async def update_profile(
    user_in: user_schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user_in.full_name:
        current_user.full_name = user_in.full_name
    if user_in.password:
        current_user.hashed_password = security.get_password_hash(user_in.password)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/logout")
def logout():
    # JWT is stateless; client should simply discard token.
    return {"message": "logged out"}
