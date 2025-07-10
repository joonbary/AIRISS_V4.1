#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIRISS v5.0 기능 테스트 스크립트
"""

import os
import sys
import asyncio
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, os.getcwd())

def test_v5_features():
    """v5 기능 테스트"""
    print("🧪 AIRISS v5.0 기능 테스트 시작")
    print("=" * 50)
    
    # 1. 기본 모듈 import 테스트
    print("\n1️⃣ 기본 모듈 테스트:")
    try:
        from app.main import app
        print("✅ FastAPI app 로드 성공")
    except Exception as e:
        print(f"❌ FastAPI app 로드 실패: {e}")
        return False
    
    # 2. 텍스트 분석기 테스트
    print("\n2️⃣ 텍스트 분석기 테스트:")
    try:
        from app.services.text_analyzer import AIRISSTextAnalyzer
        analyzer = AIRISSTextAnalyzer()
        test_text = "저는 열심히 일하고 있습니다. 좋은 성과를 내고 있습니다."
        result = analyzer.analyze_text(test_text, "업무성과")
        print(f"✅ 텍스트 분석 성공: {result}")
    except Exception as e:
        print(f"❌ 텍스트 분석 실패: {e}")
    
    # 3. 하이브리드 분석기 테스트
    print("\n3️⃣ 하이브리드 분석기 테스트:")
    try:
        from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
        hybrid = AIRISSHybridAnalyzer()
        print("✅ 하이브리드 분석기 로드 성공")
    except Exception as e:
        print(f"❌ 하이브리드 분석기 로드 실패: {e}")
    
    # 4. 편향 탐지 테스트
    print("\n4️⃣ 편향 탐지 기능 테스트:")
    try:
        from app.services.bias_detection.bias_detector import BiasDetector
        detector = BiasDetector()
        print("✅ 편향 탐지기 로드 성공")
    except Exception as e:
        print(f"❌ 편향 탐지기 로드 실패: {e}")
    
    # 5. 예측 분석 테스트
    print("\n5️⃣ 예측 분석 기능 테스트:")
    try:
        from app.services.predictive_analytics import PredictiveAnalyzer
        predictor = PredictiveAnalyzer()
        print("✅ 예측 분석기 로드 성공")
    except Exception as e:
        print(f"❌ 예측 분석기 로드 실패: {e}")
    
    # 6. 데이터베이스 연결 테스트
    print("\n6️⃣ 데이터베이스 연결 테스트:")
    try:
        from app.db.database import test_connection
        if test_connection():
            print("✅ 데이터베이스 연결 성공")
        else:
            print("⚠️ 데이터베이스 연결 실패 (설정 확인 필요)")
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")
    
    # 7. API 라우터 테스트
    print("\n7️⃣ API 라우터 테스트:")
    try:
        from app.api.upload import router as upload_router
        print("✅ 업로드 라우터 로드 성공")
    except Exception as e:
        print(f"❌ 업로드 라우터 로드 실패: {e}")
    
    try:
        from app.api.analysis import router as analysis_router
        print("✅ 분석 라우터 로드 성공")
    except Exception as e:
        print(f"❌ 분석 라우터 로드 실패: {e}")
    
    print("\n🎯 테스트 완료!")
    print("✅ 정상 작동하는 기능들을 확인했습니다.")
    print("⚠️ 실패한 기능들은 개별적으로 수정이 필요합니다.")
    
    return True

if __name__ == "__main__":
    test_v5_features()
