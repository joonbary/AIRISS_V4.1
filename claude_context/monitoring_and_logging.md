# AIRISS 모니터링 및 로깅 가이드

## 📊 모니터링 전략 개요

### 모니터링 레벨
```
Level 1: 시스템 헬스 (서버, DB, 메모리)
Level 2: 애플리케이션 성능 (API 응답시간, 처리량)
Level 3: 비즈니스 메트릭 (분석 성공률, 사용자 만족도)
Level 4: AI 모델 성능 (예측 정확도, 편향 탐지)
```

### 모니터링 도구 스택
```
기본 모니터링: Railway 기본 메트릭
로그 관리: Python logging + 구조화된 로그
실시간 알림: 이메일 + Slack 웹훅 (선택)
대시보드: 자체 제작 모니터링 페이지
```

---

## 🔍 로깅 시스템 설계

### 로그 레벨 정의
```python
# app/core/logging_config.py
import logging
import sys
from datetime import datetime

# 로그 레벨 설정
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,     # 개발시만 사용
    'INFO': logging.INFO,       # 일반 정보 (기본값)
    'WARNING': logging.WARNING, # 주의 필요한 상황
    'ERROR': logging.ERROR,     # 오류 발생
    'CRITICAL': logging.CRITICAL # 시스템 중단 위험
}

# 구조화된 로그 포맷
LOG_FORMAT = {
    'timestamp': '%(asctime)s',
    'level': '%(levelname)s',
    'module': '%(name)s',
    'message': '%(message)s',
    'function': '%(funcName)s',
    'line': '%(lineno)d'
}
```

### 로거 설정
```python
def setup_logger(name: str, level: str = 'INFO'):
    """구조화된 로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(level, logging.INFO))
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 파일 핸들러 (에러 로그)
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    
    # JSON 포맷터 (프로덕션용)
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    return logger

class JSONFormatter(logging.Formatter):
    """JSON 형태의 구조화된 로그 포맷터"""
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.name,
            'message': record.getMessage(),
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 추가 컨텍스트 정보
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
            
        return json.dumps(log_entry, ensure_ascii=False)
```

### 로깅 사용 예시
```python
# app/api/analysis.py
import logging

logger = logging.getLogger(__name__)

@app.post("/api/analyze")
async def analyze_file(file_id: str):
    start_time = time.time()
    
    try:
        logger.info(f"분석 시작", extra={
            'file_id': file_id,
            'request_id': generate_request_id(),
            'user_id': get_current_user_id()
        })
        
        # 분석 로직 실행
        result = await perform_analysis(file_id)
        
        execution_time = time.time() - start_time
        logger.info(f"분석 완료", extra={
            'file_id': file_id,
            'execution_time': execution_time,
            'result_score': result.get('overall_score')
        })
        
        return result
        
    except Exception as e:
        logger.error(f"분석 실패: {str(e)}", extra={
            'file_id': file_id,
            'error_type': type(e).__name__,
            'execution_time': time.time() - start_time
        }, exc_info=True)
        
        raise HTTPException(status_code=500, detail="분석 중 오류 발생")
```

---

## 📈 핵심 메트릭 정의

### 시스템 메트릭
```python
# app/core/metrics.py
import psutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    db_connections: int
    active_requests: int

class MetricsCollector:
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    def collect_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            db_connections=self.get_db_connection_count(),
            active_requests=self.get_active_request_count()
        )
    
    def get_db_connection_count(self) -> int:
        """데이터베이스 연결 수 확인"""
        try:
            conn = sqlite3.connect('airiss.db')
            cursor = conn.execute("PRAGMA database_list")
            return len(cursor.fetchall())
        except:
            return 0
        finally:
            if conn:
                conn.close()
    
    def get_active_request_count(self) -> int:
        """활성 요청 수 (글로벌 카운터 사용)"""
        return getattr(self, '_active_requests', 0)
```

