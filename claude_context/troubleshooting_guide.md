# AIRISS 문제 해결 가이드

## 🚨 긴급 상황 대응

### 🔥 Level 1: 즉시 대응 (시스템 다운)
```
증상: 전체 서비스 접근 불가
대응: 즉시 롤백 → 원인 분석 → 핫픽스 배포
```

**일반적 원인 및 해결책:**
1. **서버 크래시**
   ```bash
   # 서버 상태 확인
   ps aux | grep python
   
   # 프로세스 재시작
   cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
   ```

2. **데이터베이스 연결 실패**
   ```python
   # 데이터베이스 파일 확인
   import sqlite3
   try:
       conn = sqlite3.connect('airiss_database.db')
       print("✅ DB 연결 성공")
   except Exception as e:
       print(f"❌ DB 연결 실패: {e}")
   ```

3. **메모리 부족**
   ```bash
   # 메모리 사용량 확인
   tasklist /fi "imagename eq python.exe"
   
   # 메모리 정리 후 재시작
   ```

### ⚡ Level 2: 긴급 대응 (기능 장애)
```
증상: 일부 기능 오작동
대응: 해당 기능 비활성화 → 원인 분석 → 수정 배포
```

## 🔧 일반적인 문제 및 해결책

### 1. 파일 업로드 문제

#### 증상: "파일 업로드 실패" 에러
```python
# 원인 체크리스트
1. 파일 크기 제한 (50MB 초과?)
2. 파일 형식 (CSV/Excel만 허용)
3. 파일 인코딩 (UTF-8 권장)
4. 파일 권한 문제
```

**해결 방법:**
```python
# app/api/analysis.py에서 확인
@router.post("/upload")
async def upload_file(file: UploadFile):
    # 파일 크기 체크 추가
    if file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(400, "파일 크기가 너무 큽니다")
    
    # 파일 형식 체크
    allowed_types = ['.csv', '.xlsx', '.xls']
    if not any(file.filename.endswith(ext) for ext in allowed_types):
        raise HTTPException(400, "지원하지 않는 파일 형식입니다")
```

#### 증상: 한글 파일명 깨짐
```python
# 해결 방법: 파일명 인코딩 처리
import urllib.parse

def safe_filename(filename):
    # 한글 파일명 처리
    safe_name = urllib.parse.quote(filename.encode('utf-8'))
    return safe_name
```

### 2. 분석 결과 오류

#### 증상: "분석 중 오류가 발생했습니다"
```python
# 디버깅 체크리스트
1. 입력 데이터 형식 확인
2. 필수 컬럼 존재 여부 ('uid', 'opinion')
3. 메모리 사용량 확인
4. 로그 파일 확인
```

**해결 방법:**
```python
# app/services/hybrid_analyzer.py 수정
def analyze_employee_data(self, df):
    try:
        # 입력 검증 강화
        if df.empty:
            raise ValueError("빈 데이터프레임입니다")
        
        required_cols = ['uid', 'opinion']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"필수 컬럼 누락: {missing_cols}")
        
        # 분석 진행
        results = []
        for idx, row in df.iterrows():
            try:
                result = self.analyze_single_employee(row)
                results.append(result)
            except Exception as e:
                logger.error(f"직원 {row.get('uid', idx)} 분석 실패: {e}")
                # 기본값으로 처리
                results.append(self.default_result(row))
        
        return results
        
    except Exception as e:
        logger.error(f"분석 전체 실패: {e}")
        raise
```

#### 증상: 점수가 0점 또는 100점만 나옴
```python
# 원인: 점수 계산 로직 오류
# 해결: 점수 정규화 함수 확인

def normalize_score(score, min_val=0, max_val=100):
    """점수 정규화"""
    if pd.isna(score):
        return 50  # 기본값
    
    # 범위 제한
    normalized = max(min_val, min(max_val, float(score)))
    return round(normalized, 2)
```

### 3. 대시보드 표시 문제

#### 증상: 차트가 표시되지 않음
```javascript
// 원인 체크리스트
1. Chart.js 라이브러리 로딩 실패
2. 데이터 형식 오류
3. Canvas 요소 존재하지 않음
4. JavaScript 에러

// 해결 방법
console.log("Chart.js 로딩 확인:", typeof Chart);
console.log("차트 데이터:", chartData);

// 에러 핸들링 추가
try {
    const ctx = document.getElementById('radarChart').getContext('2d');
    if (!ctx) {
        throw new Error("Canvas 요소를 찾을 수 없습니다");
    }
    
    new Chart(ctx, {
        type: 'radar',
        data: chartData,
        options: chartOptions
    });
} catch (error) {
    console.error("차트 생성 실패:", error);
    document.getElementById('chartError').style.display = 'block';
}
```

