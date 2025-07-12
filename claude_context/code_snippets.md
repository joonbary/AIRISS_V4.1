# AIRISS 재사용 코드 스니펫 모음

## 🎯 사용법 안내

이 파일은 AIRISS 개발에서 자주 사용하는 코드 패턴들을 모아둔 템플릿 라이브러리입니다. 커서AI가 새 기능을 구현할 때 이 스니펫들을 참조하여 일관성 있는 코드를 작성할 수 있습니다.

## 🏗️ 기본 구조 템플릿

### 1. 새 분석 서비스 클래스
```python
import logging
import pandas as pd
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """분석 결과 표준 구조"""
    success: bool
    score: float
    confidence: float
    details: Dict[str, Any]
    timestamp: str
    metadata: Dict[str, Any]

class NewAnalysisService:
    """새 분석 서비스 표준 템플릿"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.is_initialized = False
        self._performance_cache = {}
        self._error_count = 0
        
        # 초기화
        try:
            self._initialize()
            self.is_initialized = True
            logger.info(f"✅ {self.__class__.__name__} 초기화 완료")
        except Exception as e:
            logger.error(f"❌ {self.__class__.__name__} 초기화 실패: {e}")
            self.is_initialized = False
    
    def _initialize(self):
        """무거운 리소스 로딩"""
        # 모델, 데이터, 설정 로딩
        pass
    
    def analyze(self, data: pd.Series) -> AnalysisResult:
        """메인 분석 메서드"""
        if not self.is_initialized:
            return self._error_result("서비스가 초기화되지 않았습니다")
        
        try:
            # 입력 검증
            self._validate_input(data)
            
            # 분석 수행
            score = self._calculate_score(data)
            confidence = self._calculate_confidence(data, score)
            details = self._extract_details(data)
            
            # 성공 결과 반환
            return AnalysisResult(
                success=True,
                score=round(score, 2),
                confidence=round(confidence, 2),
                details=details,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "service": self.__class__.__name__,
                    "version": "1.0",
                    "processing_time": "calculated_time"
                }
            )
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"분석 실패 ({self._error_count}회): {e}")
            return self._error_result(str(e))
    
    def _validate_input(self, data: pd.Series):
        """입력 검증"""
        required_fields = ['uid', 'opinion']
        for field in required_fields:
            if field not in data or pd.isna(data[field]):
                raise ValueError(f"필수 필드 누락: {field}")
        
        # 추가 검증 로직
        if len(str(data.get('opinion', ''))) < 5:
            raise ValueError("의견이 너무 짧습니다 (최소 5자)")
    
    def _calculate_score(self, data: pd.Series) -> float:
        """점수 계산 로직"""
        # 구현 필요
        return 75.0
    
    def _calculate_confidence(self, data: pd.Series, score: float) -> float:
        """신뢰도 계산"""
        base_confidence = 0.8
        # 점수가 극단값일 때 신뢰도 높임
        if score > 90 or score < 30:
            base_confidence += 0.1
        return min(1.0, base_confidence)
    
    def _extract_details(self, data: pd.Series) -> Dict[str, Any]:
        """상세 정보 추출"""
        return {
            "input_length": len(str(data.get('opinion', ''))),
            "department": data.get('department', 'unknown'),
            "analysis_factors": []
        }
    
    def _error_result(self, error_msg: str) -> AnalysisResult:
        """에러 결과 생성"""
        return AnalysisResult(
            success=False,
            score=0.0,
            confidence=0.0,
            details={"error": error_msg},
            timestamp=datetime.now().isoformat(),
            metadata={"service": self.__class__.__name__, "version": "1.0"}
        )
```

### 2. FastAPI 엔드포인트 템플릿
```python
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2", tags=["new_feature"])

class AnalysisRequest(BaseModel):
    """요청 데이터 구조"""
    file_id: str
    options: Optional[Dict[str, Any]] = {}
    async_mode: bool = False

class AnalysisResponse(BaseModel):
    """응답 데이터 구조"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: str
    
@router.post("/new-analysis", response_model=AnalysisResponse)
async def new_analysis_endpoint(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """새 분석 API 템플릿"""
    request_id = generate_request_id()
    
    try:
        # 입력 검증
        validate_request(request)
        
        # 비즈니스 로직
        if request.async_mode:
            # 비동기 처리
            background_tasks.add_task(
                async_analysis_task, 
                request.file_id, 
                request.options,
                request_id
            )
            return AnalysisResponse(
                status="accepted",
                message="분석이 시작되었습니다",
                request_id=request_id
            )
        else:
            # 동기 처리
            result = await sync_analysis_task(request.file_id, request.options)
            return AnalysisResponse(
                status="completed",
                message="분석이 완료되었습니다",
                data=result,
                request_id=request_id
            )
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API 오류 (request_id: {request_id}): {e}")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

def validate_request(request: AnalysisRequest):
    """요청 검증"""
    if not request.file_id:
        raise ValueError("file_id는 필수입니다")
    
    # 추가 검증 로직

def generate_request_id() -> str:
    """요청 ID 생성"""
    import uuid
    return str(uuid.uuid4())[:8]

async def sync_analysis_task(file_id: str, options: Dict) -> Dict:
    """동기 분석 작업"""
    # 구현 로직
    return {"result": "success"}

async def async_analysis_task(file_id: str, options: Dict, request_id: str):
    """비동기 분석 작업"""
    # 백그라운드 처리 로직
    pass
```

