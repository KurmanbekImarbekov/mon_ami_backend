import bcrypt

from database.database import SessionLocal
from models.user import User

db = SessionLocal()

admin = db.query(User).filter(User.username == "admin").first()

if admin is None:
    print("Пользователь admin не найден")
else:
    new_password = "admin123"

    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    admin.password_hash = password_hash

    db.commit()

    print("Пароль admin успешно изменён!")
    print("Логин: admin")
    print("Пароль: admin123")

db.close()
