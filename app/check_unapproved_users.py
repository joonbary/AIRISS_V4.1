import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db.database import SessionLocal
from app.models.user import User

def check_unapproved_users():
    db = SessionLocal()
    try:
        # 모든 사용자 확인
        all_users = db.query(User).all()
        print(f"\n전체 사용자 수: {len(all_users)}")
        
        # 미승인 사용자 확인
        unapproved = db.query(User).filter(User.is_approved == False).all()
        print(f"미승인 사용자 수: {len(unapproved)}")
        
        if unapproved:
            print("\n미승인 사용자 목록:")
            for user in unapproved:
                print(f"  - {user.email} ({user.name})")
                print(f"    가입일: {user.created_at}")
        else:
            print("\n미승인 사용자가 없습니다.")
        
        # 최근 가입한 사용자 확인
        print("\n최근 가입한 사용자 (상위 5명):")
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        for user in recent_users:
            print(f"  - {user.email} | 승인: {user.is_approved} | 관리자: {user.is_admin}")
        
    except Exception as e:
        print(f"오류: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_unapproved_users() 