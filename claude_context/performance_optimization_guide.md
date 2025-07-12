# AIRISS 성능 최적화 가이드

## 🎯 성능 목표 및 현재 상태

### 📊 성능 기준 (SLA)
```
응답시간: < 5초 (분석 완료까지)
메모리 사용량: < 4GB (최대)
동시 사용자: 50명
파일 크기: 최대 50MB (2000+ 레코드)
가용성: 99.5% (월 기준)
```

### 📈 현재 성능 수준 (v4.1)
```
✅ 평균 응답시간: 3.2초
✅ 평균 메모리 사용: 2.1GB
✅ 최대 동시 분석: 20개
✅ 최대 처리 레코드: 1500개
⚠️ 대용량 파일에서 메모리 스파이크 발생
```

---

## 🔍 성능 병목 지점 분석

### 1. 텍스트 분석 병목
```python
문제점:
- 텍스트 분석이 CPU 집약적
- 키워드 매칭 알고리즘의 O(n²) 복잡도
- 대량 텍스트 처리 시 메모리 누적

해결책:
- 병렬 처리 도입
- 알고리즘 최적화 (O(n) 목표)
- 배치 처리 및 청킹
```

### 2. 데이터베이스 성능
```sql
문제점:
- 복잡한 조인 쿼리
- 인덱스 부족
- 대량 INSERT 시 속도 저하

해결책:
- 쿼리 최적화
- 적절한 인덱스 추가
- 배치 INSERT 구현
```

### 3. 메모리 관리
```python
문제점:
- 대용량 DataFrame 메모리 상주
- 분석 결과 누적으로 메모리 증가
- 가비지 컬렉션 지연

해결책:
- 스트리밍 처리
- 명시적 메모리 해제
- 메모리 풀링
```

### 4. 파일 I/O 성능
```python
문제점:
- 대용량 Excel 파일 읽기 지연
- 임시 파일 생성 오버헤드
- 디스크 I/O 블로킹

해결책:
- 비동기 파일 처리
- 청킹 읽기
- 메모리 기반 처리
```

---

## 🚀 핵심 최적화 전략

### 1. 배치 처리 최적화

#### Before (현재)
```python
def analyze_file(file_path):
    df = pd.read_excel(file_path)  # 전체 로드
    results = []
    for idx, row in df.iterrows():  # 순차 처리
        result = analyze_single_row(row)
        results.append(result)
    return results
```

#### After (최적화)
```python
def analyze_file_optimized(file_path, chunk_size=100):
    total_rows = count_rows_fast(file_path)
    results = []
    
    # 청킹 처리
    for chunk in pd.read_excel(file_path, chunksize=chunk_size):
        # 병렬 처리
        chunk_results = process_chunk_parallel(chunk)
        results.extend(chunk_results)
        
        # 진행률 업데이트
        progress = len(results) / total_rows * 100
        update_progress(progress)
        
        # 메모리 정리
        gc.collect()
    
    return results
```

### 2. 메모리 효율 개선

#### 메모리 프로파일링 추가
```python
import psutil
import gc
from functools import wraps

def monitor_memory(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process()
        
        # 시작 메모리
        start_memory = process.memory_info().rss / 1024 / 1024
        
        try:
            result = func(*args, **kwargs)
            
            # 종료 메모리
            end_memory = process.memory_info().rss / 1024 / 1024
            memory_used = end_memory - start_memory
            
            # 메모리 사용량 로깅
            logger.info(f"{func.__name__} 메모리 사용: {memory_used:.1f}MB")
            
            # 메모리 정리
            if memory_used > 500:  # 500MB 이상 사용시
                gc.collect()
            
            return result
            
        except MemoryError:
            logger.error(f"{func.__name__} 메모리 부족 오류")
            gc.collect()  # 강제 정리
            raise
    
    return wrapper
```

