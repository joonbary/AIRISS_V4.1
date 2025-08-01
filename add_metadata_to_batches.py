# -*- coding: utf-8 -*-
"""
배치 파일에 이름, 부서, 직급 가상 데이터 추가
"""
import pandas as pd
import random
import os
import sys
import io

# 콘솔 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 한국식 성씨와 이름
last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전']
first_names = ['민수', '지현', '서연', '동현', '수진', '영희', '준호', '미경', '성민', '은주', '현우', '지영', '민준', '서윤', '예진', '준영', '수빈', '진우', '하늘', '유진']

# 실제 부서 목록
departments = [
    '대전중앙지점', '대전지점', '동대문PL팀', '디자인팀', '디지털데이터팀',
    '디지털센터기획팀', '디지털운영팀', '디지털채널1팀', '디지털채널2팀', '디지털채널부',
    '리스크관리본부', '리스크관리부', '리스크관리팀', '리테일기획부', '리테일기획팀',
    '마이데이터팀', '마케팅본부', '마케팅부', '마케팅팀', '모기지관리팀',
    '모기지기획팀', '모기지사업부', '모기지심사팀', '모기지업무지원팀', '모기지영업팀',
    '모기지팀', '미래디지털본부', '미래디지털부', '미래사업추진단', '법무팀',
    '보안기획팀', '보안운영팀', '보호감시팀', '부산1지점', '부산2지점',
    '부산PL관리2지점', '부산PL관리지점', '부산지점', '분당기업금융센터', '비서실',
    '서울역출장소', '선릉기업금융센터', '소비자금융기획부', '소비자금융기획팀', '소비자금융본부',
    '소비자금융부', '소비자금융영업부', '송무지원센터', '송무팀', '수신팀',
    '수원PL팀', '수원지점', '스포츠단사무국', '스포츠마케팅팀', '스포츠운영팀',
    '시스템운영부전주2지점', '정보보안부', '정보보안실', '정보보안팀', '정보서비스팀',
    '제주PL관리지점', '제주지점', '조직문화팀', '종합여신센터', '준법감시팀',
    '준법지원부', '준법지원실', '준법지원팀', '중기1팀', '중기2팀',
    '중기4팀', '중기5팀', '채권관리센터', '채권관리팀', '채권기획부',
    '채권기획팀', '채권운영팀', '채널기획팀', '채무조정팀', '청주지점',
    '총무부', '총무팀', '콜렉션1팀', '콜렉션센터', '콜렉션팀',
    '통합접수센터', '통합접수팀', '페이서비스팀', '평촌지점', '포항PL관리지점',
    '포항지점', '플랫폼기획팀', '해외사업부', '해외시장조사팀', '홍보CSR팀',
    '홍보부', '회계본부', '회계팀', '회생채권팀'
]

# 직급 목록 (금융권 일반적인 직급 체계)
positions = [
    '사원', '사원', '사원', '주임', '주임', '주임',  # 낮은 직급 비중 높게
    '대리', '대리', '대리', '과장', '과장', '과장',
    '차장', '차장', '부장', '부장',
    '팀장', '부서장', '본부장', '임원'
]

# 배치 디렉토리
batch_dir = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\batches"
output_dir = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\batches_with_metadata"

print("=== 배치 파일에 메타데이터 추가 ===")

try:
    # 출력 디렉토리 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"출력 디렉토리 생성: {output_dir}")
    
    # 모든 배치 파일 처리
    batch_files = [f for f in os.listdir(batch_dir) if f.endswith('.xlsx')]
    
    # UID별로 일관된 메타데이터를 유지하기 위한 딕셔너리
    uid_metadata = {}
    
    for batch_file in sorted(batch_files):
        if 'test' in batch_file:  # 테스트 파일도 포함
            pass
        
        input_path = os.path.join(batch_dir, batch_file)
        output_path = os.path.join(output_dir, batch_file)
        
        # 배치 파일 읽기
        df = pd.read_excel(input_path)
        
        # 새로운 컬럼 추가
        names = []
        departments_list = []
        positions_list = []
        
        for uid in df['UID']:
            # 이미 할당된 메타데이터가 있으면 재사용
            if uid not in uid_metadata:
                # 랜덤하게 생성
                name = random.choice(last_names) + random.choice(first_names)
                dept = random.choice(departments)
                pos = random.choice(positions)
                
                # 저장
                uid_metadata[uid] = {
                    'name': name,
                    'department': dept,
                    'position': pos
                }
            
            # 메타데이터 추가
            names.append(uid_metadata[uid]['name'])
            departments_list.append(uid_metadata[uid]['department'])
            positions_list.append(uid_metadata[uid]['position'])
        
        # 데이터프레임에 추가
        df.insert(1, '이름', names)  # UID 다음에 삽입
        df.insert(2, '부서', departments_list)
        df.insert(3, '직급', positions_list)
        
        # 저장
        df.to_excel(output_path, index=False)
        print(f"처리 완료: {batch_file} ({len(df)}명)")
        
        # 첫 번째 파일의 샘플 출력
        if batch_file == 'batch_001_of_19.xlsx':
            print("\n=== 샘플 데이터 ===")
            for i in range(min(5, len(df))):
                print(f"UID: {df.iloc[i]['UID']}, 이름: {df.iloc[i]['이름']}, "
                      f"부서: {df.iloc[i]['부서']}, 직급: {df.iloc[i]['직급']}")
    
    print(f"\n✅ 메타데이터 추가 완료!")
    print(f"새 파일 위치: {output_dir}")
    print(f"총 {len(uid_metadata)}명의 직원에게 메타데이터 할당")
    
    # 부서별 분포 확인
    dept_counts = {}
    for meta in uid_metadata.values():
        dept = meta['department']
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    print("\n=== 부서별 직원 분포 (상위 10개) ===")
    sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for dept, count in sorted_depts:
        print(f"{dept}: {count}명")
    
except Exception as e:
    print(f"오류: {str(e)}")
    import traceback
    traceback.print_exc()