# AIRISS 코딩 패턴 및 표준

## 🎨 코딩 스타일 가이드

### 네이밍 컨벤션
```python
# 함수명: snake_case
def analyze_employee_performance():
    pass

# 클래스명: PascalCase  
class AIRISSAnalyzer:
    pass

# 상수: UPPER_SNAKE_CASE
MAX_ANALYSIS_TIME = 300

# 변수명: snake_case
employee_data = {}
analysis_result = None
```

### 파일 구조 패턴
```
app/
├── services/           # 비즈니스 로직
│   ├── text_analyzer.py
│   ├── hybrid_analyzer.py
│   └── [new_module].py
├── api/               # API 엔드포인트
│   ├── analysis.py
│   └── v2/
├── templates/         # HTML 템플릿
├── static/           # CSS, JS, 이미지
└── db/              # 데이터베이스 관련
```

## 🔧 표준 코드 패턴

### 1. 분석 서비스 클래스 패턴
```python
import logging
from typing import Dict, Any, Optional, List
import pandas as pd

logger = logging.getLogger(__name__)

class NewAnalysisService:
    """새로운 분석 서비스 표준 템플릿"""
    
    def __init__(self):
        self.config = self._load_config()
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """초기화 메서드 - 무거운 로딩 작업"""
        try:
            # 모델/데이터 로딩
            logger.info("✅ NewAnalysisService 초기화 완료")
            self.is_initialized = True
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {e}")
            self.is_initialized = False
    
    def analyze(self, data: pd.Series) -> Dict[str, Any]:
        """메인 분석 메서드"""
        if not self.is_initialized:
            raise RuntimeError("서비스가 초기화되지 않았습니다")
        
        try:
            # 입력 검증
            self._validate_input(data)
            
            # 분석 수행
            result = self._perform_analysis(data)
            
            # 결과 후처리
            return self._format_result(result)
            
        except Exception as e:
            logger.error(f"분석 중 오류: {e}")
            return self._error_response(str(e))
    
    def _validate_input(self, data: pd.Series):
        """입력 데이터 검증"""
        required_fields = ['uid', 'opinion']
        for field in required_fields:
            if field not in data or pd.isna(data[field]):
                raise ValueError(f"필수 필드 누락: {field}")
    
    def _perform_analysis(self, data: pd.Series) -> Dict:
        """실제 분석 로직 (서브클래스에서 구현)"""
        raise NotImplementedError
    
    def _format_result(self, raw_result: Dict) -> Dict[str, Any]:
        """표준 결과 포맷"""
        return {
            "success": True,
            "timestamp": pd.Timestamp.now().isoformat(),
            "result": raw_result,
            "metadata": {
                "service": self.__class__.__name__,
                "version": "1.0"
            }
        }
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """표준 에러 응답"""
        return {
            "success": False,
            "error": error_msg,
            "timestamp": pd.Timestamp.now().isoformat()
        }
```

### 2. FastAPI 엔드포인트 패턴
```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2", tags=["new_feature"])

@router.post("/new-analysis")
async def new_analysis_endpoint(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """새 분석 API 표준 템플릿"""
    try:
        # 1. 입력 검증
        if not data.get("file_id"):
            raise HTTPException(status_code=400, detail="file_id 필수")
        
        # 2. 비즈니스 로직 처리
        result = await process_analysis(data)
        
        # 3. 백그라운드 작업 등록 (선택사항)
        if data.get("async_mode"):
            background_tasks.add_task(async_post_process, result)
        
        # 4. 표준 응답
        return {
            "status": "success",
            "message": "분석이 완료되었습니다",
            "data": result,
            "request_id": generate_request_id()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

async def process_analysis(data: Dict) -> Dict:
    """비즈니스 로직 분리"""
    # 실제 처리 로직
    pass
```

### 3. 데이터베이스 작업 패턴
```python
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional

class DatabaseManager:
    """데이터베이스 작업 표준 패턴"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """안전한 DB 연결 관리"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 딕셔너리 형태 결과
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """SELECT 쿼리 실행"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """INSERT 쿼리 실행"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """UPDATE/DELETE 쿼리 실행"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
```

### 4. 에러 처리 패턴
```python
import functools
import logging

logger = logging.getLogger(__name__)

def error_handler(fallback_value=None):
    """데코레이터 기반 에러 처리"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{func.__name__} 실행 중 오류: {e}")
                return fallback_value
        return wrapper
    return decorator

# 사용 예시
@error_handler(fallback_value={"score": 0, "error": True})
def risky_analysis_function(data):
    # 위험한 분석 로직
    pass
```

### 5. 비동기 처리 패턴
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any

