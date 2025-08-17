from fastapi import APIRouter, UploadFile, File, HTTPException
from services.product_service import process_excel

router = APIRouter()

@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        products = await process_excel(file)
        return products
    except HTTPException as e:
        raise e
