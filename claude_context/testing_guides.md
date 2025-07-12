# AIRISS 테스트 가이드

## 🧪 테스트 전략 개요

### 테스트 피라미드
```
         🔺 E2E 테스트 (5%)
       🔹🔹🔹 통합 테스트 (20%)
   🔸🔸🔸🔸🔸🔸🔸 단위 테스트 (75%)
```

### 테스트 원칙
1. **빠른 피드백**: 단위 테스트는 3초 이내 완료
2. **신뢰성**: 테스트 결과가 일관되어야 함
3. **유지보수성**: 코드 변경시 테스트도 쉽게 수정 가능
4. **가독성**: 테스트 코드는 문서 역할도 수행

---

## 🎯 테스트 유형별 가이드

### 1. 단위 테스트 (Unit Tests)

#### 🔍 테스트 대상
```python
✅ 반드시 테스트해야 할 함수들:
- hybrid_analyzer.py의 모든 계산 함수
- text_analyzer.py의 키워드 매칭 로직
- quantitative_analyzer.py의 점수 계산
- 모든 데이터 변환 함수
- 비즈니스 로직 함수들
```

#### 📝 테스트 예시
```python
# tests/test_text_analyzer.py
import pytest
from app.services.text_analyzer import AIRISSTextAnalyzer

class TestTextAnalyzer:
    def setup_method(self):
        """각 테스트 전에 실행"""
        self.analyzer = AIRISSTextAnalyzer()
    
    def test_analyze_positive_text(self):
        """긍정적 텍스트 분석 테스트"""
        text = "뛰어난 성과를 달성했습니다"
        result = self.analyzer.analyze_text(text, "업무성과")
        
        assert result['score'] > 70
        assert result['confidence'] > 0.5
        assert '뛰어난' in result['matched_keywords']
    
    def test_analyze_negative_text(self):
        """부정적 텍스트 분석 테스트"""
        text = "목표를 달성하지 못했습니다"
        result = self.analyzer.analyze_text(text, "업무성과")
        
        assert result['score'] < 50
        assert '달성하지 못' in result['matched_keywords']
    
    def test_empty_text_handling(self):
        """빈 텍스트 처리 테스트"""
        result = self.analyzer.analyze_text("", "업무성과")
        
        assert result['score'] == 50  # 기본값
        assert result['confidence'] == 0
    
    @pytest.mark.parametrize("dimension", [
        "업무성과", "리더십협업", "커뮤니케이션", "전문성학습"
    ])
    def test_all_dimensions(self, dimension):
        """모든 차원 테스트"""
        text = "우수한 성과를 보여주었습니다"
        result = self.analyzer.analyze_text(text, dimension)
        
        assert 'score' in result
        assert 'confidence' in result
        assert isinstance(result['score'], (int, float))
```

#### 🛠️ 단위 테스트 실행
```bash
# 전체 단위 테스트 실행
pytest tests/unit/ -v

# 특정 파일 테스트
pytest tests/test_text_analyzer.py -v

# 커버리지 확인
pytest tests/unit/ --cov=app --cov-report=html
```

### 2. 통합 테스트 (Integration Tests)

#### 🔍 테스트 대상
```python
✅ 통합 테스트 시나리오:
- 파일 업로드 → 분석 → 결과 저장 전체 플로우
- API 엔드포인트 간 데이터 흐름
- 데이터베이스 연동 기능
- WebSocket 실시간 통신
- 외부 서비스 연동 (있는 경우)
```

#### 📝 테스트 예시
```python
# tests/test_integration.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

class TestAnalysisIntegration:
    def setup_method(self):
        """테스트 환경 설정"""
        self.client = TestClient(app)
        self.test_file_path = "test_data/sample_employees.xlsx"
    
    def test_complete_analysis_flow(self):
        """전체 분석 플로우 통합 테스트"""
        # 1. 파일 업로드
        with open(self.test_file_path, "rb") as f:
            upload_response = self.client.post(
                "/api/upload",
                files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # 2. 분석 실행
        analysis_response = self.client.post(f"/api/analysis/{file_id}")
        assert analysis_response.status_code == 200
        
        # 3. 결과 확인
        result_response = self.client.get(f"/api/analysis/{file_id}/result")
        assert result_response.status_code == 200
        
        result = result_response.json()
        assert "analysis_results" in result
        assert len(result["analysis_results"]) > 0
        
        # 4. 결과 다운로드
        download_response = self.client.get(f"/api/download/{file_id}")
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    def test_database_integration(self):
        """데이터베이스 통합 테스트"""
        # 분석 결과 저장 테스트
        from app.db.sqlite_service import SQLiteService
        
        db_service = SQLiteService()
        
        # 테스트 데이터 삽입
        test_result = {
            "file_id": "test_file_123",
            "uid": "EMP001",
            "overall_score": 85.5,
            "grade": "A",
            "confidence": 0.85
        }
        
        result_id = db_service.save_analysis_result(test_result)
        assert result_id is not None
        
        # 저장된 데이터 조회
        saved_result = db_service.get_analysis_result(result_id)
        assert saved_result["overall_score"] == 85.5
        assert saved_result["grade"] == "A"
        
        # 테스트 데이터 정리
        db_service.delete_analysis_result(result_id)
```