#### 증상: WebSocket 연결 실패
```javascript
// 원인: 서버 WebSocket 설정 또는 네트워크 문제
// 해결: 재연결 로직 추가

class RobustWebSocket {
    constructor(url) {
        this.url = url;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.connect();
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log("✅ WebSocket 연결됨");
                this.reconnectAttempts = 0;
            };
            
            this.ws.onclose = () => {
                console.log("WebSocket 연결 종료");
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error("WebSocket 오류:", error);
            };
            
        } catch (error) {
            console.error("WebSocket 연결 실패:", error);
            this.attemptReconnect();
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.pow(2, this.reconnectAttempts) * 1000; // 지수 백오프
            setTimeout(() => this.connect(), delay);
        }
    }
}
```

### 4. 성능 관련 문제

#### 증상: 분석 속도 느림 (10초 이상)
```python
# 성능 병목 지점 확인
import time
import cProfile

def performance_analysis():
    """성능 분석 도구"""
    start_time = time.time()
    
    # 각 단계별 시간 측정
    step_times = {}
    
    # 1. 데이터 로딩
    step_start = time.time()
    data = load_data()
    step_times['data_loading'] = time.time() - step_start
    
    # 2. 텍스트 분석
    step_start = time.time()
    text_results = analyze_text(data)
    step_times['text_analysis'] = time.time() - step_start
    
    # 3. 정량 분석
    step_start = time.time()
    quant_results = analyze_quantitative(data)
    step_times['quant_analysis'] = time.time() - step_start
    
    total_time = time.time() - start_time
    
    # 결과 출력
    print(f"총 시간: {total_time:.2f}초")
    for step, duration in step_times.items():
        percentage = (duration / total_time) * 100
        print(f"{step}: {duration:.2f}초 ({percentage:.1f}%)")
```

**최적화 방법:**
```python
# 1. 배치 처리 최적화
def batch_analysis_optimized(df, batch_size=50):
    """배치 단위 처리로 메모리 효율성 향상"""
    results = []
    total_batches = len(df) // batch_size + 1
    
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size]
        batch_results = process_batch(batch_df)
        results.extend(batch_results)
        
        # 진행률 업데이트
        progress = (i // batch_size + 1) / total_batches * 100
        logger.info(f"배치 처리 진행률: {progress:.1f}%")
    
    return results

# 2. 캐싱 적용
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_text_analysis(text_hash):
    """텍스트 분석 결과 캐싱"""
    return expensive_text_analysis(text_hash)
```

#### 증상: 메모리 사용량 과다 (4GB 초과)
```python
# 메모리 사용량 모니터링
import psutil
import gc

def monitor_memory():
    """메모리 사용량 모니터링"""
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    
    if memory_mb > 3000:  # 3GB 초과시 경고
        logger.warning(f"메모리 사용량 높음: {memory_mb:.1f}MB")
        
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        # 메모리 사용량 재확인
        memory_info = process.memory_info()
        memory_mb_after = memory_info.rss / 1024 / 1024
        logger.info(f"GC 후 메모리: {memory_mb_after:.1f}MB")

# 메모리 효율적 데이터 처리
def memory_efficient_processing(df):
    """청크 단위로 데이터 처리"""
    chunk_size = 100
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # 청크별 처리
        process_chunk(chunk)
        
        # 메모리 정리
        del chunk
        gc.collect()
```

### 5. 인코딩 관련 문제

#### 증상: 한글 데이터 깨짐
```python
# CSV 파일 인코딩 자동 감지
import chardet

def detect_encoding(file_path):
    """파일 인코딩 자동 감지"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def read_csv_safe(file_path):
    """안전한 CSV 읽기"""
    # 인코딩 감지
    encoding = detect_encoding(file_path)
    logger.info(f"감지된 인코딩: {encoding}")
    
    try:
        # 감지된 인코딩으로 읽기
        df = pd.read_csv(file_path, encoding=encoding)
        return df
    except UnicodeDecodeError:
        # 폴백: UTF-8로 시도
        logger.warning("인코딩 문제, UTF-8로 재시도")
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            return df
        except UnicodeDecodeError:
            # 최종 폴백: cp949
            logger.warning("UTF-8 실패, cp949로 재시도")
            df = pd.read_csv(file_path, encoding='cp949')
            return df
```

### 6. 의존성 관련 문제

#### 증상: 모듈을 찾을 수 없음 (ModuleNotFoundError)
```bash
# 가상환경 확인
where python
pip list

# 필요한 패키지 재설치
pip install -r requirements.txt

# 또는 개별 설치
pip install fastapi uvicorn pandas scikit-learn matplotlib seaborn
```

