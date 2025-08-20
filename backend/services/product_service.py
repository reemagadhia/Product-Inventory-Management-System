import pandas as pd
from io import BytesIO
from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.product import ProductDB

REQUIRED_COLUMNS = [
    "Product SKU",
    "Product Name",
    "Category",
    "Purchase Date",
    "Unit Price",
    "Quantity",
]

def process_excel(file_content: bytes, db: Session):
    try:
        df = pd.read_excel(BytesIO(file_content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel: {e}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    df["Purchase Date"] = pd.to_datetime(df["Purchase Date"])

    duplicates = df[df.duplicated(subset=["Product SKU", "Purchase Date"], keep=False)]
    if not duplicates.empty:
        duplicate_rows = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in duplicates.to_dict(orient="records")
        ]
        raise HTTPException(
            status_code=400,
            detail={"error": "Duplicate rows found in file!", "duplicates": duplicate_rows},
        )

    for _, row in df.iterrows():
        exists = db.query(ProductDB).filter(
            ProductDB.product_sku == row["Product SKU"],
            ProductDB.purchase_date == row["Purchase Date"].date()
        ).first()
        if exists:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate entry in DB for SKU {row['Product SKU']} on {row['Purchase Date'].date()}",
            )

        product = ProductDB(
            product_sku=row["Product SKU"],
            product_name=row["Product Name"],
            category=row["Category"],
            purchase_date=row["Purchase Date"].date(),
            unit_price=row["Unit Price"],
            quantity=row["Quantity"]
        )
        db.add(product)

    db.commit()
    return len(df)


def get_all_products(db: Session):
    products = db.query(ProductDB).all()
    today = date.today()

    result = [
        {
            "Product SKU": p.product_sku,
            "Product Name": p.product_name,
            "Category": p.category,
            "Purchase Date": p.purchase_date,
            "Unit Price": p.unit_price,
            "Quantity": p.quantity,
            "Stock Age (Days)": (today - p.purchase_date).days
        }
        for p in products
    ]
    return result
