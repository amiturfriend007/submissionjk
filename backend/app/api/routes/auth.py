from datetime import timedelta
# from select import select
from sqlalchemy import select
from unittest import result
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session import get_db
from app.core import security
from app.schemas import user as user_schemas
from app.api.deps.auth import get_current_user

router = APIRouter()


@router.post("/signup", response_model=user_schemas.UserRead)
async def signup(user_in: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # check existing user
    q = await db.execute(
        models.User.__table__.select().where(models.User.email == user_in.email)
    )
    existing = q.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = security.get_password_hash(user_in.password)
    user = models.User(
        email=user_in.email, hashed_password=hashed, full_name=user_in.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# @router.post("/login")
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
# ):
#     # q = await db.execute(
#     #     models.User.__table__.select().where(models.User.email == form_data.username)
#     # )
#     # user = q.scalar_one_or_none()
#     result = await db.execute(
#     models.User.__table__
#     .select()
#     .where(models.User.email == form_data.username)
#     )
#     row = result.first()
#     user = models.User(**row._mapping) if row else None
#     if not user or not security.verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = security.create_access_token(data={"sub": user.id})
#     return {"access_token": access_token, "token_type": "bearer"}



@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    email = form_data.username.lower().strip()

    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        print("USER NOT FOUND")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not security.verify_password(form_data.password, user.hashed_password):
        print("PASSWORD MISMATCH")
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