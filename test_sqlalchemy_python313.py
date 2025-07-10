# -*- coding: utf-8 -*-
"""
SQLAlchemy Python 3.13 호환성 테스트
"""

import sys
from datetime import datetime

def test_sqlalchemy_compatibility():
    """SQLAlchemy Python 3.13 호환성 테스트"""
    print("🧪 SQLAlchemy Python 3.13 호환성 테스트")
    print("=" * 50)
    
    print(f"🐍 Python 버전: {sys.version}")
    print()
    
    # 1. SQLAlchemy 기본 import 테스트
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy 버전: {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"❌ SQLAlchemy import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ SQLAlchemy 로드 오류: {e}")
        return False
    
    # 2. 핵심 모듈 import 테스트
    try:
        from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker, Session
        print("✅ SQLAlchemy 핵심 모듈 import 성공")
    except Exception as e:
        print(f"❌ SQLAlchemy 모듈 import 실패: {e}")
        return False
    
    # 3. 메모리 DB 엔진 생성 테스트
    try:
        engine = create_engine('sqlite:///:memory:', echo=False)
        print("✅ SQLAlchemy 엔진 생성 성공")
    except Exception as e:
        print(f"❌ SQLAlchemy 엔진 생성 실패: {e}")
        return False
    
    # 4. 모델 정의 테스트
    try:
        Base = declarative_base()
        
        class TestModel(Base):
            __tablename__ = 'test_model'
            
            id = Column(Integer, primary_key=True)
            name = Column(String(100))
            created_at = Column(DateTime, default=datetime.utcnow)
            data = Column(Text)
        
        print("✅ SQLAlchemy 모델 정의 성공")
    except Exception as e:
        print(f"❌ SQLAlchemy 모델 정의 실패: {e}")
        return False
    
    # 5. 테이블 생성 테스트
    try:
        Base.metadata.create_all(engine)
        print("✅ SQLAlchemy 테이블 생성 성공")
    except Exception as e:
        print(f"❌ SQLAlchemy 테이블 생성 실패: {e}")
        return False
    
    # 6. 세션 생성 및 CRUD 테스트
    try:
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # 데이터 삽입
        test_record = TestModel(name="Test Record", data="Test Data")
        session.add(test_record)
        session.commit()
        
        # 데이터 조회
        result = session.query(TestModel).filter(TestModel.name == "Test Record").first()
        if result:
            print("✅ SQLAlchemy CRUD 작업 성공")
        else:
            print("❌ SQLAlchemy 데이터 조회 실패")
            return False
        
        session.close()
    except Exception as e:
        print(f"❌ SQLAlchemy CRUD 작업 실패: {e}")
        return False
    
    # 7. PostgreSQL 드라이버 테스트
    try:
        import psycopg2
        print("✅ PostgreSQL 드라이버(psycopg2) 사용 가능")
        
        # PostgreSQL 연결 문자열 테스트 (실제 연결은 안 함)
        postgres_engine = create_engine('postgresql://test:test@localhost/test', echo=False)
        print("✅ PostgreSQL 엔진 생성 가능")
        
    except ImportError:
        print("⚠️ psycopg2 설치 필요: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL 엔진 테스트 실패: {e}")
        return False
    
    return True

def main():
    """메인 실행"""
    print(f"⏰ 테스트 시작: {datetime.now()}")
    print()
    
    success = test_sqlalchemy_compatibility()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SQLAlchemy Python 3.13 호환성 테스트 성공!")
        print("✅ AIRISS에서 Neon DB 영구 저장 기능을 사용할 수 있습니다.")
        print()
        print("💡 다음 단계:")
        print("  1. 현재 AIRISS 서버 중지 (Ctrl+C)")
        print("  2. start_airiss_python313.bat 재실행")
        print("  3. 로그에서 '데이터베이스 활성화: True' 확인")
    else:
        print("❌ SQLAlchemy Python 3.13 호환성 문제 지속")
        print()
        print("🛠️ 추가 해결 방법:")
        print("  1. SQLAlchemy 1.4.x 버전으로 다운그레이드:")
        print("     pip install sqlalchemy==1.4.53")
        print("  2. Python 3.12 환경 생성:")
        print("     conda create -n airiss_312 python=3.12")
        print("  3. 코드 레벨 수정 (고급)")
    
    print(f"\n📅 테스트 완료: {datetime.now()}")
    return success

if __name__ == "__main__":
    main()
    input("\n아무 키나 눌러 종료...")
