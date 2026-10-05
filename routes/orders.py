from fastapi import APIRouter, HTTPException, Depends
import requests

from database.database import SessionLocal
from models.order import Order
from models.order_item import OrderItem

from schemas.order import OrderCreate, StatusUpdate

from auth import require_role


router = APIRouter()


TELEGRAM_WORKER_URL = (
    "https://monami-telegram.cmolohov46.workers.dev/"
)


ALLOWED_STATUS_TRANSITIONS = {
    "new": ["accepted"],
    "accepted": ["preparing"],
    "preparing": ["delivering"],
    "delivering": ["delivered"],
    "delivered": []
}


# =========================
# TELEGRAM
# =========================

def send_status_to_telegram(order, status):

    try:

        requests.post(
            TELEGRAM_WORKER_URL,
            json={
                "action": "status_update",
                "order_id": order.id,
                "status": status,
                "customer_name": order.customer_name,
                "phone": order.phone,
                "address": order.address,
                "total_price": order.total_price
            },
            timeout=5
        )

    except Exception as error:

        print(
            "Ошибка отправки Telegram:",
            error
        )


# =========================
# СОЗДАНИЕ ЗАКАЗА
# =========================

@router.post("/orders")
def create_order(order_data: OrderCreate):

    db = SessionLocal()

    order = Order(
        customer_name=order_data.customer_name,
        phone=order_data.phone,
        address=order_data.address,
        total_price=order_data.total_price,
        status="new"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for item in order_data.items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )

        db.add(order_item)

    db.commit()
    db.refresh(order)

    db.close()

    return order


# =========================
# ПОЛУЧИТЬ ВСЕ ЗАКАЗЫ
# =========================

@router.get("/orders")
def get_orders(
    current_user=Depends(require_role("admin"))
):

    db = SessionLocal()

    orders = db.query(Order).all()

    db.close()

    return orders


# =========================
# ИЗМЕНИТЬ СТАТУС АДМИНОМ
# =========================

@router.patch("/orders/{order_id}")
def update_order_status(
    order_id: int,
    status_data: StatusUpdate,
    current_user=Depends(require_role("admin"))
):

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order is None:

        db.close()

        raise HTTPException(
            status_code=404,
            detail="Заказ не найден"
        )

    new_status = status_data.status

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
        order.status,
        []
    )

    if new_status not in allowed_statuses:

        db.close()

        raise HTTPException(
            status_code=400,
            detail="Нельзя изменить статус с "
            + order.status
            + " на "
            + new_status
        )

    order.status = new_status

    db.commit()
    db.refresh(order)

    send_status_to_telegram(
        order,
        new_status
    )

    db.close()

    return order


# =========================
# ПОЛУЧИТЬ ОДИН ЗАКАЗ
# =========================

@router.get("/orders/{order_id}")
def get_order(order_id: int):

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order is None:

        db.close()

        raise HTTPException(
            status_code=404,
            detail="Заказ не найден"
        )

    db.close()

    return order


# =========================
# НАЗНАЧИТЬ КУРЬЕРА
# =========================

@router.patch("/orders/{order_id}/assign")
def assign_courier(
    order_id: int,
    courier_id: int,
    current_user=Depends(require_role("admin"))
):

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order is None:

        db.close()

        raise HTTPException(
            status_code=404,
            detail="Заказ не найден"
        )

    order.courier_id = courier_id

    db.commit()
    db.refresh(order)

    db.close()

    return {
        "message": "Курьер назначен",
        "order_id": order.id,
        "courier_id": order.courier_id
    }


# =========================
# ЗАКАЗЫ ТЕКУЩЕГО КУРЬЕРА
# =========================

@router.get("/courier/orders")
def get_courier_orders(
    current_user=Depends(require_role("courier"))
):

    db = SessionLocal()

    orders = db.query(Order).filter(
        Order.courier_id == current_user["user_id"]
    ).all()

    db.close()

    return orders


# =========================
# ИЗМЕНИТЬ СТАТУС КУРЬЕРОМ
# =========================

@router.patch("/courier/orders/{order_id}/status")
def courier_update_status(
    order_id: int,
    status_data: StatusUpdate,
    current_user=Depends(require_role("courier"))
):

    db = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if order is None:

        db.close()

        raise HTTPException(
            status_code=404,
            detail="Заказ не найден"
        )

    if order.courier_id != current_user["user_id"]:

        db.close()

        raise HTTPException(
            status_code=403,
            detail="Этот заказ назначен другому курьеру"
        )

    new_status = status_data.status

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
        order.status,
        []
    )

    if new_status not in allowed_statuses:

        db.close()

        raise HTTPException(
            status_code=400,
            detail="Нельзя изменить статус с "
            + order.status
            + " на "
            + new_status
        )

    order.status = new_status

    db.commit()
    db.refresh(order)

    send_status_to_telegram(
        order,
        new_status
    )

    db.close()

    return order