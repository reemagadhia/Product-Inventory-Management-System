from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List
from configs.database import get_db
from models.schemas import Product
from services.product_service import process_excel, get_all_products

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    count = process_excel(content, db)
    return {"message": f"Uploaded {count} products successfully"}

@router.get("/", response_model=List[Product])
def fetch_products(db: Session = Depends(get_db)):
    return get_all_products(db)
