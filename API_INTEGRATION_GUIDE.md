# AIRISS 분석결과 API 연동 가이드

AIRISS v5.0의 AI 분석 결과를 다른 시스템에서 활용하기 위한 REST API 가이드입니다.

## 📋 목차
1. [기본 정보](#기본-정보)
2. [인재풀 분석 API](#인재풀-분석-api)
3. [부서별 성과 분석 API](#부서별-성과-분석-api)
4. [리스크 분석 API](#리스크-분석-api)
5. [데이터 내보내기 API](#데이터-내보내기-api)
6. [사용 예제](#사용-예제)
7. [에러 처리](#에러-처리)

## 🏢 기본 정보

**Base URL**: `https://your-airiss-domain.com`
**API Version**: v1
**Content-Type**: `application/json`
**인코딩**: UTF-8

---

## 👥 인재풀 분석 API

### `GET /api/v1/airiss/talent-analysis`

핵심인재, 승진후보군, 우수인재 등의 분석 결과를 제공합니다.

#### 응답 구조
```json
{
  "status": "success",
  "summary": {
    "total_employees": 150,
    "core_talent_count": 23,
    "promotion_candidates_count": 18,
    "high_performers_count": 35,
    "development_needed_count": 45,
    "at_risk_count": 12,
    "talent_density": 15.33,
    "analysis_date": "2024-01-15 14:30:25"
  },
  "talent_pools": {
    "core_talent": [
      {
        "employee_id": "EMP001",
        "name": "김핵심",
        "department": "영업본부",
        "position": "팀장",
        "grade": "S",
        "score": 925,
        "years_of_service": 8,
        "last_evaluation": "2024-01-10"
      }
    ],
    "promotion_candidates": [...],
    "high_performers": [...],
    "development_needed": [...],
    "at_risk": [...]
  }
}
```

#### 인재풀 분류 기준
- **핵심인재 (core_talent)**: S, A+ 등급
- **승진후보 (promotion_candidates)**: A+ 등급 또는 800점 이상 A등급
- **우수인재 (high_performers)**: A 등급
- **개발필요 (development_needed)**: B+, B 등급
- **위험인재 (at_risk)**: C, D 등급

---

## 🏢 부서별 성과 분석 API

### `GET /api/v1/airiss/department-performance`

부서별 성과 현황과 인재 분포를 제공합니다.

#### 응답 구조
```json
{
  "status": "success",
  "analysis_date": "2024-01-15 14:30:25",
  "total_departments": 8,
  "departments": [
    {
      "department": "IT본부",
      "total_employees": 25,
      "average_score": 782,
      "core_talent_count": 6,
      "talent_ratio": 24.0,
      "grade_distribution": {
        "S": 2,
        "A+": 4,
        "A": 8,
        "B+": 6,
        "B": 3,
        "C": 2,
        "D": 0
      },
      "performance_level": "우수",
      "employees": [
        {
          "employee_id": "EMP001",
          "name": "김개발",
          "position": "선임연구원",
          "grade": "S",
          "score": 925
        }
      ]
    }
  ]
}
```

#### 성과 수준 분류
- **우수**: 평균 점수 750점 이상
- **보통**: 평균 점수 650-749점
- **개선필요**: 평균 점수 650점 미만

---

## ⚠️ 리스크 분석 API

### `GET /api/v1/airiss/risk-analysis`

조직의 위험 요소와 리텐션 관련 분석을 제공합니다.

#### 응답 구조
```json
{
  "status": "success",
  "analysis_date": "2024-01-15 14:30:25",
  "risk_summary": {
    "total_employees": 150,
    "average_score": 695,
    "overall_risk_level": "MEDIUM",
    "high_risk_count": 12,
    "medium_risk_count": 18,
    "low_risk_count": 35,
    "retention_candidates_count": 8,
    "high_risk_rate": 8.0,
    "grade_distribution": {...},
    "recommendations": [
      "핵심 인재 리텐션 전략 강화",
      "전사 교육 및 개발 프로그램 확대"
    ]
  },
  "risk_categories": {
    "high_risk": [...],
    "medium_risk": [...],
    "low_risk": [...],
    "retention_candidates": [...]
  }
}
```

#### 위험도 분류
- **HIGH**: 고위험 인력 비율 20% 초과
- **MEDIUM**: 고위험 인력 비율 10-20%
- **LOW**: 고위험 인력 비율 10% 미만

---

## 📁 데이터 내보내기 API

### `GET /api/v1/airiss/export/csv?analysis_type=talent`

분석 결과를 CSV 파일로 다운로드합니다.

#### 파라미터
- `analysis_type`: 내보낼 분석 유형 (기본값: "talent")

#### 응답
CSV 파일 스트림 (UTF-8 BOM 포함)

#### CSV 구조
```csv
직원ID,이름,부서,직급,등급,점수,인재분류,분석일시
EMP001,김핵심,영업본부,팀장,S,925,핵심인재,2024-01-15 14:30:25
EMP002,이우수,마케팅부,과장,A+,856,핵심인재,2024-01-15 14:30:25
```

---

## 💻 사용 예제

### Python 예제
```python
import requests
import json

# 기본 설정
BASE_URL = "https://your-airiss-domain.com"
headers = {"Content-Type": "application/json"}

# 1. 핵심인재 목록 조회
response = requests.get(f"{BASE_URL}/api/v1/airiss/talent-analysis", headers=headers)
talent_data = response.json()

print(f"핵심인재 수: {talent_data['summary']['core_talent_count']}명")
print(f"승진후보 수: {talent_data['summary']['promotion_candidates_count']}명")

# 2. 부서별 성과 조회
response = requests.get(f"{BASE_URL}/api/v1/airiss/department-performance", headers=headers)
dept_data = response.json()

for dept in dept_data['departments']:
    print(f"{dept['department']}: 평균 {dept['average_score']}점 ({dept['performance_level']})")

# 3. CSV 다운로드
response = requests.get(f"{BASE_URL}/api/v1/airiss/export/csv?analysis_type=talent")
with open("airiss_talent_analysis.csv", "wb") as f:
    f.write(response.content)
```

### JavaScript 예제
```javascript
// 기본 설정
const BASE_URL = 'https://your-airiss-domain.com';

// 1. 인재풀 분석 조회
async function getTalentAnalysis() {
    try {
        const response = await fetch(`${BASE_URL}/api/v1/airiss/talent-analysis`);
        const data = await response.json();
        
        console.log('핵심인재 수:', data.summary.core_talent_count);
        console.log('승진후보 수:', data.summary.promotion_candidates_count);
        
        return data;
    } catch (error) {
        console.error('API 호출 실패:', error);
    }
}

// 2. 부서별 성과 조회
async function getDepartmentPerformance() {
    try {
        const response = await fetch(`${BASE_URL}/api/v1/airiss/department-performance`);
        const data = await response.json();
        
        data.departments.forEach(dept => {
            console.log(`${dept.department}: ${dept.average_score}점 (${dept.performance_level})`);
        });
        
        return data;
    } catch (error) {
        console.error('API 호출 실패:', error);
    }
}

// 3. 리스크 분석 조회
async function getRiskAnalysis() {
    try {
        const response = await fetch(`${BASE_URL}/api/v1/airiss/risk-analysis`);
        const data = await response.json();
        
        console.log('전체 위험도:', data.risk_summary.overall_risk_level);
        console.log('고위험 인력:', data.risk_summary.high_risk_count);
        
        return data;
    } catch (error) {
        console.error('API 호출 실패:', error);
    }
}
```

### cURL 예제
```bash
# 1. 인재풀 분석 조회
curl -X GET "https://your-airiss-domain.com/api/v1/airiss/talent-analysis" \
     -H "Content-Type: application/json"

# 2. 부서별 성과 조회
curl -X GET "https://your-airiss-domain.com/api/v1/airiss/department-performance" \
     -H "Content-Type: application/json"

# 3. 리스크 분석 조회
curl -X GET "https://your-airiss-domain.com/api/v1/airiss/risk-analysis" \
     -H "Content-Type: application/json"

# 4. CSV 다운로드
curl -X GET "https://your-airiss-domain.com/api/v1/airiss/export/csv?analysis_type=talent" \
     -H "Content-Type: application/json" \
     -o "airiss_analysis.csv"
```

---

## 🚨 에러 처리

### 표준 에러 응답
```json
{
  "detail": "에러 메시지",
  "status_code": 500
}
```

### 주요 에러 코드
- **404**: 데이터를 찾을 수 없음
- **500**: 서버 내부 오류
- **422**: 잘못된 파라미터

### 에러 처리 예제
```python
try:
    response = requests.get(f"{BASE_URL}/api/v1/airiss/talent-analysis")
    response.raise_for_status()  # HTTP 에러 체크
    
    data = response.json()
    if data.get('status') != 'success':
        print(f"API 에러: {data.get('message', '알 수 없는 오류')}")
    else:
        # 정상 처리
        print(f"분석 완료: {data['summary']['total_employees']}명 분석됨")
        
except requests.exceptions.RequestException as e:
    print(f"네트워크 오류: {e}")
except json.JSONDecodeError as e:
    print(f"JSON 파싱 오류: {e}")
```

---

## 🔄 정기 연동 예제

### 매일 오전 9시 인재 현황 업데이트
```python
import schedule
import time
import requests

def update_talent_status():
    """매일 인재 현황을 업데이트하는 함수"""
    try:
        # AIRISS에서 최신 분석 결과 조회
        response = requests.get("https://your-airiss-domain.com/api/v1/airiss/talent-analysis")
        talent_data = response.json()
        
        # 외부 시스템으로 데이터 전송
        external_api_update(talent_data)
        
        print(f"인재 현황 업데이트 완료: {talent_data['summary']['analysis_date']}")
        
    except Exception as e:
        print(f"업데이트 실패: {e}")

def external_api_update(data):
    """외부 시스템 API 호출 예제"""
    # 외부 시스템의 API 엔드포인트로 데이터 전송
    external_url = "https://your-external-system.com/api/hr/talent-update"
    
    # 필요한 데이터만 추출하여 전송
    update_data = {
        "core_talent_count": data['summary']['core_talent_count'],
        "promotion_candidates": data['talent_pools']['promotion_candidates'],
        "analysis_date": data['summary']['analysis_date']
    }
    
    response = requests.post(external_url, json=update_data)
    response.raise_for_status()

# 스케줄 설정
schedule.every().day.at("09:00").do(update_talent_status)

# 실행
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 📞 지원 및 문의

- **기술 문의**: AIRISS 개발팀
- **API 버전**: v1.0
- **최신 업데이트**: 2024.01.15

이 가이드를 참조하여 AIRISS의 AI 인사 분석 결과를 다른 시스템과 효율적으로 연동하실 수 있습니다.