### 3. 데이터베이스 처리 템플릿
```python
import sqlite3
import pandas as pd
from contextlib import contextmanager
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """데이터베이스 매니저 템플릿"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()
    
    @contextmanager
    def get_connection(self):
        """안전한 DB 연결"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"DB 오류: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _ensure_tables(self):
        """테이블 생성"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS new_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid TEXT NOT NULL,
                    score REAL NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def save_analysis_result(self, uid: str, score: float, 
                           details: Dict[str, Any]) -> int:
        """분석 결과 저장"""
        import json
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO new_analysis_results (uid, score, details)
                VALUES (?, ?, ?)
            """, (uid, score, json.dumps(details)))
            conn.commit()
            return cursor.lastrowid
    
    def get_analysis_results(self, uid: Optional[str] = None, 
                           limit: int = 100) -> List[Dict]:
        """분석 결과 조회"""
        with self.get_connection() as conn:
            if uid:
                cursor = conn.execute("""
                    SELECT * FROM new_analysis_results 
                    WHERE uid = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (uid, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM new_analysis_results 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 조회"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    AVG(score) as avg_score,
                    MIN(score) as min_score,
                    MAX(score) as max_score
                FROM new_analysis_results
            """)
            
            result = cursor.fetchone()
            return dict(result) if result else {}
```

## 🔧 유틸리티 함수들

### 데이터 처리 유틸리티
```python
import pandas as pd
import numpy as np
from typing import Any, List, Dict, Optional

def safe_convert_to_float(value: Any, default: float = 0.0) -> float:
    """안전한 float 변환"""
    try:
        if pd.isna(value) or value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """점수 정규화"""
    if pd.isna(score):
        return min_val
    return max(min_val, min(max_val, float(score)))

def clean_text(text: Any) -> str:
    """텍스트 정제"""
    if pd.isna(text) or text is None:
        return ""
    
    import re
    text = str(text).strip()
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수 문자 정리
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    
    # 중복 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
    """DataFrame 검증"""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # 빈 DataFrame 확인
    if df.empty:
        validation_result["valid"] = False
        validation_result["errors"].append("빈 데이터프레임입니다")
        return validation_result
    
    # 필수 컬럼 확인
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        validation_result["valid"] = False
        validation_result["errors"].append(f"필수 컬럼 누락: {missing_cols}")
    
    # 중복 데이터 확인
    if df.duplicated().any():
        dup_count = df.duplicated().sum()
        validation_result["warnings"].append(f"중복 데이터 {dup_count}개 발견")
    
    # 빈 값 확인
    for col in required_columns:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                validation_result["warnings"].append(f"{col} 컬럼에 빈 값 {null_count}개")
    
    return validation_result

def create_summary_statistics(scores: List[float]) -> Dict[str, float]:
    """요약 통계 생성"""
    if not scores:
        return {}
    
    scores_array = np.array([s for s in scores if not pd.isna(s)])
    
    if len(scores_array) == 0:
        return {}
    
    return {
        "count": len(scores_array),
        "mean": float(np.mean(scores_array)),
        "median": float(np.median(scores_array)),
        "std": float(np.std(scores_array)),
        "min": float(np.min(scores_array)),
        "max": float(np.max(scores_array)),
        "q25": float(np.percentile(scores_array, 25)),
        "q75": float(np.percentile(scores_array, 75))
    }
```

### 에러 처리 유틸리티
```python
import functools
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """재시도 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} 최종 실패 ({max_attempts}회 시도): {e}")
                        raise
                    else:
                        logger.warning(f"{func.__name__} 실패 (시도 {attempt + 1}/{max_attempts}): {e}")
                        time.sleep(delay)
            
        return wrapper
    return decorator

def safe_execute(func: Callable, fallback_value: Any = None, 
                log_errors: bool = True) -> Any:
    """안전한 함수 실행"""
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"safe_execute 실패: {e}")
        return fallback_value

class ErrorCollector:
    """에러 수집기"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, message: str, context: Optional[Dict] = None):
        """에러 추가"""
        self.errors.append({
            "message": message,
            "context": context or {},
            "timestamp": pd.Timestamp.now().isoformat()
        })
    
    def add_warning(self, message: str, context: Optional[Dict] = None):
        """경고 추가"""
        self.warnings.append({
            "message": message,
            "context": context or {},
            "timestamp": pd.Timestamp.now().isoformat()
        })
    
    def has_errors(self) -> bool:
        """에러 존재 여부"""
        return len(self.errors) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """요약 정보"""
        return {
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        }
```