### 애플리케이션 메트릭
```python
@dataclass
class ApplicationMetrics:
    timestamp: datetime
    total_analyses: int
    successful_analyses: int
    failed_analyses: int
    average_response_time: float
    success_rate: float
    
class ApplicationMonitor:
    def __init__(self):
        self.response_times = []
        self.error_counts = {'total': 0, 'by_type': {}}
        
    def record_request(self, endpoint: str, status_code: int, response_time: float):
        """요청 기록"""
        self.response_times.append(response_time)
        
        if status_code >= 400:
            self.error_counts['total'] += 1
            error_type = f"{status_code}x"
            self.error_counts['by_type'][error_type] = \
                self.error_counts['by_type'].get(error_type, 0) + 1
    
    def get_metrics(self) -> ApplicationMetrics:
        """애플리케이션 메트릭 생성"""
        total_requests = len(self.response_times)
        failed_requests = self.error_counts['total']
        successful_requests = total_requests - failed_requests
        
        return ApplicationMetrics(
            timestamp=datetime.now(),
            total_analyses=total_requests,
            successful_analyses=successful_requests,
            failed_analyses=failed_requests,
            average_response_time=sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            success_rate=(successful_requests / total_requests * 100) if total_requests > 0 else 100
        )
```

### AI 모델 메트릭 (v5)
```python
@dataclass
class AIModelMetrics:
    model_name: str
    timestamp: datetime
    inference_time: float
    confidence_score: float
    prediction_accuracy: float
    bias_score: float
    memory_usage: float

class AIModelMonitor:
    def __init__(self):
        self.model_metrics = {}
        
    def record_inference(self, model_name: str, inference_time: float, 
                        confidence: float, memory_usage: float):
        """AI 모델 추론 기록"""
        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = []
            
        metrics = AIModelMetrics(
            model_name=model_name,
            timestamp=datetime.now(),
            inference_time=inference_time,
            confidence_score=confidence,
            prediction_accuracy=0,  # 실제 결과와 비교 후 업데이트
            bias_score=0,  # 편향 분석 결과
            memory_usage=memory_usage
        )
        
        self.model_metrics[model_name].append(metrics)
    
    def calculate_model_performance(self, model_name: str, days: int = 7):
        """모델 성능 통계 계산"""
        recent_metrics = [
            m for m in self.model_metrics.get(model_name, [])
            if (datetime.now() - m.timestamp).days <= days
        ]
        
        if not recent_metrics:
            return None
            
        return {
            'average_inference_time': sum(m.inference_time for m in recent_metrics) / len(recent_metrics),
            'average_confidence': sum(m.confidence_score for m in recent_metrics) / len(recent_metrics),
            'total_inferences': len(recent_metrics),
            'performance_trend': self.calculate_trend(recent_metrics)
        }
```

---

## 🚨 알림 시스템

### 알림 임계값 설정
```python
# app/core/alerting.py
ALERT_THRESHOLDS = {
    'system': {
        'cpu_usage': 80,        # CPU 사용률 80% 초과
        'memory_usage': 85,     # 메모리 사용률 85% 초과
        'disk_usage': 90,       # 디스크 사용률 90% 초과
        'response_time': 10     # 응답시간 10초 초과
    },
    'application': {
        'error_rate': 5,        # 에러율 5% 초과
        'success_rate': 95,     # 성공률 95% 미만
        'queue_size': 100       # 대기열 크기 100개 초과
    },
    'business': {
        'analysis_failure_rate': 10,  # 분석 실패율 10% 초과
        'bias_score': 70,             # 편향 점수 70점 미만
        'user_satisfaction': 3.5      # 사용자 만족도 3.5점 미만
    }
}

class AlertManager:
    def __init__(self):
        self.alert_history = []
        self.cooldown_period = 300  # 5분 쿨다운
        
    def check_alerts(self, metrics: dict):
        """알림 조건 확인"""
        alerts = []
        
        # 시스템 알림 확인
        for metric, threshold in ALERT_THRESHOLDS['system'].items():
            if metrics.get(metric, 0) > threshold:
                alerts.append(self.create_alert('SYSTEM', metric, metrics[metric], threshold))
        
        # 애플리케이션 알림 확인
        for metric, threshold in ALERT_THRESHOLDS['application'].items():
            value = metrics.get(metric, 0)
            if (metric == 'success_rate' and value < threshold) or \
               (metric != 'success_rate' and value > threshold):
                alerts.append(self.create_alert('APPLICATION', metric, value, threshold))
        
        # 중복 알림 방지
        filtered_alerts = self.filter_duplicate_alerts(alerts)
        
        # 알림 전송
        for alert in filtered_alerts:
            self.send_alert(alert)
            
        return filtered_alerts
    
    def create_alert(self, category: str, metric: str, value: float, threshold: float):
        """알림 객체 생성"""
        severity = 'CRITICAL' if value > threshold * 1.5 else 'WARNING'
        
        return {
            'id': f"{category}_{metric}_{int(time.time())}",
            'category': category,
            'metric': metric,
            'value': value,
            'threshold': threshold,
            'severity': severity,
            'timestamp': datetime.now(),
            'message': f"{category} {metric}: {value} (임계값: {threshold})"
        }
    
    def send_alert(self, alert: dict):
        """알림 전송"""
        logger = logging.getLogger(__name__)
        
        # 로그로 기록
        logger.warning(f"ALERT: {alert['message']}", extra={
            'alert_id': alert['id'],
            'category': alert['category'],
            'severity': alert['severity']
        })
        
        # 이메일 전송 (선택사항)
        if alert['severity'] == 'CRITICAL':
            self.send_email_alert(alert)
        
        # Slack 전송 (선택사항)
        self.send_slack_alert(alert)
    
    def send_slack_alert(self, alert: dict):
        """Slack 웹훅 알림"""
        # 실제 구현에서는 Slack 웹훅 URL 설정 필요
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook_url:
            return
            
        color = '#ff0000' if alert['severity'] == 'CRITICAL' else '#ffa500'
        
        payload = {
            'text': f"🚨 AIRISS 알림",
            'attachments': [{
                'color': color,
                'title': f"{alert['severity']}: {alert['metric']}",
                'text': alert['message'],
                'timestamp': int(alert['timestamp'].timestamp())
            }]
        }
        
        try:
            import requests
            requests.post(webhook_url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Slack 알림 전송 실패: {e}")
```

