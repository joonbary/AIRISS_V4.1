# -*- coding: utf-8 -*-
"""
대용량 데이터를 작은 배치로 분할
"""
import pandas as pd
import sys
import io
import os

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 입력 파일 경로
input_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\merged_all_opinions.xlsx"
output_dir = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\batches"

# 배치 크기 설정
BATCH_SIZE = 100  # 한 번에 100명씩 처리

print("=== 대용량 파일 배치 분할 ===")

try:
    # 출력 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"출력 디렉토리 생성: {output_dir}")
    
    # 파일 읽기
    df = pd.read_excel(input_file)
    total_rows = len(df)
    print(f"전체 데이터: {total_rows} 행")
    
    # 배치 수 계산
    num_batches = (total_rows + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"배치 수: {num_batches} (각 {BATCH_SIZE}명)")
    
    # 배치별로 분할 저장
    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min((batch_num + 1) * BATCH_SIZE, total_rows)
        
        # 배치 데이터 추출
        batch_df = df.iloc[start_idx:end_idx]
        
        # 파일명 생성
        batch_filename = f"batch_{batch_num + 1:03d}_of_{num_batches}.xlsx"
        batch_path = os.path.join(output_dir, batch_filename)
        
        # 배치 파일 저장
        batch_df.to_excel(batch_path, index=False)
        
        print(f"배치 {batch_num + 1}/{num_batches} 저장: {batch_filename} ({len(batch_df)}명)")
        
        # 첫 번째 배치의 샘플 출력
        if batch_num == 0:
            print(f"  첫 번째 UID: {batch_df.iloc[0]['UID']}")
            print(f"  마지막 UID: {batch_df.iloc[-1]['UID']}")
    
    print(f"\n✅ 분할 완료!")
    print(f"배치 파일 위치: {output_dir}")
    print(f"\n처리 방법:")
    print("1. UI에서 각 배치 파일을 순차적으로 업로드")
    print("2. 각 배치마다 '분석' 버튼 클릭")
    print("3. 한 배치가 완료되면 다음 배치 업로드")
    
    # 작은 테스트 파일도 생성
    test_df = df.head(10)
    test_path = os.path.join(output_dir, "test_10_employees.xlsx")
    test_df.to_excel(test_path, index=False)
    print(f"\n테스트용 파일 생성: test_10_employees.xlsx (10명)")
    
except Exception as e:
    print(f"오류: {str(e)}")
    import traceback
    traceback.print_exc()