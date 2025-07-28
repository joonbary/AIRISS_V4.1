import bcrypt
from app.core.db.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == "test@test.com").first()
print(user)
print(user.password_hash)
print(bcrypt.checkpw("test123".encode(), user.password_hash.encode()))
db.close()