#### 스트리밍 처리 구현
```python
def streaming_analysis(file_path):
    """대용량 파일을 스트리밍으로 처리"""
    
    def row_generator():
        """행별 제너레이터"""
        for chunk in pd.read_excel(file_path, chunksize=50):
            for _, row in chunk.iterrows():
                yield row
    
    # 스트리밍 처리
    for i, row in enumerate(row_generator()):
        result = analyze_single_row(row)
        
        # 즉시 저장 (메모리에 누적하지 않음)
        save_result_to_db(result)
        
        # 주기적 진행률 업데이트
        if i % 10 == 0:
            update_progress_websocket(i)
```

### 3. 병렬 처리 도입

#### 멀티프로세싱 구현
```python
from multiprocessing import Pool, cpu_count
from concurrent.futures import ProcessPoolExecutor
import threading

def parallel_analysis(df, max_workers=None):
    """CPU 집약적 분석을 병렬 처리"""
    
    if max_workers is None:
        max_workers = min(cpu_count(), 4)  # 최대 4개 프로세스
    
    # 데이터를 청크로 분할
    chunks = split_dataframe(df, max_workers)
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 각 청크를 병렬 처리
        futures = [
            executor.submit(analyze_chunk, chunk) 
            for chunk in chunks
        ]
        
        results = []
        for i, future in enumerate(futures):
            chunk_result = future.result()
            results.extend(chunk_result)
            
            # 진행률 업데이트
            progress = (i + 1) / len(futures) * 100
            update_progress(progress)
    
    return results

def split_dataframe(df, n_chunks):
    """DataFrame을 n개 청크로 분할"""
    chunk_size = len(df) // n_chunks
    chunks = []
    
    for i in range(n_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < n_chunks - 1 else len(df)
        chunks.append(df.iloc[start:end].copy())
    
    return chunks
```

#### 비동기 I/O 처리
```python
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor

async def async_file_analysis(file_path):
    """비동기 파일 분석"""
    
    # 파일 읽기 (별도 스레드)
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        df = await loop.run_in_executor(
            executor, pd.read_excel, file_path
        )
    
    # 분석 작업 (비동기)
    tasks = []
    for _, row in df.iterrows():
        task = asyncio.create_task(analyze_row_async(row))
        tasks.append(task)
    
    # 결과 수집
    results = await asyncio.gather(*tasks)
    return results

async def analyze_row_async(row):
    """개별 행 비동기 분석"""
    # CPU 집약적 작업은 별도 스레드에서
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor, analyze_single_row, row
        )
    return result
```

### 4. 캐싱 시스템

#### LRU 캐시 구현
```python
from functools import lru_cache
import hashlib
import pickle
import redis

class AnalysisCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def get_cache_key(self, text, dimension):
        """캐시 키 생성"""
        content = f"{text}_{dimension}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @lru_cache(maxsize=1000)
    def analyze_with_cache(self, text_hash, dimension):
        """캐시된 분석 결과 반환"""
        return self._analyze_internal(text_hash, dimension)
    
    def get_or_analyze(self, text, dimension):
        """캐시 확인 후 분석"""
        cache_key = self.get_cache_key(text, dimension)
        
        if cache_key in self.cache:
            # 캐시 히트
            self.access_count[cache_key] = self.access_count.get(cache_key, 0) + 1
            return self.cache[cache_key]
        
        # 캐시 미스 - 새로 분석
        result = analyze_text_original(text, dimension)
        
        # 캐시 저장
        self.cache[cache_key] = result
        self.access_count[cache_key] = 1
        
        # 캐시 크기 관리
        if len(self.cache) > self.max_size:
            self._evict_lru()
        
        return result
    
    def _evict_lru(self):
        """LRU 정책으로 캐시 제거"""
        # 가장 적게 사용된 항목 제거
        lru_key = min(self.access_count, key=self.access_count.get)
        del self.cache[lru_key]
        del self.access_count[lru_key]
```

