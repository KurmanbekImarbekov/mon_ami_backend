from fastapi import APIRouter
from database.database import SessionLocal
from models.order_item import OrderItem
from schemas.order_item import OrderItemCreate

router = APIRouter()


@router.post("/order-items")
def create_order_item(item_data: OrderItemCreate):
    db = SessionLocal()

    item = OrderItem(
        order_id=item_data.order_id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
        price=item_data.price
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    db.close()

    return item