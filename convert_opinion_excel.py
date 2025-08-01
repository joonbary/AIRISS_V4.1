# -*- coding: utf-8 -*-
"""
평가의견 엑셀 파일을 AIRISS 형식으로 변환
Convert assessment opinion Excel to AIRISS format
"""
import pandas as pd
import json

# 원본 파일 경로
input_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\AIRISS_평가정제\assessment_dummy_opinion.xlsx"
output_file = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\opinion_data_converted.xlsx"

try:
    # 엑셀 파일 읽기
    df = pd.read_excel(input_file)
    
    print("=== Converting Assessment Opinion Data ===")
    print(f"Total rows: {len(df)}")
    
    # 새로운 데이터프레임 생성
    converted_data = []
    
    # 첫 번째 행은 헤더이므로 제외
    for idx, row in df.iloc[1:].iterrows():
        uid = str(row['Unnamed: 0'])  # UID
        
        if uid and uid != 'nan':
            record = {'UID': uid}
            
            # 평가의견 컬럼 (.1로 끝나는 컬럼들)
            opinion_cols = [col for col in df.columns if str(col).endswith('.1')]
            
            for col in opinion_cols:
                # 연도 추출 (예: "2023년 상반기.1" -> "의견_2023상")
                year_info = str(col).replace('.1', '')
                if '년' in year_info:
                    year = year_info.split('년')[0]
                    period = '상' if '상반기' in year_info else '하'
                    
                    # 새 컬럼명
                    new_col_name = f'의견_{year}{period}'
                    
                    # 평가의견 값
                    opinion = row[col]
                    if pd.notna(opinion) and str(opinion) != '0' and str(opinion) != 'nan':
                        record[new_col_name] = str(opinion)
                    else:
                        record[new_col_name] = None
            
            converted_data.append(record)
    
    # 데이터프레임 생성
    result_df = pd.DataFrame(converted_data)
    
    # 연도별로 통합 (상반기/하반기를 하나로)
    final_data = []
    for idx, row in result_df.iterrows():
        uid = row['UID']
        combined_record = {'UID': uid}
        
        # 연도별로 의견 통합
        for year in ['2020', '2021', '2022', '2023', '2024']:
            opinions = []
            
            # 상반기 의견
            col_up = f'의견_{year}상'
            if col_up in row and pd.notna(row[col_up]):
                opinions.append(f"[상반기] {row[col_up]}")
            
            # 하반기 의견
            col_down = f'의견_{year}하'
            if col_down in row and pd.notna(row[col_down]):
                opinions.append(f"[하반기] {row[col_down]}")
            
            # 통합
            if opinions:
                combined_record[f'의견_{year}'] = ' '.join(opinions)
            else:
                combined_record[f'의견_{year}'] = None
        
        final_data.append(combined_record)
    
    # 최종 데이터프레임
    final_df = pd.DataFrame(final_data)
    
    # 유효한 의견이 있는 행만 필터링
    valid_rows = []
    for idx, row in final_df.iterrows():
        has_opinion = False
        for col in final_df.columns:
            if col.startswith('의견_') and pd.notna(row[col]):
                has_opinion = True
                break
        if has_opinion:
            valid_rows.append(row)
    
    final_df = pd.DataFrame(valid_rows)
    
    print(f"\nConverted {len(final_df)} employees with valid opinions")
    print(f"\nColumns: {list(final_df.columns)}")
    
    # 샘플 출력
    print("\n=== Sample Data ===")
    print(final_df.head(3))
    
    # 엑셀로 저장
    final_df.to_excel(output_file, index=False)
    print(f"\nSaved to: {output_file}")
    
    # CSV로도 저장 (UTF-8 BOM)
    csv_file = output_file.replace('.xlsx', '.csv')
    final_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"Also saved as CSV: {csv_file}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()