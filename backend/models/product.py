from sqlalchemy import Column, Integer, String, Float, Date
from configs.database import Base

class ProductDB(Base):
    __tablename__ = "products"


    id = Column(Integer, primary_key=True, index=True)
    product_sku = Column(String, index=True)
    product_name = Column(String, index=True)
    category = Column(String, index=True)
    purchase_date = Column(Date)
    unit_price = Column(Float)
    quantity = Column(Integer)