#### 🛠️ 통합 테스트 실행
```bash
# 통합 테스트 실행
pytest tests/integration/ -v

# 데이터베이스 포함 테스트
pytest tests/integration/ --db-integration

# 느린 테스트 포함
pytest tests/integration/ -m "not slow"
```

### 3. API 테스트

#### 📝 API 테스트 예시
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIEndpoints:
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_health_check(self):
        """헬스체크 API 테스트"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()
    
    def test_api_info(self):
        """API 정보 엔드포인트 테스트"""
        response = self.client.get("/api")
        
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "features" in data
    
    def test_upload_valid_file(self):
        """유효한 파일 업로드 테스트"""
        test_file_content = b"Name,Opinion\nJohn,Great performance"
        
        response = self.client.post(
            "/api/upload",
            files={"file": ("test.csv", test_file_content, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "message" in data
    
    def test_upload_invalid_file(self):
        """잘못된 파일 업로드 테스트"""
        invalid_content = b"This is not a valid file"
        
        response = self.client.post(
            "/api/upload",
            files={"file": ("test.txt", invalid_content, "text/plain")}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.parametrize("file_id", ["invalid_id", "nonexistent"])
    def test_analysis_invalid_file_id(self, file_id):
        """존재하지 않는 파일 ID로 분석 요청"""
        response = self.client.post(f"/api/analysis/{file_id}")
        assert response.status_code == 404
```

### 4. 성능 테스트

#### 📝 성능 테스트 예시
```python
# tests/test_performance.py
import pytest
import time
import psutil
from app.services.hybrid_analyzer import AIRISSHybridAnalyzer

class TestPerformance:
    def setup_method(self):
        self.analyzer = AIRISSHybridAnalyzer()
    
    def test_analysis_response_time(self):
        """분석 응답시간 테스트"""
        test_data = {
            "uid": "EMP001",
            "opinion": "매우 뛰어난 성과를 달성했습니다" * 10  # 긴 텍스트
        }
        
        start_time = time.time()
        result = self.analyzer.comprehensive_analysis("EMP001", test_data["opinion"], test_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0  # 5초 이내
        assert result["hybrid_analysis"]["overall_score"] > 0
    
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # 대량 데이터 처리 시뮬레이션
        for i in range(100):
            test_data = {
                "uid": f"EMP{i:03d}",
                "opinion": f"직원 {i}의 성과 평가 의견입니다"
            }
            self.analyzer.comprehensive_analysis(f"EMP{i:03d}", test_data["opinion"], test_data)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        assert memory_increase < 500  # 500MB 미만
    
    @pytest.mark.slow
    def test_large_file_processing(self):
        """대용량 파일 처리 테스트"""
        # 1000개 레코드 시뮬레이션
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                "uid": f"EMP{i:04d}",
                "opinion": f"직원 {i}의 상세한 성과 평가 의견입니다. 매우 우수한 성과를 보여주었습니다."
            })
        
        start_time = time.time()
        results = []
        for data in large_dataset:
            result = self.analyzer.comprehensive_analysis(data["uid"], data["opinion"], data)
            results.append(result)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_record = total_time / len(large_dataset)
        
        assert avg_time_per_record < 2.0  # 레코드당 2초 이내
        assert len(results) == 1000
```

### 5. E2E 테스트 (End-to-End)

#### 📝 E2E 테스트 예시 (Selenium)
```python
# tests/test_e2e.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestE2E:
    def setup_method(self):
        """브라우저 설정"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 헤드리스 모드
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("http://localhost:8002")
    
    def teardown_method(self):
        """브라우저 종료"""
        self.driver.quit()
    
    def test_complete_user_journey(self):
        """완전한 사용자 여정 테스트"""
        # 1. 메인 페이지 로딩 확인
        assert "AIRISS" in self.driver.title
        
        # 2. 파일 업로드 버튼 클릭
        upload_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "upload-button"))
        )
        upload_button.click()
        
        # 3. 파일 선택
        file_input = self.driver.find_element(By.INPUT, "type='file'")
        file_input.send_keys("/path/to/test/file.xlsx")
        
        # 4. 분석 시작
        analyze_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "analyze-button"))
        )
        analyze_button.click()
        
        # 5. 결과 대기 및 확인
        results_container = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "analysis-results"))
        )
        
        assert results_container.is_displayed()
        
        # 6. 차트 렌더링 확인
        radar_chart = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "radar-chart"))
        )
        assert radar_chart.is_displayed()
        
        # 7. 다운로드 버튼 확인
        download_button = self.driver.find_element(By.ID, "download-button")
        assert download_button.is_enabled()
