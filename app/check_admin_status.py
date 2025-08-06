import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db.database import SessionLocal
from app.models.user import User

def check_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@test.com").first()
        if user:
            print(f"Email: {user.email}")
            print(f"Is Approved: {user.is_approved}")
            print(f"Is Admin: {user.is_admin}")
        else:
            print("❌ admin@test.com 계정을 찾을 수 없습니다.")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()