---

## 📊 모니터링 대시보드

### 대시보드 API 엔드포인트
```python
# app/api/monitoring.py
from fastapi import APIRouter, Depends
from app.core.metrics import MetricsCollector, ApplicationMonitor

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

@router.get("/system/metrics")
async def get_system_metrics():
    """시스템 메트릭 조회"""
    collector = MetricsCollector()
    metrics = collector.collect_system_metrics()
    
    return {
        "cpu_usage": metrics.cpu_usage,
        "memory_usage": metrics.memory_usage,
        "disk_usage": metrics.disk_usage,
        "db_connections": metrics.db_connections,
        "timestamp": metrics.timestamp.isoformat()
    }

@router.get("/application/metrics")
async def get_application_metrics():
    """애플리케이션 메트릭 조회"""
    monitor = ApplicationMonitor()
    metrics = monitor.get_metrics()
    
    return {
        "total_analyses": metrics.total_analyses,
        "success_rate": metrics.success_rate,
        "average_response_time": metrics.average_response_time,
        "failed_analyses": metrics.failed_analyses,
        "timestamp": metrics.timestamp.isoformat()
    }

@router.get("/alerts")
async def get_recent_alerts(limit: int = 10):
    """최근 알림 조회"""
    # 실제로는 데이터베이스나 캐시에서 조회
    return {
        "alerts": [],
        "total": 0,
        "active_alerts": 0
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """상세 헬스 체크"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "v4.1",
        "uptime_seconds": (datetime.now() - start_time).total_seconds(),
        "checks": {
            "database": check_database_health(),
            "memory": check_memory_health(),
            "disk": check_disk_health(),
            "external_apis": check_external_apis()
        }
    }
    
    # 전체 상태 결정
    if any(check['status'] == 'unhealthy' for check in health_status['checks'].values()):
        health_status['status'] = 'unhealthy'
    elif any(check['status'] == 'degraded' for check in health_status['checks'].values()):
        health_status['status'] = 'degraded'
    
    return health_status
```

