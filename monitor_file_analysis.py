#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 File Analysis Monitor
실시간으로 파일 업로드 및 분석 상태를 모니터링
"""

import requests
import time
import json
from datetime import datetime

class AnalysisMonitor:
    def __init__(self, base_url="http://localhost:8006/api/v1"):
        self.base_url = base_url
        self.active_jobs = {}
    
    def check_health(self):
        """시스템 상태 확인"""
        try:
            response = requests.get(f"{self.base_url.replace('/api/v1', '')}/health")
            if response.status_code == 200:
                print("[OK] 시스템 정상 작동 중")
                return True
            else:
                print(f"[ERROR] 시스템 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] 서버 연결 실패: {e}")
            return False
    
    def monitor_jobs(self):
        """진행 중인 작업 모니터링"""
        try:
            # 활성 작업 조회
            response = requests.get(f"{self.base_url}/analysis/jobs")
            if response.status_code == 200:
                jobs = response.json()
                
                # 진행 중인 작업 필터링
                active_jobs = [j for j in jobs if j.get('status') in ['pending', 'processing']]
                completed_jobs = [j for j in jobs if j.get('status') == 'completed']
                failed_jobs = [j for j in jobs if j.get('status') == 'failed']
                
                # 상태 출력
                print(f"\n[STATUS] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  - 진행 중: {len(active_jobs)}개")
                print(f"  - 완료됨: {len(completed_jobs)}개")
                print(f"  - 실패함: {len(failed_jobs)}개")
                
                # 진행 중인 작업 상세 정보
                for job in active_jobs:
                    job_id = job.get('id')
                    if job_id:
                        self.check_job_detail(job_id)
                
                # 최근 완료된 작업
                if completed_jobs:
                    recent = completed_jobs[-1]
                    print(f"\n[최근 완료] Job ID: {recent.get('id')}")
                    print(f"  - 파일: {recent.get('filename', 'Unknown')}")
                    print(f"  - 레코드: {recent.get('total_records', 0)}개")
                    
                    # 결과 확인
                    self.check_results(recent.get('id'))
                
                # 실패한 작업
                if failed_jobs:
                    for job in failed_jobs[-3:]:  # 최근 3개만
                        print(f"\n[실패] Job ID: {job.get('id')}")
                        print(f"  - 오류: {job.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"[ERROR] 작업 모니터링 실패: {e}")
    
    def check_job_detail(self, job_id):
        """특정 작업 상세 정보 확인"""
        try:
            response = requests.get(f"{self.base_url}/analysis/status/{job_id}")
            if response.status_code == 200:
                status = response.json()
                print(f"\n[진행 중] Job ID: {job_id}")
                print(f"  - 상태: {status.get('status')}")
                print(f"  - 진행률: {status.get('progress', 0)}%")
                print(f"  - 파일: {status.get('filename', 'Unknown')}")
                print(f"  - 레코드: {status.get('total_records', 0)}개")
        except Exception as e:
            print(f"[ERROR] 작업 상세 조회 실패: {e}")
    
    def check_results(self, job_id):
        """분석 결과 확인"""
        try:
            response = requests.get(f"{self.base_url}/analysis/check-results/{job_id}")
            if response.status_code == 200:
                result = response.json()
                if result.get('available'):
                    print(f"  - 결과 파일 준비됨")
                    print(f"  - 다운로드 가능: Excel={result.get('formats', {}).get('excel')}, "
                          f"CSV={result.get('formats', {}).get('csv')}, "
                          f"JSON={result.get('formats', {}).get('json')}")
                    print(f"  - 분석된 레코드: {result.get('record_count', 0)}개")
        except Exception as e:
            print(f"[ERROR] 결과 확인 실패: {e}")
    
    def run(self, interval=5):
        """모니터링 실행"""
        print("=" * 60)
        print("AIRISS v4.0 분석 모니터")
        print("종료하려면 Ctrl+C를 누르세요")
        print("=" * 60)
        
        # 초기 상태 확인
        if not self.check_health():
            print("[ERROR] 서버가 실행 중이지 않습니다!")
            return
        
        try:
            while True:
                self.monitor_jobs()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[INFO] 모니터링 종료")

if __name__ == "__main__":
    monitor = AnalysisMonitor()
    monitor.run(interval=3)  # 3초마다 확인