#### Redis 캐싱 (선택사항)
```python
import redis
import json

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.ttl = 3600  # 1시간
    
    def get_cached_result(self, cache_key):
        """Redis에서 캐시된 결과 조회"""
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except:
            pass
        return None
    
    def set_cached_result(self, cache_key, result):
        """Redis에 결과 캐싱"""
        try:
            self.redis_client.setex(
                cache_key, 
                self.ttl, 
                json.dumps(result)
            )
        except:
            pass  # 캐시 실패해도 분석은 계속
```

---

## 📊 데이터베이스 최적화

### 1. 쿼리 최적화

#### 인덱스 추가
```sql
-- 자주 사용되는 쿼리 패턴 분석
-- 1. 파일별 분석 결과 조회
CREATE INDEX idx_analysis_file_id ON analysis_results(file_id);

-- 2. 사용자별 분석 결과 조회  
CREATE INDEX idx_analysis_uid ON analysis_results(uid);

-- 3. 날짜 범위 조회
CREATE INDEX idx_analysis_created_at ON analysis_results(created_at);

-- 4. 점수 범위 조회
CREATE INDEX idx_analysis_score ON analysis_results(overall_score);

-- 5. 복합 인덱스 (파일 + 생성일)
CREATE INDEX idx_analysis_file_date ON analysis_results(file_id, created_at);
```

#### 쿼리 최적화 예시
```python
# Before: N+1 쿼리 문제
def get_analysis_with_files():
    analyses = db.query("SELECT * FROM analysis_results")
    for analysis in analyses:
        file_info = db.query("SELECT filename FROM uploaded_files WHERE id = ?", 
                           analysis['file_id'])
        analysis['filename'] = file_info['filename']
    return analyses

# After: 조인으로 최적화
def get_analysis_with_files_optimized():
    query = """
    SELECT 
        ar.*,
        uf.filename,
        uf.upload_time
    FROM analysis_results ar
    LEFT JOIN uploaded_files uf ON ar.file_id = uf.id
    ORDER BY ar.created_at DESC
    """
    return db.query(query)
```

### 2. 배치 INSERT 최적화

#### 단일 INSERT vs 배치 INSERT
```python
# Before: 개별 INSERT (느림)
def save_results_slow(results):
    for result in results:
        db.execute("""
            INSERT INTO analysis_results (uid, overall_score, grade, ...)
            VALUES (?, ?, ?, ...)
        """, result)

# After: 배치 INSERT (빠름)
def save_results_fast(results):
    values = []
    for result in results:
        values.append((
            result['uid'], 
            result['overall_score'], 
            result['grade'],
            # ...
        ))
    
    # 한 번에 여러 레코드 INSERT
    db.executemany("""
        INSERT INTO analysis_results (uid, overall_score, grade, ...)
        VALUES (?, ?, ?, ...)
    """, values)
```

---

## ⚡ 프론트엔드 성능 최적화

### 1. React 컴포넌트 최적화

#### 메모이제이션 적용
```javascript
// Before: 매번 리렌더링
function AnalysisChart({ data }) {
    const chartConfig = {
        type: 'radar',
        data: processChartData(data),  // 매번 실행
        options: getChartOptions()     // 매번 실행
    };
    
    return <Chart {...chartConfig} />;
}

// After: 메모이제이션
import { useMemo, memo } from 'react';

const AnalysisChart = memo(({ data }) => {
    const chartConfig = useMemo(() => ({
        type: 'radar',
        data: processChartData(data),
        options: getChartOptions()
    }), [data]);  // data가 변경될 때만 재계산
    
    return <Chart {...chartConfig} />;
});
```

#### 가상화 (Virtualization)
```javascript
// 대량 데이터 리스트 가상화
import { FixedSizeList as List } from 'react-window';

function LargeDataList({ items }) {
    const Row = ({ index, style }) => (
        <div style={style}>
            <AnalysisResultItem data={items[index]} />
        </div>
    );
    
    return (
        <List
            height={600}
            itemCount={items.length}
            itemSize={80}
            width={800}
        >
            {Row}
        </List>
    );
}
```

### 2. Chart.js 성능 최적화