#### 증상: 패키지 버전 충돌
```bash
# 버전 충돌 해결
pip install --upgrade pip
pip install --force-reinstall [패키지명]

# 또는 새 가상환경 생성
python -m venv new_venv
new_venv\Scripts\activate
pip install -r requirements.txt
```

## 🔍 디버깅 도구

### 1. 로깅 활용
```python
import logging

# 디버그 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 사용 예시
def debug_analysis_function(data):
    logger.debug(f"입력 데이터: {data.shape}")
    logger.debug(f"데이터 샘플: {data.head()}")
    
    try:
        result = perform_analysis(data)
        logger.debug(f"분석 결과: {result}")
        return result
    except Exception as e:
        logger.error(f"분석 실패: {e}", exc_info=True)
        raise
```

### 2. 성능 프로파일링
```python
import cProfile
import pstats

def profile_analysis():
    """성능 프로파일링"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 분석 함수 실행
    result = run_analysis()
    
    profiler.disable()
    
    # 결과 출력
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 상위 10개 함수
    
    return result
```

### 3. 메모리 프로파일링
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """메모리 사용량 프로파일링"""
    # 함수 실행 시 라인별 메모리 사용량 출력
    large_list = [i for i in range(1000000)]
    del large_list
    return "완료"
```

## 📊 모니터링 대시보드

### 시스템 상태 체크 스크립트
```python
def system_health_check():
    """시스템 상태 종합 체크"""
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "checks": {}
    }
    
    # 1. 서버 응답 확인
    try:
        response = requests.get("http://localhost:8002/health")
        health_status["checks"]["server"] = response.status_code == 200
    except:
        health_status["checks"]["server"] = False
        health_status["status"] = "unhealthy"
    
    # 2. 데이터베이스 연결 확인
    try:
        conn = sqlite3.connect('airiss_database.db')
        cursor = conn.execute("SELECT COUNT(*) FROM analysis_results")
        count = cursor.fetchone()[0]
        health_status["checks"]["database"] = count >= 0
        conn.close()
    except:
        health_status["checks"]["database"] = False
        health_status["status"] = "unhealthy"
    
    # 3. 메모리 사용량 확인
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    health_status["checks"]["memory"] = memory_mb < 4000
    health_status["memory_usage_mb"] = memory_mb
    
    if memory_mb > 4000:
        health_status["status"] = "warning"
    
    # 4. 디스크 공간 확인
    disk_usage = psutil.disk_usage('.')
    free_gb = disk_usage.free / (1024**3)
    health_status["checks"]["disk_space"] = free_gb > 1
    health_status["free_disk_gb"] = free_gb
    
    return health_status
```

## 🆘 긴급 연락처 및 에스컬레이션

### 문제 심각도별 대응
```
🔥 Critical (시스템 다운)
├── 즉시 대응: 개발팀 긴급 연락
├── 1시간 내: 임시 복구 또는 롤백
├── 4시간 내: 근본 원인 파악
└── 24시간 내: 완전 복구 및 재발 방지

⚡ High (주요 기능 장애)
├── 2시간 내: 문제 인지 및 회피 방법 제공
├── 1일 내: 임시 해결책 적용
└── 3일 내: 완전 해결

⚠️ Medium (부분 기능 이상)
├── 1일 내: 문제 확인 및 계획 수립
└── 1주 내: 해결 완료

💡 Low (개선 사항)
└── 다음 스프린트에 포함
```

### 비상 연락망
```
1차: 개발팀 (즉시 대응)
2차: 프로젝트 매니저 (1시간 내)
3차: IT 팀장 (4시간 내)
4차: CTO (24시간 내)
```

## 📚 참고 자료

### 로그 파일 위치
- **애플리케이션 로그**: `logs/airiss_YYYYMMDD.log`
- **에러 로그**: `logs/error_YYYYMMDD.log`
- **성능 로그**: `logs/performance_YYYYMMDD.log`

### 백업 파일 위치
- **코드 백업**: `backups/code_backup_YYYYMMDD.zip`
- **데이터베이스 백업**: `backups/db_backup_YYYYMMDD.db`
- **설정 백업**: `backups/config_backup_YYYYMMDD.zip`

### 유용한 명령어
```bash
# 프로세스 확인
ps aux | grep python

# 포트 사용 확인
netstat -an | grep 8002

# 로그 실시간 확인
tail -f logs/airiss_$(date +%Y%m%d).log

# 메모리 사용량 확인
free -h

# 디스크 사용량 확인
df -h
```

---

**"문제는 피할 수 없지만, 해결책은 언제나 있습니다!"** 🚀