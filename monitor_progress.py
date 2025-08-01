# -*- coding: utf-8 -*-
"""
분석 진행 상황 모니터링
"""
import requests
import sys
import io
import time
from sqlalchemy import create_engine, text

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 데이터베이스 연결
DATABASE_URL = "postgresql://neondb_owner:npg_u7NVKxXhpbL8@ep-summer-surf-a153am7x-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # opinion_results 테이블의 레코드 수 확인
        result = conn.execute(text("SELECT COUNT(*) FROM opinion_results"))
        count = result.scalar()
        
        print(f"=== 평가의견 분석 진행 상황 ===")
        print(f"현재까지 분석 완료: {count}명")
        
        # 최근 분석된 데이터 확인
        recent = conn.execute(text("""
            SELECT uid, text_score, hybrid_score, analyzed_at 
            FROM opinion_results 
            ORDER BY analyzed_at DESC 
            LIMIT 5
        """))
        
        print("\n최근 분석된 직원:")
        for row in recent:
            print(f"- UID: {row[0]}, 텍스트점수: {row[1]:.1f}, 하이브리드점수: {row[2]:.1f}, 시간: {row[3]}")
        
        # 평균 점수 확인
        avg_result = conn.execute(text("""
            SELECT 
                AVG(text_score) as avg_text,
                AVG(hybrid_score) as avg_hybrid,
                AVG(confidence) as avg_confidence
            FROM opinion_results
        """))
        
        avg_row = avg_result.fetchone()
        if avg_row[0]:
            print(f"\n현재까지 평균:")
            print(f"- 텍스트 점수: {avg_row[0]:.1f}")
            print(f"- 하이브리드 점수: {avg_row[1]:.1f}")
            print(f"- 신뢰도: {avg_row[2]:.2f}")
        
        print(f"\n목표: 1410명")
        if count > 0:
            progress = (count / 1410) * 100
            print(f"진행률: {progress:.1f}%")
            
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()