from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import product_api, health_api

app = FastAPI(title="Product Inventory API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(product_api.router, prefix="/products", tags=["products"])
app.include_router(health_api.router, prefix="/health", tags=["health"])


# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import List
# import pandas as pd
# from io import BytesIO
# from datetime import date

# app = FastAPI(title="Product Inventory API", version="1.0.0")

# # Allow CORS (optional)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["http://localhost:4200"],  # frontend origin
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # Excel columns we expect
# REQUIRED_COLUMNS = [
#     "Product SKU",
#     "Product Name",
#     "Category",
#     "Purchase Date",
#     "Unit Price",
#     "Quantity",
# ]

# # Product model
# class Product(BaseModel):
#     product_sku: str = Field(..., alias="Product SKU")
#     product_name: str = Field(..., alias="Product Name")
#     category: str = Field(..., alias="Category")
#     purchase_date: date = Field(..., alias="Purchase Date")
#     unit_price: float = Field(..., alias="Unit Price")
#     quantity: int = Field(..., alias="Quantity")
#     stock_age_days: int = Field(..., alias="Stock Age (Days)")

# @app.post("/upload-excel")
# async def upload_excel(file: UploadFile = File(...)):
#     filename = (file.filename or "").lower()
#     if not (filename.endswith(".xlsx") or filename.endswith(".xls")):
#         raise HTTPException(status_code=400, detail="Only .xlsx or .xls files are supported")

#     content = await file.read()
#     try:
#         df = pd.read_excel(BytesIO(content))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Failed to read Excel: {e}")

#     # Check required columns
#     missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
#     if missing:
#         raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")
    
#     df["Purchase Date"] = pd.to_datetime(df["Purchase Date"])
    
#     today = pd.Timestamp.today().normalize()
#     df["Stock Age (Days)"] = (today - df["Purchase Date"]).dt.days
    
#     duplicates = df[df.duplicated(subset=["Product SKU", "Purchase Date"], keep=False)]
#     if not duplicates.empty:
#         duplicate_rows =[
#             {k: (v.isoformat() if isinstance(v, date) else v) for k, v in row.items()}
#             for row in duplicates.to_dict(orient="records")
#         ]
#         raise HTTPException(
#             status_code=400,
#             detail={
#                 "error": "Duplicate rows found based on Product SKU + Purchase Date",
#                 "duplicates": duplicate_rows
#             }
#         )
        
#     # Map to List of Product objects
#     data = df.to_dict(orient="records")
#     products: List[Product] = [Product(**row) for row in data]
#     return products

# @app.get("/health")
# def health():
#     return {"status": "ok"}