### 모니터링 대시보드 UI
```html
<!-- app/templates/monitoring_dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>AIRISS 모니터링 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 10px;
            min-width: 200px;
        }
        .status-healthy { background-color: #d4edda; }
        .status-warning { background-color: #fff3cd; }
        .status-critical { background-color: #f8d7da; }
    </style>
</head>
<body>
    <h1>🔍 AIRISS 시스템 모니터링</h1>
    
    <!-- 시스템 상태 카드 -->
    <div id="system-metrics" class="metrics-grid">
        <div class="metric-card" id="cpu-card">
            <h3>CPU 사용률</h3>
            <div class="metric-value" id="cpu-value">--</div>
            <div class="metric-chart">
                <canvas id="cpu-chart"></canvas>
            </div>
        </div>
        
        <div class="metric-card" id="memory-card">
            <h3>메모리 사용률</h3>
            <div class="metric-value" id="memory-value">--</div>
            <div class="metric-chart">
                <canvas id="memory-chart"></canvas>
            </div>
        </div>
        
        <div class="metric-card" id="response-card">
            <h3>평균 응답시간</h3>
            <div class="metric-value" id="response-value">--</div>
            <div class="metric-chart">
                <canvas id="response-chart"></canvas>
            </div>
        </div>
        
        <div class="metric-card" id="success-card">
            <h3>성공률</h3>
            <div class="metric-value" id="success-value">--</div>
            <div class="metric-chart">
                <canvas id="success-chart"></canvas>
            </div>
        </div>
    </div>
    
    <!-- 실시간 알림 -->
    <div id="alerts-section">
        <h2>🚨 최근 알림</h2>
        <div id="alerts-list"></div>
    </div>
    
    <!-- 실시간 로그 스트림 -->
    <div id="logs-section">
        <h2>📋 실시간 로그</h2>
        <div id="logs-container" style="height: 300px; overflow-y: scroll; background: #f8f9fa; padding: 10px;">
        </div>
    </div>

    <script>
        // 실시간 메트릭 업데이트
        async function updateMetrics() {
            try {
                const response = await fetch('/api/monitoring/system/metrics');
                const metrics = await response.json();
                
                document.getElementById('cpu-value').textContent = `${metrics.cpu_usage.toFixed(1)}%`;
                document.getElementById('memory-value').textContent = `${metrics.memory_usage.toFixed(1)}%`;
                
                // 상태에 따른 카드 색상 변경
                updateCardStatus('cpu-card', metrics.cpu_usage);
                updateCardStatus('memory-card', metrics.memory_usage);
                
            } catch (error) {
                console.error('메트릭 업데이트 실패:', error);
            }
        }
        
        function updateCardStatus(cardId, value) {
            const card = document.getElementById(cardId);
            card.className = 'metric-card';
            
            if (value > 80) {
                card.classList.add('status-critical');
            } else if (value > 60) {
                card.classList.add('status-warning');
            } else {
                card.classList.add('status-healthy');
            }
        }
        
        // WebSocket으로 실시간 로그 스트리밍
        function setupLogStream() {
            const ws = new WebSocket(`ws://${window.location.host}/ws/logs`);
            const logsContainer = document.getElementById('logs-container');
            
            ws.onmessage = function(event) {
                const logEntry = JSON.parse(event.data);
                const logDiv = document.createElement('div');
                logDiv.innerHTML = `
                    <span style="color: #666;">${logEntry.timestamp}</span>
                    <span style="font-weight: bold; color: ${getLogLevelColor(logEntry.level)};">
                        [${logEntry.level}]
                    </span>
                    <span>${logEntry.message}</span>
                `;
                logsContainer.appendChild(logDiv);
                
                // 자동 스크롤
                logsContainer.scrollTop = logsContainer.scrollHeight;
                
                // 최대 100개 로그만 유지
                while (logsContainer.children.length > 100) {
                    logsContainer.removeChild(logsContainer.firstChild);
                }
            };
        }
        
        function getLogLevelColor(level) {
            const colors = {
                'DEBUG': '#6c757d',
                'INFO': '#17a2b8',
                'WARNING': '#ffc107',
                'ERROR': '#dc3545',
                'CRITICAL': '#721c24'
            };
            return colors[level] || '#000';
        }
        
        // 초기화
        updateMetrics();
        setupLogStream();
        
        // 주기적 업데이트 (30초마다)
        setInterval(updateMetrics, 30000);
    </script>
