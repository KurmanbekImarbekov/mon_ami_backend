from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import engine, Base
from routes.ai import router as ai_router
from models.user import User
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from routes.users import router as users_router

from routes.products import router
from routes.orders import router as orders_router
from routes.order_items import router as order_items_router


Base.metadata.create_all(bind=engine)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(orders_router)
app.include_router(order_items_router)
app.include_router(users_router)
app.include_router(ai_router)

@app.get("/")
def home():
    return {"message": "Mon Ami Backend работает!"}