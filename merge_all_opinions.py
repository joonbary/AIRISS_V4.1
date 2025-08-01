# -*- coding: utf-8 -*-
"""
5년간 모든 평가의견을 하나로 통합
"""
import pandas as pd
import sys
import io

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 입력 파일 경로
input_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\complete_opinions_for_analysis.xlsx"
output_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\merged_all_opinions.xlsx"

print("=== 5년간 모든 평가의견 통합 ===")

try:
    # 변환된 파일 읽기
    df = pd.read_excel(input_file)
    print(f"원본 파일 로드: {len(df)} 행")
    
    # 새로운 데이터프레임 생성
    new_df = pd.DataFrame()
    new_df['UID'] = df['UID']
    
    # 모든 연도의 평가의견을 하나로 통합
    all_opinions = []
    
    for index, row in df.iterrows():
        combined_text = ""
        
        # 2020년부터 2025년까지 순차적으로 통합
        for year in ['2020', '2021', '2022', '2023', '2024', '2025']:
            col_name = f'의견_{year}'
            if col_name in df.columns and row[col_name] and str(row[col_name]).strip():
                if combined_text:
                    combined_text += "\n\n"
                combined_text += str(row[col_name])
        
        all_opinions.append(combined_text)
    
    # 통합된 평가의견 추가
    new_df['평가의견'] = all_opinions
    
    # 빈 평가의견 제거
    new_df = new_df[new_df['평가의견'].str.strip() != '']
    
    print(f"\n유효한 데이터: {len(new_df)} 행")
    
    # 샘플 데이터 확인
    print("\n=== 통합된 데이터 샘플 (첫 번째 직원) ===")
    if len(new_df) > 0:
        row = new_df.iloc[0]
        print(f"UID: {row['UID']}")
        print(f"\n평가의견 (처음 500자):")
        opinion = str(row['평가의견'])
        if len(opinion) > 500:
            print(opinion[:500] + "...")
        else:
            print(opinion)
        print(f"\n전체 평가의견 길이: {len(opinion)}자")
    
    # 통계 정보
    print("\n=== 통계 정보 ===")
    lengths = new_df['평가의견'].str.len()
    print(f"평균 평가의견 길이: {lengths.mean():.0f}자")
    print(f"최소 평가의견 길이: {lengths.min()}자")
    print(f"최대 평가의견 길이: {lengths.max()}자")
    
    # 파일 저장
    new_df.to_excel(output_file, index=False)
    print(f"\n통합 파일 저장: {output_file}")
    print(f"총 {len(new_df)}명의 직원 데이터")
    
except Exception as e:
    print(f"오류: {str(e)}")
    import traceback
    traceback.print_exc()