</body>
</html>
```

---

## 📝 로그 분석 도구

### 로그 분석 스크립트
```python
# scripts/analyze_logs.py
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class LogAnalyzer:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.logs = []
        
    def load_logs(self, hours: int = 24):
        """최근 N시간의 로그 로드"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    log_time = datetime.fromisoformat(log_entry['timestamp'])
                    
                    if log_time >= cutoff_time:
                        self.logs.append(log_entry)
                except:
                    continue
    
    def analyze_error_patterns(self):
        """에러 패턴 분석"""
        error_logs = [log for log in self.logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        # 에러 유형별 분류
        error_types = Counter()
        error_modules = Counter()
        
        for error in error_logs:
            # 에러 메시지에서 패턴 추출
            message = error['message']
            if 'FileNotFoundError' in message:
                error_types['file_not_found'] += 1
            elif 'ConnectionError' in message:
                error_types['connection_error'] += 1
            elif 'ValueError' in message:
                error_types['value_error'] += 1
            else:
                error_types['other'] += 1
                
            error_modules[error['module']] += 1
        
        return {
            'total_errors': len(error_logs),
            'error_types': dict(error_types),
            'error_modules': dict(error_modules),
            'error_rate': len(error_logs) / len(self.logs) * 100 if self.logs else 0
        }
    
    def analyze_performance(self):
        """성능 분석"""
        performance_logs = [
            log for log in self.logs 
            if 'execution_time' in log
        ]
        
        if not performance_logs:
            return {'message': 'No performance data available'}
        
        execution_times = [float(log['execution_time']) for log in performance_logs]
        
        return {
            'total_requests': len(performance_logs),
            'average_time': sum(execution_times) / len(execution_times),
            'max_time': max(execution_times),
            'min_time': min(execution_times),
            'slow_requests': len([t for t in execution_times if t > 5]),
            'percentiles': {
                '50th': sorted(execution_times)[len(execution_times)//2],
                '95th': sorted(execution_times)[int(len(execution_times)*0.95)],
                '99th': sorted(execution_times)[int(len(execution_times)*0.99)]
            }
        }
    
    def generate_report(self):
        """종합 분석 보고서 생성"""
        error_analysis = self.analyze_error_patterns()
        performance_analysis = self.analyze_performance()
        
        return {
            'analysis_period': f"최근 24시간",
            'total_logs': len(self.logs),
            'log_levels': Counter(log['level'] for log in self.logs),
            'errors': error_analysis,
            'performance': performance_analysis,
            'recommendations': self.generate_recommendations(error_analysis, performance_analysis)
        }
    
    def generate_recommendations(self, error_analysis, performance_analysis):
        """개선 권고사항 생성"""
        recommendations = []
        
        if error_analysis['error_rate'] > 5:
            recommendations.append("⚠️ 에러율이 5%를 초과합니다. 즉시 조치가 필요합니다.")
        
        if performance_analysis.get('slow_requests', 0) > 10:
            recommendations.append("🐌 느린 요청이 10개 이상 감지되었습니다. 성능 최적화를 검토하세요.")
        
        if error_analysis['error_types'].get('connection_error', 0) > 5:
            recommendations.append("🔌 연결 오류가 빈번합니다. 외부 서비스 상태를 확인하세요.")
        
        return recommendations

# 사용 예시
if __name__ == "__main__":
    analyzer = LogAnalyzer("logs/application.log")
    analyzer.load_logs(hours=24)
    report = analyzer.generate_report()
    
    print(json.dumps(report, indent=2, ensure_ascii=False))
```

---

## 🔧 모니터링 설정 체크리스트

### 기본 설정
- [ ] 로그 레벨 적절히 설정 (INFO 이상)
- [ ] 로그 로테이션 설정 (일일/크기 기반)
- [ ] 에러 로그 별도 저장
- [ ] 구조화된 로그 포맷 적용

### 메트릭 수집
- [ ] 시스템 리소스 모니터링
- [ ] API 응답시간 추적
- [ ] 에러율 모니터링
- [ ] 비즈니스 메트릭 정의

### 알림 설정
- [ ] 임계값 적절히 설정
- [ ] 알림 채널 구성 (이메일/Slack)
- [ ] 알림 중복 방지 로직
- [ ] 에스컬레이션 절차 수립

### 대시보드
- [ ] 실시간 메트릭 표시
- [ ] 히스토리컬 트렌드 차트
- [ ] 알림 상태 표시
- [ ] 로그 검색 기능

이제 AIRISS 시스템의 완전한 모니터링 및 로깅 체계가 구축되었습니다! 📊✨
