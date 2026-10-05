from fastapi import APIRouter
from database.database import SessionLocal
from models.product import Product
from schemas.product import ProductCreate

router = APIRouter()


@router.get("/products")
def get_products():
    db = SessionLocal()

    products = db.query(Product).all()

    db.close()

    return products


@router.post("/products")
@router.post("/products")
def create_product(product_data: ProductCreate):
    db = SessionLocal()

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    db.close()

    return product