```

---

## 🛠️ 테스트 환경 설정

### 테스트 데이터베이스 설정
```python
# conftest.py
import pytest
from app.db.database import create_tables, get_database_info
from app.db.sqlite_service import SQLiteService

@pytest.fixture(scope="session")
def test_db():
    """테스트용 데이터베이스 설정"""
    # 테스트 DB 생성
    test_db_url = "sqlite:///test_airiss.db"
    
    # 테이블 생성
    create_tables()
    
    yield SQLiteService(test_db_url)
    
    # 테스트 후 정리
    import os
    if os.path.exists("test_airiss.db"):
        os.remove("test_airiss.db")

@pytest.fixture(scope="function")
def sample_data():
    """테스트용 샘플 데이터"""
    return {
        "employees": [
            {"uid": "EMP001", "opinion": "뛰어난 성과를 달성했습니다"},
            {"uid": "EMP002", "opinion": "팀워크가 좋고 소통이 원활합니다"},
            {"uid": "EMP003", "opinion": "창의적인 아이디어를 많이 제시합니다"}
        ]
    }
```

### 테스트 설정 파일
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    unit: marks tests as unit tests
```

---

## 📊 테스트 커버리지 관리

### 커버리지 목표
```
✅ 목표 커버리지:
- 전체 코드: 80% 이상
- 핵심 비즈니스 로직: 90% 이상
- API 엔드포인트: 95% 이상
- 유틸리티 함수: 85% 이상
```

### 커버리지 확인 명령어
```bash
# HTML 리포트 생성
pytest --cov=app --cov-report=html

# 터미널에서 간단히 확인
pytest --cov=app --cov-report=term-missing

# 특정 파일만 커버리지 확인
pytest --cov=app.services.hybrid_analyzer --cov-report=term
```

### 커버리지 제외 설정
```python
# .coveragerc
[run]
source = app
omit = 
    */tests/*
    */venv/*
    */migrations/*
    app/main.py  # FastAPI 설정 파일
    
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

---

## 🔄 CI/CD 테스트 자동화

### GitHub Actions 설정
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=app
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
```

---

## 🐛 테스트 디버깅 팁

### 테스트 실패시 디버깅
```bash
# 자세한 출력으로 실행
pytest -v -s tests/test_specific.py

# 특정 테스트만 실행
pytest tests/test_hybrid_analyzer.py::TestHybridAnalyzer::test_specific_function

# 실패한 테스트만 재실행
pytest --lf

# PDB 디버거 사용
pytest --pdb tests/test_specific.py
```

### 테스트 데이터 생성 도구
```python
# tests/utils/data_generator.py
class TestDataGenerator:
    @staticmethod
    def generate_employee_data(count=10):
        """테스트용 직원 데이터 생성"""
        import random
        
        opinions = [
            "매우 뛰어난 성과를 달성했습니다",
            "팀워크가 좋고 협업을 잘합니다", 
            "창의적인 아이디어를 제시합니다",
            "고객 응대가 우수합니다",
            "전문성이 뛰어납니다"
        ]
        
        employees = []
        for i in range(count):
            employees.append({
                "uid": f"EMP{i:03d}",
                "name": f"직원{i}",
                "opinion": random.choice(opinions),
                "department": random.choice(["영업", "개발", "마케팅", "인사"]),
                "position": random.choice(["사원", "대리", "과장", "차장"])
            })
        
        return employees
```

---

## 📈 테스트 메트릭 모니터링

### 테스트 실행 시간 추적
```python
# tests/conftest.py
import time
import pytest

@pytest.fixture(autouse=True)
def measure_test_time(request):
    """각 테스트 실행 시간 측정"""
    start = time.time()
    yield
    duration = time.time() - start
    
    # 3초 이상 걸리는 테스트는 경고
    if duration > 3.0:
        pytest.warn(f"Slow test: {request.node.name} took {duration:.2f}s")
```

### 테스트 안정성 추적
```bash
# 10번 반복 실행으로 안정성 확인
pytest tests/test_critical.py --count=10

# 병렬 실행으로 race condition 확인
pytest tests/ -n 4  # pytest-xdist 필요
```

---

**"좋은 테스트는 버그를 찾는 것이 아니라 예방하는 것입니다!"** 🧪