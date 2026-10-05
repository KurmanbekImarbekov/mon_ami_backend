from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    price: float