# AIRISS Railway 배포 문제 진단 스크립트
# Railway 배포 실패 원인을 단계별로 확인

import os
import sys
import subprocess
import json
from datetime import datetime

def print_separator(title):
    print("=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def check_railway_status():
    """Railway 프로젝트 상태 확인"""
    print_separator("Railway 프로젝트 상태 확인")
    
    try:
        # Railway CLI 설치 확인
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI 버전: {result.stdout.strip()}")
        else:
            print("❌ Railway CLI가 설치되지 않았습니다")
            print("설치 방법: npm install -g @railway/cli")
            return False
        
        # 프로젝트 연결 상태 확인
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway 프로젝트 연결됨")
            print(result.stdout)
        else:
            print("❌ Railway 프로젝트 연결 실패")
            print("연결 방법: railway link")
            return False
            
        return True
        
    except FileNotFoundError:
        print("❌ Railway CLI를 찾을 수 없습니다")
        print("설치 방법:")
        print("1. npm install -g @railway/cli")
        print("2. railway login")
        print("3. railway link (프로젝트 연결)")
        return False

def check_logs():
    """Railway 로그 확인"""
    print_separator("Railway 로그 확인")
    
    try:
        # 최근 로그 확인
        print("📋 최근 배포 로그:")
        result = subprocess.run(['railway', 'logs', '--json'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ 로그 가져오기 실패")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ 로그 가져오기 시간 초과")
    except Exception as e:
        print(f"❌ 로그 확인 중 오류: {e}")

def test_local_app():
    """로컬에서 앱 테스트"""
    print_separator("로컬 애플리케이션 테스트")
    
    # 현재 디렉토리 확인
    current_dir = os.getcwd()
    print(f"📁 현재 디렉토리: {current_dir}")
    
    # main.py 파일 존재 확인
    main_py_path = os.path.join(current_dir, "app", "main.py")
    if os.path.exists(main_py_path):
        print(f"✅ main.py 파일 존재: {main_py_path}")
    else:
        print(f"❌ main.py 파일 없음: {main_py_path}")
        return False
    
    # requirements.txt 확인
    req_path = os.path.join(current_dir, "requirements.txt")
    if os.path.exists(req_path):
        print(f"✅ requirements.txt 존재")
        with open(req_path, 'r') as f:
            lines = f.readlines()
            print(f"📦 의존성 개수: {len(lines)}")
    else:
        print(f"❌ requirements.txt 없음")
        return False
    
    # 로컬 테스트 실행
    print("\n🧪 로컬 FastAPI 앱 테스트 시작...")
    try:
        # FastAPI 앱 import 테스트
        sys.path.insert(0, current_dir)
        from app.main import app
        print("✅ FastAPI 앱 import 성공")
        
        # 포트 설정 확인
        port = os.environ.get('PORT', '8002')
        print(f"📡 설정된 포트: {port}")
        
        return True
        
    except ImportError as e:
        print(f"❌ FastAPI 앱 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 로컬 테스트 실패: {e}")
        return False

def check_docker_build():
    """Docker 빌드 테스트"""
    print_separator("Docker 빌드 테스트")
    
    dockerfile_path = "Dockerfile"
    if not os.path.exists(dockerfile_path):
        print("❌ Dockerfile이 없습니다")
        return False
    
    print("✅ Dockerfile 존재")
    
    # Docker 설치 확인
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker 설치됨: {result.stdout.strip()}")
        else:
            print("❌ Docker가 설치되지 않았습니다")
            return False
    except FileNotFoundError:
        print("❌ Docker를 찾을 수 없습니다")
        return False
    
    # 로컬 Docker 빌드 테스트 (시간이 오래 걸리므로 선택적)
    print("\n🔧 Docker 빌드 테스트를 실행하시겠습니까? (y/n): ", end="")
    response = input()
    
    if response.lower() == 'y':
        print("🔨 Docker 빌드 시작...")
        try:
            result = subprocess.run(
                ['docker', 'build', '-t', 'airiss-test', '.'],
                capture_output=True,
                text=True,
                timeout=300  # 5분 제한
            )
            
            if result.returncode == 0:
                print("✅ Docker 빌드 성공")
                return True
            else:
                print("❌ Docker 빌드 실패")
                print("ERROR OUTPUT:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Docker 빌드 시간 초과 (5분)")
            return False
        except Exception as e:
            print(f"❌ Docker 빌드 중 오류: {e}")
            return False
    
    return True

def generate_fix_suggestions():
    """문제 해결 제안 생성"""
    print_separator("문제 해결 제안")
    
    print("🔧 Railway 배포 문제 해결 방법:")
    print()
    
    print("1️⃣ **포트 설정 수정** (가장 가능성 높음)")
    print("   - main.py에서 PORT 환경변수 처리 개선")
    print("   - railway.json의 startCommand 수정")
    print()
    
    print("2️⃣ **의존성 문제 해결**")
    print("   - requirements.txt 최적화")
    print("   - 불필요한 패키지 제거")
    print()
    
    print("3️⃣ **헬스체크 강화**")
    print("   - /health 엔드포인트 응답 시간 개선")
    print("   - 더 간단한 헬스체크 구현")
    print()
    
    print("4️⃣ **로그 기반 디버깅**")
    print("   - Railway 배포 로그 상세 분석")
    print("   - 에러 메시지 기반 수정")
    print()
    
    print("5️⃣ **대안 플랫폼 고려**")
    print("   - Render.com 배포")
    print("   - Fly.io 배포")
    print("   - Vercel 배포")

def main():
    """메인 실행"""
    print("🚀 AIRISS Railway 배포 문제 진단 도구")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Railway 상태 확인
    railway_ok = check_railway_status()
    print()
    
    # 2. 로그 확인 (Railway 연결된 경우만)
    if railway_ok:
        check_logs()
        print()
    
    # 3. 로컬 앱 테스트
    local_ok = test_local_app()
    print()
    
    # 4. Docker 빌드 테스트
    docker_ok = check_docker_build()
    print()
    
    # 5. 문제 해결 제안
    generate_fix_suggestions()
    print()
    
    # 결과 요약
    print_separator("진단 결과 요약")
    print(f"Railway CLI: {'✅' if railway_ok else '❌'}")
    print(f"로컬 앱 테스트: {'✅' if local_ok else '❌'}")
    print(f"Docker 환경: {'✅' if docker_ok else '❌'}")
    print()
    
    if not local_ok:
        print("🚨 **우선순위**: 로컬 앱 문제부터 해결하세요")
    elif not railway_ok:
        print("🚨 **우선순위**: Railway CLI 설정부터 확인하세요")
    else:
        print("✅ **상태**: 기본 환경은 정상, Railway 배포 설정 확인 필요")

if __name__ == "__main__":
    main()