#### 애니메이션 및 렌더링 최적화
```javascript
// 대용량 데이터용 차트 설정
const optimizedChartOptions = {
    responsive: true,
    animation: {
        duration: 0  // 애니메이션 비활성화
    },
    elements: {
        point: {
            radius: 2  // 포인트 크기 축소
        }
    },
    scales: {
        x: {
            ticks: {
                maxTicksLimit: 10  // 틱 개수 제한
            }
        }
    },
    plugins: {
        legend: {
            display: false  // 불필요한 레전드 숨김
        }
    }
};
```

### 3. API 호출 최적화

#### 요청 디바운싱
```javascript
import { debounce } from 'lodash';

// 검색 입력 디바운싱
const debouncedSearch = useMemo(
    () => debounce((query) => {
        searchAnalysisResults(query);
    }, 300),
    []
);

function SearchBox() {
    const [query, setQuery] = useState('');
    
    useEffect(() => {
        if (query) {
            debouncedSearch(query);
        }
    }, [query, debouncedSearch]);
    
    return (
        <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="검색..."
        />
    );
}
```

#### 요청 배치화
```javascript
// 개별 요청 대신 배치 요청
class APIBatcher {
    constructor() {
        this.pendingRequests = [];
        this.batchTimeout = null;
    }
    
    addRequest(endpoint, params) {
        return new Promise((resolve, reject) => {
            this.pendingRequests.push({ endpoint, params, resolve, reject });
            
            if (!this.batchTimeout) {
                this.batchTimeout = setTimeout(() => {
                    this.processBatch();
                }, 50);
            }
        });
    }
    
    async processBatch() {
        const requests = [...this.pendingRequests];
        this.pendingRequests = [];
        this.batchTimeout = null;
        
        try {
            const response = await fetch('/api/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ requests })
            });
            
            const results = await response.json();
            
            requests.forEach((req, index) => {
                req.resolve(results[index]);
            });
        } catch (error) {
            requests.forEach(req => req.reject(error));
        }
    }
}
```

---

## 📈 성능 모니터링

### 1. 실시간 성능 메트릭

#### 성능 측정 미들웨어
```python
import time
from functools import wraps

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def track_performance(self, func_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = func(*args, **kwargs)
                    status = 'success'
                except Exception as e:
                    status = 'error'
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    
                    # 메트릭 수집
                    execution_time = end_time - start_time
                    memory_delta = (end_memory - start_memory) / 1024 / 1024
                    
                    self.record_metric(func_name, {
                        'execution_time': execution_time,
                        'memory_delta': memory_delta,
                        'status': status,
                        'timestamp': end_time
                    })
                
                return result
            return wrapper
        return decorator
    
    def record_metric(self, func_name, metric):
        if func_name not in self.metrics:
            self.metrics[func_name] = []
        
        self.metrics[func_name].append(metric)
        
        # 최근 100개 항목만 유지
        if len(self.metrics[func_name]) > 100:
            self.metrics[func_name] = self.metrics[func_name][-100:]
    
    def get_performance_report(self):
        report = {}
        for func_name, metrics in self.metrics.items():
            if not metrics:
                continue
                
            execution_times = [m['execution_time'] for m in metrics]
            memory_deltas = [m['memory_delta'] for m in metrics]
            
            report[func_name] = {
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'max_execution_time': max(execution_times),
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'max_memory_delta': max(memory_deltas),
                'call_count': len(metrics),
                'error_rate': len([m for m in metrics if m['status'] == 'error']) / len(metrics)
            }
        
        return report

# 전역 모니터 인스턴스
performance_monitor = PerformanceMonitor()
```

#### 사용 예시
```python
from app.utils.performance_monitor import performance_monitor

@performance_monitor.track_performance('text_analysis')
def analyze_text_with_monitoring(text, dimension):
    return analyze_text_original(text, dimension)

@performance_monitor.track_performance('file_analysis')
def analyze_file_with_monitoring(file_path):
    return analyze_file_original(file_path)
```

