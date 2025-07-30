#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""중복 데이터 정리 스크립트"""

from app.db.database import SessionLocal
from app.models.employee import EmployeeResult
from sqlalchemy import text

db = SessionLocal()

print("=== 현재 EmployeeResult 테이블 상태 ===")

# Raw SQL로 확인
result = db.execute(text("SELECT COUNT(*) FROM employee_results"))
count = result.scalar()
print(f"employee_results 테이블의 총 레코드 수: {count}")

# 모든 레코드 조회
result = db.execute(text("""
    SELECT id, uid, overall_score, grade, employee_metadata 
    FROM employee_results 
    ORDER BY uid, overall_score DESC
"""))
records = result.fetchall()

print(f"\n총 {len(records)}개 레코드:")
for r in records:
    metadata = r.employee_metadata or {}
    name = metadata.get('name', 'No Name') if metadata else 'No Metadata'
    print(f"ID: {r.id[:8]}..., UID: {r.uid}, Score: {r.overall_score}, Grade: {r.grade}, Name: {name}")

# 중복 확인
result = db.execute(text("""
    SELECT uid, COUNT(*) as cnt 
    FROM employee_results 
    GROUP BY uid 
    HAVING COUNT(*) > 1
"""))
duplicates = result.fetchall()

if duplicates:
    print("\n=== 중복된 UID ===")
    for uid, cnt in duplicates:
        print(f"{uid}: {cnt}개")
else:
    print("\n중복된 UID가 없습니다.")

db.close()