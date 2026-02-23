from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def upload_book():
    return {"message": "book uploaded, async summary triggered"}

@router.get("/")
def list_books():
    return {"items": [], "page": 1}