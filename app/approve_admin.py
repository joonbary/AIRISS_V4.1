import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db.database import SessionLocal
from app.models.user import User

def approve_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@test.com").first()
        if user:
            user.is_approved = True
            db.commit()
            print(f"✅ {user.email} 계정이 승인되었습니다!")
        else:
            print("❌ admin@test.com 계정을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    approve_admin()