### 2. 알림 시스템

#### 성능 임계값 모니터링
```python
class PerformanceAlert:
    def __init__(self):
        self.thresholds = {
            'response_time': 10.0,      # 10초 이상
            'memory_usage': 3000.0,     # 3GB 이상  
            'error_rate': 0.05,         # 5% 이상
            'queue_length': 50          # 대기열 50개 이상
        }
        
        self.alert_cooldown = {}
        self.cooldown_duration = 300  # 5분
    
    def check_thresholds(self, metrics):
        current_time = time.time()
        
        for metric_name, value in metrics.items():
            threshold = self.thresholds.get(metric_name)
            if not threshold:
                continue
            
            # 임계값 초과 확인
            if value > threshold:
                # 쿨다운 확인
                last_alert = self.alert_cooldown.get(metric_name, 0)
                if current_time - last_alert > self.cooldown_duration:
                    self.send_alert(metric_name, value, threshold)
                    self.alert_cooldown[metric_name] = current_time
    
    def send_alert(self, metric_name, value, threshold):
        message = f"성능 임계값 초과: {metric_name} = {value:.2f} (임계값: {threshold})"
        
        # 로그 기록
        logger.warning(message)
        
        # WebSocket 알림
        websocket_manager.broadcast({
            'type': 'performance_alert',
            'metric': metric_name,
            'value': value,
            'threshold': threshold,
            'message': message
        })
        
        # 이메일/슬랙 알림 (선택사항)
        # send_slack_notification(message)
```

---

## 🛠️ 성능 최적화 도구

### 1. 프로파일링 도구

#### Python 프로파일러
```python
import cProfile
import pstats
from pstats import SortKey

def profile_function(func):
    """함수 프로파일링"""
    pr = cProfile.Profile()
    pr.enable()
    
    result = func()
    
    pr.disable()
    
    # 결과 분석
    stats = pstats.Stats(pr)
    stats.sort_stats(SortKey.TIME)
    stats.print_stats(20)  # 상위 20개 함수
    
    return result

# 사용 예시
def profile_analysis():
    return profile_function(lambda: analyze_file("test_data/large.xlsx"))
```

#### 메모리 프로파일러
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # 메모리 사용량 라인별 분석
    large_data = pd.read_excel("large_file.xlsx")
    processed = process_data(large_data)
    result = analyze_data(processed)
    return result

# 명령행에서 실행: python -m memory_profiler script.py
```

### 2. 벤치마킹 스크립트

#### 성능 벤치마크
```python
import time
import statistics
import psutil

class PerformanceBenchmark:
    def __init__(self):
        self.results = {}
    
    def benchmark_function(self, func, name, iterations=10):
        """함수 성능 벤치마크"""
        times = []
        memory_usage = []
        
        for i in range(iterations):
            # 메모리 정리
            gc.collect()
            start_memory = psutil.Process().memory_info().rss
            
            # 실행 시간 측정
            start_time = time.time()
            result = func()
            end_time = time.time()
            
            # 메모리 사용량
            end_memory = psutil.Process().memory_info().rss
            
            times.append(end_time - start_time)
            memory_usage.append((end_memory - start_memory) / 1024 / 1024)
        
        # 통계 계산
        self.results[name] = {
            'avg_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_time': statistics.stdev(times) if len(times) > 1 else 0,
            'avg_memory': statistics.mean(memory_usage),
            'max_memory': max(memory_usage)
        }
        
        return self.results[name]
    
    def compare_functions(self, functions, iterations=10):
        """여러 함수 성능 비교"""
        for name, func in functions.items():
            print(f"\n벤치마킹: {name}")
            result = self.benchmark_function(func, name, iterations)
            
            print(f"평균 시간: {result['avg_time']:.3f}초")
            print(f"메모리 사용: {result['avg_memory']:.1f}MB")
    
    def generate_report(self):
        """성능 리포트 생성"""
        report = []
        report.append("=" * 60)
        report.append("AIRISS 성능 벤치마크 리포트")
        report.append("=" * 60)
        
        for name, stats in self.results.items():
            report.append(f"\n{name}:")
            report.append(f"  평균 실행시간: {stats['avg_time']:.3f}초")
            report.append(f"  최소/최대 시간: {stats['min_time']:.3f}초 / {stats['max_time']:.3f}초")
            report.append(f"  표준편차: {stats['std_time']:.3f}초")
            report.append(f"  평균 메모리: {stats['avg_memory']:.1f}MB")
            report.append(f"  최대 메모리: {stats['max_memory']:.1f}MB")
        
        return "\n".join(report)

