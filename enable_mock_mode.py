# -*- coding: utf-8 -*-
"""
Mock 모드 활성화 - OpenAI API 없이 분석
"""
import os

# .env 파일 경로
env_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\.env"

# .env 파일 읽기
with open(env_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# OpenAI API 키 라인을 주석 처리
new_lines = []
for line in lines:
    if line.strip().startswith('OPENAI_API_KEY='):
        new_lines.append('# ' + line)  # 주석 처리
        print(f"OpenAI API 키 비활성화: {line.strip()[:30]}...")
    else:
        new_lines.append(line)

# 파일 다시 쓰기
with open(env_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ Mock 모드 활성화 완료!")
print("서버를 재시작하면 Mock AI 분석이 사용됩니다.")
print("\n다시 OpenAI를 사용하려면:")
print("1. .env 파일에서 # OPENAI_API_KEY 라인의 # 제거")
print("2. OpenAI 계정에서 결제 정보 확인")