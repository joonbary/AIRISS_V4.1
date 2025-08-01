#!/usr/bin/env python
"""
최적화된 서버 시작 스크립트
메모리와 타임아웃 설정 증가
"""
import os
import sys

# PORT 환경 변수 처리
port = os.environ.get('PORT', '8006')
try:
    port = int(port)
except ValueError:
    port = 8006

# 서버 시작 (워커 수 증가, 타임아웃 연장)
os.system(f'uvicorn app.main:app --host 0.0.0.0 --port {port} --workers 1 --timeout-keep-alive 300 --limit-max-requests 1000')