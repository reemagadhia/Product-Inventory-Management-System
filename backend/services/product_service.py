import pandas as pd
from io import BytesIO
from fastapi import HTTPException
from datetime import date
from models.product import Product
from typing import List

REQUIRED_COLUMNS = [
    "Product SKU",
    "Product Name",
    "Category",
    "Purchase Date",
    "Unit Price",
    "Quantity",
]

async def process_excel(file) -> List[Product]:
    filename = (file.filename or "").lower()
    if not (filename.endswith(".xlsx") or filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx or .xls files are supported")

    content = await file.read()
    try:
        df = pd.read_excel(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel: {e}")

    # Check required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    # Parse purchase date & calculate stock age
    df["Purchase Date"] = pd.to_datetime(df["Purchase Date"])
    today = pd.Timestamp.today().normalize()
    df["Stock Age (Days)"] = (today - df["Purchase Date"]).dt.days

    # Check for duplicates
    duplicates = df[df.duplicated(subset=["Product SKU", "Purchase Date"], keep=False)]
    if not duplicates.empty:
        duplicate_rows = [
            {k: (v.isoformat() if isinstance(v, date) else v) for k, v in row.items()}
            for row in duplicates.to_dict(orient="records")
        ]
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Duplicate rows found based on Product SKU + Purchase Date",
                "duplicates": duplicate_rows,
            },
        )

    # Map to Product model
    data = df.to_dict(orient="records")
    products: List[Product] = [Product(**row) for row in data]
    return products
