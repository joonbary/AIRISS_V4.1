# -*- coding: utf-8 -*-
"""
업로드된 파일을 평가의견 분석 형식으로 변환
"""
import pandas as pd
import sys
import io

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 입력 파일 경로
input_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\uploads\3c086f7c-8451-4755-bf86-c26a591ec80d_assessment_dummy_opinion.xlsx"
output_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\converted_opinion_file.xlsx"

print("=== 평가의견 분석용 파일 변환 ===")

try:
    # 원본 파일 읽기
    df = pd.read_excel(input_file)
    print(f"원본 파일 로드: {len(df)} 행, {len(df.columns)} 컬럼")
    
    # 헤더 행 제거 (첫 번째 행이 컬럼명)
    df = df.iloc[1:].reset_index(drop=True)
    print(f"헤더 제거 후: {len(df)} 행")
    
    # UID와 평가의견만 추출 (연도별 형식으로 변환)
    new_df = pd.DataFrame()
    new_df['UID'] = df['Unnamed: 0']
    # API가 연도별 의견을 기대하므로 2024년 의견으로 설정
    new_df['의견_2024'] = df['Unnamed: 21']
    
    # NaN 값 제거
    new_df = new_df.dropna(subset=['UID', '의견_2024'])
    
    print(f"유효한 데이터: {len(new_df)} 행")
    
    # 샘플 데이터 확인
    print("\n=== 변환된 데이터 샘플 ===")
    for idx, row in new_df.head(3).iterrows():
        print(f"UID: {row['UID']}")
        print(f"의견: {str(row['의견_2024'])[:100]}...")
        print()
    
    # 파일 저장
    new_df.to_excel(output_file, index=False)
    print(f"변환된 파일 저장: {output_file}")
    
    print("\n=== 변환 완료 ===")
    print(f"- 총 직원 수: {len(new_df)}")
    print(f"- 평균 의견 길이: {new_df['의견_2024'].str.len().mean():.1f}자")
    
except Exception as e:
    print(f"오류: {str(e)}")
    import traceback
    traceback.print_exc()