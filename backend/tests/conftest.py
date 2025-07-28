"""
Test Configuration
pytest 설정 및 fixtures
"""

import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# 테스트 환경 설정
os.environ["ENVIRONMENT"] = "testing"

from app.main_final import app
from app.db import Base, get_db
from app.services import UserService


# 테스트용 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """테스트 DB 엔진"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, None, None]:
    """테스트 DB 세션"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db) -> TestClient:
    """테스트 클라이언트"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db) -> Dict[str, Any]:
    """테스트 사용자"""
    user_service = UserService(db)
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    user = user_service.create_user(user_data)
    return user


@pytest.fixture(scope="function")
def test_admin(db) -> Dict[str, Any]:
    """테스트 관리자"""
    user_service = UserService(db)
    admin_data = {
        "username": "testadmin",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Test Admin",
        "is_superuser": True
    }
    admin = user_service.create_user(admin_data)
    return admin


@pytest.fixture(scope="function")
def auth_headers(client, test_user) -> Dict[str, str]:
    """인증 헤더"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_headers(client, test_admin) -> Dict[str, str]:
    """관리자 인증 헤더"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testadmin",
            "password": "adminpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_file_data():
    """샘플 파일 데이터"""
    import pandas as pd
    import io
    
    # 샘플 DataFrame 생성
    df = pd.DataFrame({
        'employee_id': ['EMP001', 'EMP002', 'EMP003'],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'opinion': [
            'Excellent work performance and great team player',
            'Good technical skills but needs improvement in communication',
            'Average performance with room for growth'
        ],
        'performance_score': [85, 70, 60],
        'attendance_rate': [95, 90, 85]
    })
    
    # Excel 파일로 변환
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    
    return output