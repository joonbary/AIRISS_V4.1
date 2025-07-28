#!/usr/bin/env python3
"""
리팩터링된 코드를 기존 프로젝트에 통합하는 스크립트
"""

import os
import shutil
from pathlib import Path


def integrate_refactored_code():
    """리팩터링된 코드를 기존 프로젝트 구조에 통합"""
    
    print("[INTEGRATION] 리팩터링된 코드 통합 시작")
    
    # backend 폴더의 내용을 기존 app 폴더로 복사
    mappings = [
        # API v1 endpoints
        ("backend/app/api/v1/__init__.py", "app/api/v1/__init__.py"),
        ("backend/app/api/v1/auth.py", "app/api/v1/endpoints/auth.py"),
        ("backend/app/api/v1/analysis.py", "app/api/v1/endpoints/analysis_refactored.py"),
        ("backend/app/api/v1/files.py", "app/api/v1/endpoints/files.py"),
        ("backend/app/api/v1/users.py", "app/api/v1/endpoints/users.py"),
        ("backend/app/api/v1/websocket.py", "app/api/v1/endpoints/websocket.py"),
        
        # Schemas
        ("backend/app/schemas/__init__.py", "app/schemas/__init__.py"),
        ("backend/app/schemas/user.py", "app/schemas/user.py"),
        ("backend/app/schemas/file.py", "app/schemas/file.py"),
        ("backend/app/schemas/analysis.py", "app/schemas/analysis.py"),
        
        # Core
        ("backend/app/core/__init__.py", "app/core/__init__.py"),
        ("backend/app/core/config.py", "app/core/config_refactored.py"),
        ("backend/app/core/security.py", "app/core/security.py"),
        
        # Main app
        ("backend/app/main.py", "app/main_refactored.py"),
    ]
    
    for src, dst in mappings:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            # 대상 디렉토리 생성
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 복사
            shutil.copy2(src_path, dst_path)
            print(f"  [COPY] {src} -> {dst}")
    
    # requirements.txt 업데이트
    additional_requirements = """
# Additional requirements for refactored code
pydantic-settings>=2.0.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.5
"""
    
    req_path = Path("requirements.txt")
    if req_path.exists():
        current_reqs = req_path.read_text()
        if "pydantic-settings" not in current_reqs:
            with open(req_path, "a") as f:
                f.write(additional_requirements)
            print("  [UPDATE] requirements.txt 업데이트 완료")
    
    # .env.example 생성
    env_example = """# AIRISS v4 Environment Variables

# Project
PROJECT_NAME="AIRISS v4"
VERSION="4.0.0"

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=postgresql://user:password@localhost/airiss_v4
# Or use individual variables
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airiss_v4

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1

# AI Analysis
OPENAI_API_KEY=your-openai-api-key

# Admin User
FIRST_SUPERUSER=admin
FIRST_SUPERUSER_PASSWORD=admin123
FIRST_SUPERUSER_EMAIL=admin@airiss.com

# Logging
LOG_LEVEL=INFO
"""
    
    env_example_path = Path(".env.example")
    env_example_path.write_text(env_example)
    print("  [CREATE] .env.example 생성 완료")
    
    # 새로운 실행 스크립트 생성
    run_script = """#!/usr/bin/env python3
\"\"\"
Run AIRISS v4 Refactored Version
\"\"\"

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.main_refactored import app
    from app.core.config_refactored import settings
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
"""
    
    run_script_path = Path("run_refactored.py")
    run_script_path.write_text(run_script)
    print("  [CREATE] run_refactored.py 생성 완료")
    
    print("\n[COMPLETE] 리팩터링된 코드 통합 완료")
    print("\n[NEXT STEPS]:")
    print("1. pip install -r requirements.txt (새로운 의존성 설치)")
    print("2. cp .env.example .env (환경 설정 파일 생성)")
    print("3. python run_refactored.py (리팩터링된 버전 실행)")
    print("\n[NOTE] 기존 코드와 병행 실행 가능:")
    print("- 기존 버전: python app/main.py")
    print("- 리팩터링 버전: python run_refactored.py")


if __name__ == "__main__":
    integrate_refactored_code()