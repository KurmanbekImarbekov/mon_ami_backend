from fastapi import APIRouter, HTTPException, Depends
import bcrypt

from database.database import SessionLocal
from models.user import User
from schemas.user import UserCreate, UserLogin
from auth import create_access_token, get_current_user, require_role

router = APIRouter()


@router.post("/users")
def create_user(user_data: UserCreate):

    db = SessionLocal()

    password_hash = bcrypt.hashpw(
        user_data.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        username=user_data.username, password_hash=password_hash, role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.close()

    return {"id": user.id, "username": user.username, "role": user.role}


@router.post("/login")
def login(user_data: UserLogin):

    db = SessionLocal()

    user = db.query(User).filter(User.username == user_data.username).first()

    if user is None:

        db.close()

        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    password_correct = bcrypt.checkpw(
        user_data.password.encode("utf-8"), user.password_hash.encode("utf-8")
    )

    if not password_correct:

        db.close()

        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token(user.id, user.username, user.role)

    db.close()

    return {
        "message": "Вход выполнен",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "role": user.role},
    }


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):

    return {"message": "Ты авторизован", "user": current_user}


@router.get("/admin-test")
def admin_test(current_user=Depends(require_role("admin"))):

    return {"message": "Ты администратор", "user": current_user}


@router.get("/courier-test")
def courier_test(current_user=Depends(require_role("courier"))):

    return {"message": "Ты курьер", "user": current_user}


@router.get("/couriers")
@router.get("/couriers")
def get_couriers(current_user=Depends(require_role("admin"))):
    db = SessionLocal()

    couriers = db.query(User).filter(User.role == "courier").all()

    db.close()

    return [{"id": courier.id, "username": courier.username} for courier in couriers]


@router.get("/users")
def get_users(current_user=Depends(require_role("admin"))):
    db = SessionLocal()

    users = db.query(User).all()

    result = []

    for user in users:
        result.append({"id": user.id, "username": user.username, "role": user.role})

    db.close()

    return result


@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user=Depends(require_role("admin"))):
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.delete(user)
    db.commit()
    db.close()

    return {"message": "Пользователь удалён", "user_id": user_id}