class AsyncProcessor:
    """비동기 처리 표준 패턴"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(self, items: List[Any], 
                          processor_func: callable) -> List[Any]:
        """배치 비동기 처리"""
        loop = asyncio.get_event_loop()
        
        # CPU 집약적 작업을 스레드풀에서 처리
        tasks = [
            loop.run_in_executor(self.executor, processor_func, item)
            for item in items
        ]
        
        # 모든 작업 완료 대기
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"배치 처리 {i} 실패: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
```

## 📊 데이터 처리 패턴

### 1. DataFrame 검증 패턴
```python
def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """DataFrame 유효성 검사"""
    # 필수 컬럼 확인
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"필수 컬럼 누락: {missing_cols}")
    
    # 빈 DataFrame 확인
    if df.empty:
        raise ValueError("빈 데이터프레임입니다")
    
    # 중복 제거 (선택사항)
    if df.duplicated().any():
        logger.warning("중복 데이터 발견, 제거 진행")
        df = df.drop_duplicates()
    
    return True

# 사용 예시
def process_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    validate_dataframe(df, ['uid', 'name', 'opinion'])
    # 처리 로직
    return df
```

### 2. 안전한 점수 계산 패턴
```python
def safe_score_calculation(value: Any, min_score: float = 0, 
                         max_score: float = 100) -> float:
    """안전한 점수 계산"""
    try:
        # 숫자 변환
        score = float(value) if value is not None else 0
        
        # 범위 제한
        score = max(min_score, min(max_score, score))
        
        # NaN 체크
        if pd.isna(score):
            score = min_score
        
        return round(score, 2)
        
    except (ValueError, TypeError):
        logger.warning(f"점수 계산 실패, 기본값 반환: {value}")
        return min_score
```

## 🎨 프론트엔드 패턴

### 1. Chart.js 표준 설정
```javascript
// 차트 기본 설정 패턴
const standardChartConfig = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom'
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white'
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            max: 100,
            ticks: {
                stepSize: 20
            }
        }
    }
};

// 레이더 차트 생성 함수
function createRadarChart(canvasId, data, labels) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: '점수',
                data: data,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            ...standardChartConfig,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}
```

### 2. WebSocket 통신 패턴
```javascript
class AIRISSWebSocket {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 1000;
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket 연결됨');
                this.reconnectAttempts = 0;
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket 연결 종료');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket 오류:', error);
            };
            
        } catch (error) {
            console.error('WebSocket 연결 실패:', error);
        }
    }
    
    handleMessage(data) {
        // 메시지 타입별 처리
        switch(data.type) {
            case 'progress':
                this.updateProgress(data.progress, data.message);
                break;
            case 'result':
                this.displayResult(data.result);
                break;
            case 'error':
                this.showError(data.error);
                break;
            default:
                console.log('알 수 없는 메시지:', data);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                this.connect();
            }, this.reconnectInterval * this.reconnectAttempts);
        }
    }
}
```

## 🔒 보안 패턴

### 1. 입력 검증 패턴
```python
import re
from typing import Any

def sanitize_input(value: Any, input_type: str = 'text') -> str:
    """입력 데이터 sanitization"""
    if value is None:
        return ""
    
    # 문자열 변환
    value = str(value).strip()
    
    if input_type == 'text':
        # HTML 태그 제거
        value = re.sub(r'<[^>]+>', '', value)
        # 특수 문자 제한
        value = re.sub(r'[<>"\']', '', value)
    
    elif input_type == 'filename':
        # 파일명 안전 문자만 허용
        value = re.sub(r'[^\w\-_\.]', '', value)
    
    # 길이 제한
    max_length = 1000
    if len(value) > max_length:
        value = value[:max_length]
    
    return value
```

### 2. 로깅 패턴
```python
import logging
from datetime import datetime

def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """표준 로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 파일 핸들러
        file_handler = logging.FileHandler(
            f'logs/airiss_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger
```

## 🧪 테스트 패턴

### 1. 단위 테스트 패턴
```python
import unittest
import pandas as pd
from unittest.mock import Mock, patch

class TestAIRISSAnalyzer(unittest.TestCase):
    """표준 테스트 클래스 패턴"""
    
    def setUp(self):
        """테스트 준비"""
        self.analyzer = AIRISSAnalyzer()
        self.sample_data = pd.Series({
            'uid': 'TEST001',
            'opinion': '좋은 성과를 거두었습니다',
            'department': 'IT'
        })
    
    def test_normal_analysis(self):
        """정상 케이스 테스트"""
        result = self.analyzer.analyze(self.sample_data)
        
        self.assertTrue(result['success'])
        self.assertIn('score', result)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)
    
    def test_empty_input(self):
        """비정상 입력 테스트"""
        empty_data = pd.Series({'uid': None, 'opinion': ''})
        
        with self.assertRaises(ValueError):
            self.analyzer.analyze(empty_data)
    
    @patch('app.services.text_analyzer.some_external_api')
    def test_external_api_failure(self, mock_api):
        """외부 API 실패 시나리오"""
        mock_api.side_effect = Exception("API 오류")
        
        result = self.analyzer.analyze(self.sample_data)
        self.assertFalse(result['success'])
        self.assertIn('error', result)
```

---

**"일관된 패턴은 코드의 품질을 높이고 개발 속도를 가속화합니다!"** 🚀