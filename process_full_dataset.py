# -*- coding: utf-8 -*-
"""
전체 데이터셋 처리 (1410명)
"""
import requests
import sys
import io
import time

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 엔드포인트
base_url = "http://localhost:8003"
upload_url = f"{base_url}/api/v1/analysis/upload/excel"

# 전체 변환된 파일 경로
file_path = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\converted_opinion_file.xlsx"

try:
    # 파일 업로드
    with open(file_path, 'rb') as f:
        files = {'file': ('converted_opinion_file.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        data = {
            'uid_column': 'UID',
            'sheet_name': None
        }
        
        print("=== 전체 평가의견 파일 분석 시작 (1410명) ===")
        print(f"파일: {file_path}")
        print(f"UID 컬럼: {data['uid_column']}")
        print("의견 컬럼: 의견_2024 (연도별 형식)")
        print(f"예상 소요 시간: 약 3시간")
        
        start_time = time.time()
        print(f"\n분석 시작: {time.strftime('%H:%M:%S')}")
        print("처리 중... (완료까지 오래 걸릴 수 있습니다)")
        
        # 타임아웃을 15분(900초)로 설정
        response = requests.post(upload_url, files=files, data=data, timeout=900)
        
        end_time = time.time()
        elapsed_minutes = (end_time - start_time) / 60
        print(f"분석 종료: {time.strftime('%H:%M:%S')} (소요시간: {elapsed_minutes:.1f}분)")
        
        print(f"\nStatus Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            success_count = result.get('successfully_analyzed', 0)
            failed_count = result.get('failed', 0)
            total_count = result.get('total_uploaded', 0)
            
            print(f"✅ 성공적으로 분석된 직원 수: {success_count}")
            print(f"❌ 실패한 직원 수: {failed_count}")
            print(f"📊 전체 업로드 수: {total_count}")
            print(f"📝 메시지: {result.get('message', '')}")
            
            # 성공률 계산
            if total_count > 0:
                success_rate = (success_count / total_count) * 100
                print(f"📈 성공률: {success_rate:.1f}%")
                
                # 시간당 처리량 계산
                if elapsed_minutes > 0:
                    per_hour = success_count / elapsed_minutes * 60
                    print(f"⚡ 처리 속도: {per_hour:.1f}명/시간")
            
        else:
            print(f"Error Response: {response.text}")
        
except requests.Timeout:
    print("⏰ 타임아웃 발생: 15분 내에 처리가 완료되지 않았습니다.")
    print("서버에서 백그라운드로 계속 처리 중일 수 있습니다.")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    
print("\n처리 완료 후 개별 결과 확인:")
print("python check_analysis_result.py 실행")