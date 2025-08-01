# -*- coding: utf-8 -*-
"""
정수빈 UID 찾기
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.employee import EmployeeResult
from app.core.config import settings
import json

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # PostgreSQL JSON 쿼리 사용
    query = text("""
        SELECT uid, overall_score, grade, employee_metadata
        FROM employee_results
        WHERE employee_metadata->>'name' = '정수빈'
        LIMIT 10
    """)
    
    results = db.execute(query)
    
    print("=== 정수빈 검색 결과 ===")
    found = False
    for row in results:
        found = True
        print(f"\nUID: {row.uid}")
        print(f"Overall Score: {row.overall_score}")
        print(f"Grade: {row.grade}")
        print(f"Metadata: {row.employee_metadata}")
        
    if not found:
        print("정수빈 데이터를 찾을 수 없습니다.")
        
        # 이름이 있는 모든 데이터 확인
        print("\n=== 이름이 있는 데이터 샘플 ===")
        query2 = text("""
            SELECT uid, overall_score, employee_metadata
            FROM employee_results
            WHERE employee_metadata->>'name' IS NOT NULL
            AND employee_metadata->>'name' != ''
            LIMIT 10
        """)
        
        results2 = db.execute(query2)
        for row in results2:
            name = row.employee_metadata.get('name', 'N/A')
            print(f"UID: {row.uid}, Name: {name}, Score: {row.overall_score}")
            
finally:
    db.close()