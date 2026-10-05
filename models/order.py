from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    phone = Column(String)
    address = Column(String)
    total_price = Column(Float)
    status = Column(String, default="new")
    courier_id = Column(Integer, nullable=True)