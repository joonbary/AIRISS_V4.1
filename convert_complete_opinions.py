# -*- coding: utf-8 -*-
"""
5년간 상/하반기 강점 및 보완점을 통합하여 변환
"""
import pandas as pd
import sys
import io

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 파일 경로
input_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\AIRISS_평가정제\assessment_dummy_opinion.xlsx"
output_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\complete_opinions_for_analysis.xlsx"

print("=== 5년간 평가의견 통합 변환 ===")

try:
    # 원본 파일 읽기
    df = pd.read_excel(input_file)
    print(f"원본 파일 로드: {len(df)} 행, {len(df.columns)} 컬럼")
    
    # 새로운 데이터프레임 생성
    new_df = pd.DataFrame()
    new_df['UID'] = df['UID']
    
    # 연도별로 평가의견 통합
    years = ['2020', '2021', '2022', '2023', '2024']
    
    for year in years:
        # 각 연도의 평가의견을 통합
        year_short = year[-2:]  # '20', '21', etc.
        
        # 해당 연도의 모든 평가를 하나로 합침
        combined_opinions = []
        
        # 상반기 강점
        col_name = f'{year_short}-상-강점'
        if col_name in df.columns:
            combined_opinions.append(f"[{year}년 상반기 강점]\n" + df[col_name].astype(str))
        
        # 상반기 보완점
        col_name = f'{year_short}-상-보완점'
        if col_name in df.columns:
            combined_opinions.append(f"[{year}년 상반기 보완점]\n" + df[col_name].astype(str))
        
        # 하반기 강점
        col_name = f'{year_short}-하-강점'
        if col_name in df.columns:
            combined_opinions.append(f"[{year}년 하반기 강점]\n" + df[col_name].astype(str))
        
        # 하반기 보완점
        col_name = f'{year_short}-하-보완점'
        if col_name in df.columns:
            combined_opinions.append(f"[{year}년 하반기 보완점]\n" + df[col_name].astype(str))
        
        # 연도별 통합 의견 생성
        if combined_opinions:
            # 각 직원의 의견을 합침
            year_opinion = pd.Series([''] * len(df))
            for opinion_series in combined_opinions:
                year_opinion = year_opinion + '\n\n' + opinion_series
            
            # 결과를 새 컬럼에 저장
            new_df[f'의견_{year}'] = year_opinion.str.strip()
    
    # 2025년 상반기 종합도 추가
    if '25-상-강점 및 보완점' in df.columns:
        new_df['의견_2025'] = '[2025년 상반기 종합]\n' + df['25-상-강점 및 보완점'].astype(str)
    
    # '0' 값이나 '0.0'을 빈 문자열로 변환
    for col in new_df.columns:
        if '의견_' in col:
            new_df[col] = new_df[col].replace(['0', '0.0', 0, 0.0], '')
            # NaN도 빈 문자열로
            new_df[col] = new_df[col].fillna('')
    
    # 유효한 데이터만 남기기 (UID가 있는 행)
    new_df = new_df.dropna(subset=['UID'])
    
    print(f"\n유효한 데이터: {len(new_df)} 행")
    
    # 샘플 데이터 확인
    print("\n=== 변환된 데이터 샘플 (첫 번째 직원) ===")
    if len(new_df) > 0:
        row = new_df.iloc[0]
        print(f"UID: {row['UID']}")
        
        for year in years + ['2025']:
            col_name = f'의견_{year}'
            if col_name in new_df.columns and row[col_name]:
                print(f"\n{col_name}:")
                content = str(row[col_name])
                # 첫 200자만 출력
                if len(content) > 200:
                    print(content[:200] + "...")
                else:
                    print(content)
    
    # 파일 저장
    new_df.to_excel(output_file, index=False)
    print(f"\n변환된 파일 저장: {output_file}")
    print(f"총 {len(new_df)}명의 직원 데이터")
    
    # 통계 정보
    print("\n=== 데이터 통계 ===")
    for year in years + ['2025']:
        col_name = f'의견_{year}'
        if col_name in new_df.columns:
            non_empty = (new_df[col_name] != '').sum()
            print(f"{year}년: {non_empty}명의 평가의견")
    
except Exception as e:
    print(f"오류: {str(e)}")
    import traceback
    traceback.print_exc()