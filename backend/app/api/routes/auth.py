from fastapi import APIRouter

router = APIRouter()

@router.post("/signup")
def signup():
    return {"message": "signup stub"}

@router.post("/login")
def login():
    return {"access_token": "fake-jwt", "token_type": "bearer"}