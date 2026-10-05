from database.database import SessionLocal
from models.user import User

db = SessionLocal()

users = db.query(User).all()

for user in users:
    db.delete(user)

db.commit()
db.close()

print("Все пользователи удалены!")