## 🎨 프론트엔드 스니펫

### Chart.js 차트 생성
```javascript
// 표준 차트 설정
const standardChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                usePointStyle: true,
                padding: 20
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.2)',
            borderWidth: 1
        }
    }
};

// 레이더 차트 생성 함수
function createRadarChart(canvasId, data, labels, title = '역량 분석') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas 요소를 찾을 수 없습니다: ${canvasId}`);
        return null;
    }
    
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            ...standardChartOptions,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: '#666'
                    },
                    grid: {
                        color: '#e0e0e0'
                    },
                    angleLines: {
                        color: '#e0e0e0'
                    }
                }
            }
        }
    });
}

// 게이지 차트 생성 함수
function createGaugeChart(canvasId, value, title = '점수', maxValue = 100) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas 요소를 찾을 수 없습니다: ${canvasId}`);
        return null;
    }
    
    // 색상 결정
    let color;
    if (value >= 80) color = '#4CAF50';      // 녹색
    else if (value >= 60) color = '#FFC107'; // 노란색
    else if (value >= 40) color = '#FF9800'; // 주황색
    else color = '#F44336';                  // 빨간색
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, maxValue - value],
                backgroundColor: [color, '#e0e0e0'],
                borderWidth: 0,
                cutout: '75%'
            }]
        },
        options: {
            ...standardChartOptions,
            rotation: -90,
            circumference: 180,
            plugins: {
                ...standardChartOptions.plugins,
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            id: 'gaugeText',
            beforeDraw: function(chart) {
                const ctx = chart.ctx;
                const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2 + 20;
                
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                
                // 값 표시
                ctx.font = 'bold 24px Arial';
                ctx.fillStyle = color;
                ctx.fillText(Math.round(value), centerX, centerY - 10);
                
                // 제목 표시
                ctx.font = '14px Arial';
                ctx.fillStyle = '#666';
                ctx.fillText(title, centerX, centerY + 15);
            }
        }]
    });
}

// 라인 차트 생성 함수 (시계열)
function createTimeSeriesChart(canvasId, data, labels, title = '트렌드') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas 요소를 찾을 수 없습니다: ${canvasId}`);
        return null;
    }
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...standardChartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45
                    }
                }
            }
        }
    });
}
```

### WebSocket 통신 클래스
```javascript
class AIRISSWebSocket {
    constructor(url, options = {}) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
        this.reconnectInterval = options.reconnectInterval || 1000;
        this.heartbeatInterval = options.heartbeatInterval || 30000;
        this.heartbeatTimer = null;
        
        // 이벤트 핸들러
        this.onOpen = options.onOpen || (() => {});
        this.onMessage = options.onMessage || (() => {});
        this.onClose = options.onClose || (() => {});
        this.onError = options.onError || (() => {});
        
        this.connect();
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = (event) => {
                console.log('✅ WebSocket 연결됨');
                this.reconnectAttempts = 0;
                this.startHeartbeat();
                this.onOpen(event);
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
                this.onMessage(data);
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket 연결 종료');
                this.stopHeartbeat();
                this.onClose(event);
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket 오류:', error);
                this.onError(error);
            };
            
        } catch (error) {
            console.error('WebSocket 연결 실패:', error);
            this.attemptReconnect();
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
            case 'heartbeat':
                // 하트비트 응답
                break;
            default:
                console.log('알 수 없는 메시지 타입:', data.type);
        }
    }
    
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket이 연결되지 않음');
        }
    }
    
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            this.send({ type: 'heartbeat', timestamp: Date.now() });
        }, this.heartbeatInterval);
    }
    
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(
                this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
                30000
            );
            
            console.log(`재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts} (${delay}ms 후)`);
            
            setTimeout(() => {
                this.connect();
            }, delay);
        } else {
            console.error('WebSocket 재연결 포기');
        }
    }
    
    updateProgress(progress, message) {
        // 진행률 업데이트 UI
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) {
            progressBar.style.width = progress + '%';
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        if (progressText) {
            progressText.textContent = message || `${progress}% 완료`;
        }
    }
    
    displayResult(result) {
        // 결과 표시
        console.log('분석 결과:', result);
        // 실제 UI 업데이트 로직
    }
    
    showError(error) {
        // 에러 표시
        console.error('WebSocket 에러:', error);
        // 사용자에게 에러 알림
        this.showNotification(error, 'error');
    }
    
    showNotification(message, type = 'info') {
        // 알림 표시 (Toast, Alert 등)
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    close() {
        this.stopHeartbeat();
        if (this.ws) {
            this.ws.close();
        }
    }
}

