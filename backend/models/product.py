from pydantic import BaseModel, Field
from datetime import date

class Product(BaseModel):
    product_sku: str = Field(..., alias="Product SKU")
    product_name: str = Field(..., alias="Product Name")
    category: str = Field(..., alias="Category")
    purchase_date: date = Field(..., alias="Purchase Date")
    unit_price: float = Field(..., alias="Unit Price")
    quantity: int = Field(..., alias="Quantity")
    stock_age_days: int = Field(..., alias="Stock Age (Days)")
