# -*- coding: utf-8 -*-
"""
모든 연도별 평가의견을 포함하여 변환
"""
import pandas as pd
import sys
import io

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 입력 파일 경로
input_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\uploads\3c086f7c-8451-4755-bf86-c26a591ec80d_assessment_dummy_opinion.xlsx"
output_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\full_opinions_converted.xlsx"

print("=== 전체 평가의견 변환 (10년치) ===")

try:
    # 원본 파일 읽기
    df = pd.read_excel(input_file)
    print(f"원본 파일 로드: {len(df)} 행, {len(df.columns)} 컬럼")
    
    # 첫 번째 행 확인 (컬럼명 확인)
    print("\n=== 컬럼 구조 확인 ===")
    first_row = df.iloc[0]
    for i, (col, val) in enumerate(zip(df.columns, first_row)):
        if i <= 21:  # 처음 22개 컬럼만
            print(f"{i}: {col} = {str(val)[:50]}...")
    
    # 실제 컬럼명이 첫 번째 행에 있다면
    if '직원번호' in str(first_row.iloc[0]) or 'UID' in str(first_row.iloc[0]):
        # 첫 번째 행을 컬럼명으로 설정
        new_columns = first_row.values
        df.columns = new_columns
        df = df.iloc[1:].reset_index(drop=True)
        print(f"\n컬럼명 재설정 후: {len(df)} 행")
    
    # 새로운 데이터프레임 생성
    new_df = pd.DataFrame()
    
    # UID 컬럼 찾기
    uid_col = None
    for col in df.columns:
        if 'Unnamed: 0' in str(col) or 'UID' in str(col) or '직원' in str(col):
            uid_col = col
            break
    
    if uid_col:
        new_df['UID'] = df[uid_col]
        print(f"\nUID 컬럼 발견: {uid_col}")
    else:
        print("UID 컬럼을 찾을 수 없습니다!")
        exit()
    
    # 평가의견 컬럼들 추출 (1~20번 컬럼이 연도별 평가)
    opinion_cols = []
    for i in range(1, 21):
        col_name = f'Unnamed: {i}' if f'Unnamed: {i}' in df.columns else df.columns[i]
        if col_name in df.columns:
            opinion_cols.append(col_name)
    
    print(f"\n평가의견 컬럼 수: {len(opinion_cols)}")
    
    # 각 평가의견을 연도별로 매핑
    # 10년간 상/하반기 = 20개 컬럼
    years = []
    for year in range(2015, 2025):  # 2015-2024 (10년)
        years.append(f'{year}_상반기')
        years.append(f'{year}_하반기')
    
    # 평가의견 매핑
    for i, (col, year_label) in enumerate(zip(opinion_cols[:20], years[:20])):
        new_col_name = f'의견_{year_label}'
        new_df[new_col_name] = df[col]
        print(f"  {col} → {new_col_name}")
    
    # 종합의견도 포함 (21번째 컬럼)
    if 'Unnamed: 21' in df.columns:
        new_df['의견_종합'] = df['Unnamed: 21']
        print(f"  Unnamed: 21 → 의견_종합")
    
    # NaN 값이 있는 행 제거 (UID가 없는 행)
    new_df = new_df.dropna(subset=['UID'])
    
    print(f"\n유효한 데이터: {len(new_df)} 행")
    
    # 샘플 데이터 확인
    print("\n=== 변환된 데이터 샘플 (첫 번째 직원) ===")
    if len(new_df) > 0:
        row = new_df.iloc[0]
        print(f"UID: {row['UID']}")
        for col in new_df.columns:
            if '의견_' in col and pd.notna(row[col]):
                print(f"{col}: {str(row[col])[:50]}...")
    
    # 파일 저장
    new_df.to_excel(output_file, index=False)
    print(f"\n변환된 파일 저장: {output_file}")
    print(f"총 {len(new_df)}명의 직원, {len(opinion_cols)+1}개의 평가의견 컬럼")
    
except Exception as e:
    print(f"오류: {str(e)}")
    import traceback
    traceback.print_exc()