# 사용 예시
benchmark = PerformanceBenchmark()

functions_to_test = {
    'current_analysis': lambda: analyze_file("test_data/medium.xlsx"),
    'optimized_analysis': lambda: analyze_file_optimized("test_data/medium.xlsx"),
    'parallel_analysis': lambda: analyze_file_parallel("test_data/medium.xlsx")
}

benchmark.compare_functions(functions_to_test)
print(benchmark.generate_report())
```

---

## 🎯 최적화 로드맵

### Phase 1: 즉시 적용 가능 (1-2주)
```
✅ 메모리 모니터링 추가
✅ 배치 INSERT 최적화
✅ 기본 캐싱 구현
✅ 데이터베이스 인덱스 추가
✅ 프론트엔드 메모이제이션
```

### Phase 2: 중기 최적화 (1개월)
```
🔄 병렬 처리 도입
🔄 스트리밍 처리 구현
🔄 Redis 캐싱 시스템
🔄 비동기 I/O 최적화
🔄 성능 모니터링 대시보드
```

### Phase 3: 고급 최적화 (2-3개월)
```
🚀 마이크로서비스 아키텍처
🚀 분산 처리 시스템
🚀 GPU 가속 (선택사항)
🚀 CDN 적용
🚀 오토스케일링
```

---

## 📊 성능 최적화 효과 예측

### 메모리 사용량 개선
```
Before: 평균 2.1GB, 최대 4.2GB
After:  평균 1.4GB, 최대 2.8GB
개선률: 33% 감소
```

### 응답시간 개선
```
Before: 평균 3.2초, 최대 8.5초
After:  평균 2.1초, 최대 4.2초  
개선률: 34% 단축
```

### 처리량 개선
```
Before: 1500개 레코드 최대
After:  3000개 레코드 최대
개선률: 100% 증가
```

### 동시 처리 개선
```
Before: 20개 동시 분석
After:  50개 동시 분석
개선률: 150% 증가
```

---

**"성능 최적화는 사용자 경험의 핵심입니다!"** ⚡

## 🎪 실무 적용 가이드

### 1. 단계별 적용 순서
```
1일차: 메모리 모니터링 추가
2일차: 데이터베이스 인덱스 추가  
3일차: 기본 캐싱 구현
1주차: 배치 처리 최적화
2주차: 병렬 처리 도입
1개월: 성능 모니터링 시스템 완성
```

### 2. 성과 측정 방법
```python
# 성능 개선 전후 비교
def measure_improvement():
    # Before 측정
    before_metrics = benchmark_current_system()
    
    # 최적화 적용
    apply_optimizations()
    
    # After 측정  
    after_metrics = benchmark_optimized_system()
    
    # 개선률 계산
    improvement = calculate_improvement_rate(before_metrics, after_metrics)
    
    return improvement
```

### 3. 회귀 방지
```python
# 성능 회귀 테스트
def performance_regression_test():
    current_metrics = get_current_performance()
    baseline_metrics = load_baseline_performance()
    
    regression_detected = []
    
    for metric in ['response_time', 'memory_usage', 'throughput']:
        if current_metrics[metric] > baseline_metrics[metric] * 1.1:  # 10% 이상 악화
            regression_detected.append(metric)
    
    if regression_detected:
        send_regression_alert(regression_detected)
    
    return len(regression_detected) == 0
```