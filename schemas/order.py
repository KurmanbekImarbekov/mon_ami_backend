from pydantic import BaseModel


class OrderItemData(BaseModel):
    product_id: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    address: str
    total_price: float
    items: list[OrderItemData]


class StatusUpdate(BaseModel):
    status: str