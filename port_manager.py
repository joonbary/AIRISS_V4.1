#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIRISS v4.1 포트 관리 유틸리티
사용 가능한 포트를 찾고 AIRISS를 실행하는 도구
"""

import socket
import subprocess
import sys
import os
import time
from typing import List, Optional

def check_port_available(port: int) -> bool:
    """포트 사용 가능 여부 확인"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # 연결 실패 = 포트 사용 가능
    except Exception:
        return False

def find_available_ports(start_port: int = 8002, count: int = 10) -> List[int]:
    """사용 가능한 포트 목록 찾기"""
    available_ports = []
    for port in range(start_port, start_port + count):
        if check_port_available(port):
            available_ports.append(port)
    return available_ports

def kill_process_on_port(port: int) -> bool:
    """특정 포트를 사용하는 프로세스 종료 (Windows)"""
    try:
        # netstat으로 포트 사용 프로세스 찾기
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        lines = result.stdout.split('\n')
        pids_to_kill = []
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        # 프로세스 종료
        killed = False
        for pid in pids_to_kill:
            try:
                subprocess.run(['taskkill', '/PID', pid, '/F'], 
                             capture_output=True, check=True)
                print(f"✅ 프로세스 PID {pid} 종료 성공")
                killed = True
            except subprocess.CalledProcessError:
                print(f"❌ 프로세스 PID {pid} 종료 실패")
        
        return killed
        
    except Exception as e:
        print(f"❌ 프로세스 종료 중 오류: {e}")
        return False

def run_airiss_on_port(port: int) -> None:
    """지정된 포트에서 AIRISS 실행"""
    print(f"\n🚀 AIRISS v4.1을 포트 {port}에서 시작합니다...")
    print(f"🌐 접속 주소: http://localhost:{port}")
    print(f"🛑 서버 중지: Ctrl+C")
    print("-" * 50)
    
    # 환경변수 설정
    env = os.environ.copy()
    env['SERVER_PORT'] = str(port)
    
    try:
        # AIRISS 실행
        subprocess.run([sys.executable, '-m', 'app.main'], env=env)
    except KeyboardInterrupt:
        print(f"\n🛑 포트 {port}에서 AIRISS 서버 중지됨")
    except Exception as e:
        print(f"\n❌ AIRISS 실행 오류: {e}")

def main():
    """메인 함수"""
    print("🎯 AIRISS v4.1 포트 관리 유틸리티")
    print("=" * 50)
    
    # 기본 포트 8002 확인
    default_port = 8002
    print(f"\n📍 기본 포트 {default_port} 상태 확인...")
    
    if check_port_available(default_port):
        print(f"✅ 포트 {default_port} 사용 가능!")
        
        # 바로 실행할지 묻기
        response = input(f"\n포트 {default_port}에서 AIRISS를 시작하시겠습니까? (Y/n): ")
        if response.lower() != 'n':
            run_airiss_on_port(default_port)
            return
    else:
        print(f"❌ 포트 {default_port} 사용 중")
        
        # 프로세스 종료할지 묻기
        response = input(f"\n포트 {default_port}를 사용하는 프로세스를 종료하시겠습니까? (y/N): ")
        if response.lower() == 'y':
            if kill_process_on_port(default_port):
                print(f"\n⏳ 잠시 대기 중...")
                time.sleep(3)
                
                if check_port_available(default_port):
                    print(f"✅ 포트 {default_port} 해제 성공!")
                    run_airiss_on_port(default_port)
                    return
                else:
                    print(f"❌ 포트 {default_port} 여전히 사용 중")
    
    # 대체 포트 찾기
    print(f"\n🔍 대체 포트 검색 중...")
    available_ports = find_available_ports(8003, 10)
    
    if not available_ports:
        print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
        print("💡 수동으로 다른 포트 범위를 시도하거나 시스템을 재시작해보세요.")
        return
    
    print(f"✅ 사용 가능한 포트: {available_ports[:5]}")
    
    # 첫 번째 사용 가능한 포트로 실행
    selected_port = available_ports[0]
    print(f"\n🎯 포트 {selected_port}를 선택합니다.")
    
    response = input(f"포트 {selected_port}에서 AIRISS를 시작하시겠습니까? (Y/n): ")
    if response.lower() != 'n':
        run_airiss_on_port(selected_port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        print("💡 관리자 권한으로 실행해보거나 네트워크 설정을 확인하세요.")