// 사용 예시
const wsManager = new AIRISSWebSocket('ws://localhost:8002/ws', {
    onMessage: (data) => {
        console.log('메시지 수신:', data);
    },
    onError: (error) => {
        console.error('연결 오류:', error);
    }
});
```

## 🔐 보안 관련 스니펫

### 입력 검증 및 Sanitization
```python
import re
import html
from typing import Any, Union

def sanitize_text_input(input_text: Any, max_length: int = 1000) -> str:
    """텍스트 입력 sanitization"""
    if not input_text:
        return ""
    
    # 문자열 변환
    text = str(input_text).strip()
    
    # 길이 제한
    if len(text) > max_length:
        text = text[:max_length]
    
    # HTML 엔티티 인코딩
    text = html.escape(text)
    
    # 위험한 패턴 제거
    # Script 태그 관련
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # SQL 인젝션 패턴
    sql_patterns = [
        r'\b(union|select|insert|update|delete|drop|create|alter)\b',
        r'[\'\"]\s*;\s*--',
        r'[\'\"]\s*\|\|',
        r'[\'\"]\s*#'
    ]
    
    for pattern in sql_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text

def validate_file_upload(filename: str, content_type: str, 
                        file_size: int) -> Dict[str, Any]:
    """파일 업로드 검증"""
    validation_result = {
        "valid": True,
        "errors": []
    }
    
    # 파일명 검증
    if not filename:
        validation_result["valid"] = False
        validation_result["errors"].append("파일명이 없습니다")
        return validation_result
    
    # 허용된 확장자 확인
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        validation_result["valid"] = False
        validation_result["errors"].append(f"허용되지 않은 파일 형식: {file_ext}")
    
    # 파일 크기 확인 (50MB 제한)
    max_size = 50 * 1024 * 1024  # 50MB
    if file_size > max_size:
        validation_result["valid"] = False
        validation_result["errors"].append(f"파일 크기 초과: {file_size / 1024 / 1024:.1f}MB (최대 50MB)")
    
    # MIME 타입 확인
    allowed_mime_types = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]
    
    if content_type not in allowed_mime_types:
        validation_result["errors"].append(f"허용되지 않은 MIME 타입: {content_type}")
    
    return validation_result

def hash_sensitive_data(data: str, salt: str = None) -> str:
    """민감한 데이터 해싱"""
    import hashlib
    import secrets
    
    if salt is None:
        salt = secrets.token_hex(16)
    
    # SHA-256 해싱
    hash_obj = hashlib.sha256()
    hash_obj.update((data + salt).encode('utf-8'))
    
    return f"{salt}:{hash_obj.hexdigest()}"
```

## 📊 성능 모니터링 스니펫

### 성능 측정 데코레이터
```python
import time
import functools
import psutil
import logging

logger = logging.getLogger(__name__)

def performance_monitor(log_level=logging.INFO):
    """성능 모니터링 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 시작 시간 및 메모리
            start_time = time.time()
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                # 함수 실행
                result = func(*args, **kwargs)
                
                # 종료 시간 및 메모리
                end_time = time.time()
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                # 성능 정보 로깅
                execution_time = end_time - start_time
                memory_diff = end_memory - start_memory
                
                logger.log(log_level, 
                    f"[PERF] {func.__name__}: "
                    f"시간={execution_time:.3f}s, "
                    f"메모리={memory_diff:+.1f}MB "
                    f"(시작={start_memory:.1f}MB, 종료={end_memory:.1f}MB)"
                )
                
                # 성능 경고
                if execution_time > 5.0:
                    logger.warning(f"{func.__name__} 실행시간이 오래 걸림: {execution_time:.3f}s")
                
                if memory_diff > 100:  # 100MB 이상 증가
                    logger.warning(f"{func.__name__} 메모리 사용량이 크게 증가: +{memory_diff:.1f}MB")
                
                return result
                
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                
                logger.error(
                    f"[PERF-ERROR] {func.__name__}: "
                    f"실패 (시간={execution_time:.3f}s, 오류={str(e)})"
                )
                raise
        
        return wrapper
    return decorator

# 사용 예시
@performance_monitor()
def expensive_analysis_function(data):
    # 시간이 오래 걸리는 분석 함수
    time.sleep(2)  # 시뮬레이션
    return {"result": "success"}
```

---

**"좋은 코드는 복사되고, 훌륭한 코드는 재사용됩니다!"** 🚀