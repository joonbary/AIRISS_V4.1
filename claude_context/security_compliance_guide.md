# AIRISS 보안 및 컴플라이언스 가이드

## 🛡️ 보안 아키텍처 개요

### 다층 보안 모델
```
사용자 브라우저
    ↓ HTTPS/TLS 1.3
웹 애플리케이션 방화벽 (WAF)
    ↓ 인증/인가
FastAPI 애플리케이션 서버
    ↓ 데이터 암호화
PostgreSQL 데이터베이스
    ↓ 백업 암호화
클라우드 저장소 (Railway)
```

### 핵심 보안 원칙
1. **Zero Trust**: 모든 접근을 검증
2. **Defense in Depth**: 다층 방어
3. **Principle of Least Privilege**: 최소 권한 원칙
4. **Data Classification**: 데이터 분류 및 보호
5. **Continuous Monitoring**: 지속적 모니터링

---

## 🔐 인증 및 접근 제어

### 사용자 인증 체계
```python
# app/auth/authentication.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets

class AuthenticationService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱 (bcrypt 사용)"""
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        import bcrypt
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    
    def create_access_token(self, data: dict) -> str:
        """JWT 액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """JWT 리프레시 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """토큰 검증 및 페이로드 추출"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

# 인증 의존성
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 정보 추출"""
    auth_service = AuthenticationService()
    payload = auth_service.verify_token(credentials.credentials)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")
    
    # 데이터베이스에서 사용자 정보 조회
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
    
    return user
```

### 역할 기반 접근 제어 (RBAC)
```python
# app/auth/authorization.py
from enum import Enum
from functools import wraps

class Permission(Enum):
    READ_ANALYSIS = "read_analysis"
    CREATE_ANALYSIS = "create_analysis"
    DELETE_ANALYSIS = "delete_analysis"
    MANAGE_USERS = "manage_users"
    ADMIN_ACCESS = "admin_access"
    BIAS_CHECK = "bias_check"
    EXPORT_DATA = "export_data"

class Role(Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    MANAGER = "manager"
    ADMIN = "admin"

# 역할별 권한 매트릭스
ROLE_PERMISSIONS = {
    Role.VIEWER: [
        Permission.READ_ANALYSIS
    ],
    Role.ANALYST: [
        Permission.READ_ANALYSIS,
        Permission.CREATE_ANALYSIS,
        Permission.BIAS_CHECK
    ],
    Role.MANAGER: [
        Permission.READ_ANALYSIS,
        Permission.CREATE_ANALYSIS,
        Permission.DELETE_ANALYSIS,
        Permission.BIAS_CHECK,
        Permission.EXPORT_DATA
    ],
    Role.ADMIN: [
        Permission.READ_ANALYSIS,
        Permission.CREATE_ANALYSIS,
        Permission.DELETE_ANALYSIS,
        Permission.MANAGE_USERS,
        Permission.ADMIN_ACCESS,
        Permission.BIAS_CHECK,
        Permission.EXPORT_DATA
    ]
}

def require_permission(permission: Permission):
    """권한 확인 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="인증이 필요합니다")
            
            user_role = Role(current_user.role)
            user_permissions = ROLE_PERMISSIONS.get(user_role, [])
            
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403, 
                    detail=f"'{permission.value}' 권한이 필요합니다"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 사용 예시
@router.delete("/analysis/{analysis_id}")
@require_permission(Permission.DELETE_ANALYSIS)
async def delete_analysis(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    # 분석 삭제 로직
    pass
```

---

## 🔒 데이터 보호

### 데이터 암호화
```python
# app/security/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self):
        self.salt = os.getenv("ENCRYPTION_SALT", b"default_salt_change_me")
        self.password = os.getenv("ENCRYPTION_PASSWORD", "default_password")
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """암호화 키 생성"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt.encode() if isinstance(self.salt, str) else self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """데이터 암호화"""
        if not data:
            return data
        
        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """데이터 복호화"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("복호화에 실패했습니다")

# 민감한 데이터 자동 암호화
class EncryptedField:
    def __init__(self, encryptor: DataEncryption):
        self.encryptor = encryptor
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        encrypted_value = getattr(obj, self.private_name, None)
        if encrypted_value:
            return self.encryptor.decrypt(encrypted_value)
        return None
    
    def __set__(self, obj, value):
        if value:
            encrypted_value = self.encryptor.encrypt(value)
            setattr(obj, self.private_name, encrypted_value)
        else:
            setattr(obj, self.private_name, None)

# 사용 예시
class UserModel:
    def __init__(self):
        self.encryptor = DataEncryption()
        
    # 민감한 필드들 암호화
    personal_info = EncryptedField(encryptor)
    phone_number = EncryptedField(encryptor)
    
    def to_dict_safe(self):
        """민감한 정보 마스킹하여 반환"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "phone_number": self.mask_phone(self.phone_number) if self.phone_number else None
        }
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """전화번호 마스킹"""
        if len(phone) >= 8:
            return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]
        return "*" * len(phone)
```

### 데이터베이스 보안
```python
# app/db/secure_database.py
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
import logging

class SecureDatabase:
    def __init__(self, database_url: str):
        # SSL 강제 및 연결 보안 설정
        if "postgresql" in database_url:
            if "sslmode" not in database_url:
                database_url += "?sslmode=require"
        
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,  # 연결 상태 확인
            pool_recycle=3600,   # 1시간마다 연결 재생성
            echo=False,          # SQL 로깅 비활성화 (운영환경)
            connect_args={
                "sslmode": "require",
                "connect_timeout": 10,
                "application_name": "AIRISS_v4"
            } if "postgresql" in database_url else {}
        )
        
        # 데이터베이스 이벤트 리스너 등록
        self._register_security_events()
    
    def _register_security_events(self):
        """보안 관련 이벤트 리스너 등록"""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """SQLite 보안 설정"""
            if "sqlite" in str(self.engine.url):
                with dbapi_connection.cursor() as cursor:
                    # 외래 키 제약 조건 활성화
                    cursor.execute("PRAGMA foreign_keys=ON")
                    # 보안 모드 활성화
                    cursor.execute("PRAGMA secure_delete=ON")
                    # 로그 모드로 WAL 설정
                    cursor.execute("PRAGMA journal_mode=WAL")
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def log_sql_queries(conn, cursor, statement, parameters, context, executemany):
            """SQL 쿼리 로깅 (개발환경에서만)"""
            if os.getenv("ENVIRONMENT") == "development":
                logger.debug(f"SQL Query: {statement}")
                if parameters:
                    logger.debug(f"Parameters: {parameters}")

# SQL Injection 방지
class SafeQueryBuilder:
    @staticmethod
    def build_where_clause(filters: dict) -> tuple:
        """안전한 WHERE 절 생성"""
        where_parts = []
        params = {}
        
        for key, value in filters.items():
            # 허용된 컬럼명만 사용
            safe_key = SafeQueryBuilder.validate_column_name(key)
            param_key = f"param_{len(params)}"
            
            where_parts.append(f"{safe_key} = :{param_key}")
            params[param_key] = value
        
        where_clause = " AND ".join(where_parts) if where_parts else "1=1"
        return where_clause, params
    
    @staticmethod
    def validate_column_name(column_name: str) -> str:
        """컬럼명 검증"""
        allowed_columns = [
            "id", "name", "role", "created_at", "updated_at",
            "file_id", "uid", "overall_score", "grade", "confidence"
        ]
        
        if column_name not in allowed_columns:
            raise ValueError(f"허용되지 않은 컬럼명: {column_name}")
        
        return column_name
```

---

## 🛡️ 입력 검증 및 출력 보안

### 입력 데이터 검증
```python
# app/security/validation.py
from pydantic import BaseModel, validator, constr
from typing import Optional, List
import re
import bleach

class SecureBaseModel(BaseModel):
    """보안이 강화된 기본 모델"""
    
    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        """문자열 입력 정화"""
        if isinstance(v, str):
            # HTML 태그 제거
            v = bleach.clean(v, tags=[], attributes={}, strip=True)
            # 제어 문자 제거
            v = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', v)
            # 과도한 공백 제거
            v = ' '.join(v.split())
        return v

class FileUploadRequest(SecureBaseModel):
    """파일 업로드 요청 검증"""
    filename: constr(min_length=1, max_length=255, regex=r'^[a-zA-Z0-9._-]+$')
    file_size: int
    content_type: str
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 50 * 1024 * 1024  # 50MB
        if v > max_size:
            raise ValueError(f'파일 크기가 {max_size} 바이트를 초과할 수 없습니다')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = [
            'text/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ]
        if v not in allowed_types:
            raise ValueError('허용되지 않은 파일 형식입니다')
        return v

class AnalysisRequest(SecureBaseModel):
    """분석 요청 검증"""
    file_id: constr(min_length=1, max_length=100, regex=r'^[a-zA-Z0-9_-]+$')
    options: Optional[dict] = {}
    
    @validator('options')
    def validate_options(cls, v):
        # 허용된 옵션만 허용
        allowed_keys = ['bias_check', 'include_predictions', 'export_format']
        filtered_options = {k: v for k, v in v.items() if k in allowed_keys}
        return filtered_options

# 파일 내용 검증
class FileContentValidator:
    @staticmethod
    def validate_csv_content(file_content: bytes) -> bool:
        """CSV 파일 내용 검증"""
        try:
            import pandas as pd
            import io
            
            # 파일 크기 확인
            if len(file_content) > 50 * 1024 * 1024:  # 50MB
                return False
            
            # CSV 파싱 시도
            df = pd.read_csv(io.BytesIO(file_content))
            
            # 최대 행 수 제한
            if len(df) > 10000:
                return False
            
            # 필수 컬럼 확인
            required_columns = ['uid', 'opinion']
            if not all(col in df.columns for col in required_columns):
                return False
            
            # 데이터 타입 검증
            for col in df.columns:
                if df[col].dtype == 'object':
                    # 문자열 길이 제한
                    max_length = df[col].astype(str).str.len().max()
                    if max_length > 10000:  # 10KB per cell
                        return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def scan_for_malicious_content(content: str) -> bool:
        """악성 콘텐츠 검사"""
        # 스크립트 태그 검사
        script_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return True
        
        # SQL Injection 패턴 검사
        sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.*set',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
```

### 출력 데이터 보안
```python
# app/security/output_security.py
import json
from typing import Any, Dict, List

class SecureResponseFormatter:
    """보안이 강화된 응답 포맷터"""
    
    @staticmethod
    def sanitize_response(data: Any) -> Any:
        """응답 데이터 정화"""
        if isinstance(data, dict):
            return {k: SecureResponseFormatter.sanitize_response(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [SecureResponseFormatter.sanitize_response(item) for item in data]
        elif isinstance(data, str):
            # 잠재적으로 위험한 문자 이스케이프
            return data.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        else:
            return data
    
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """민감한 데이터 마스킹"""
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data:
                value = masked_data[field]
                if isinstance(value, str) and value:
                    if len(value) > 6:
                        masked_data[field] = value[:2] + '*' * (len(value) - 4) + value[-2:]
                    else:
                        masked_data[field] = '*' * len(value)
                elif value:
                    masked_data[field] = '[MASKED]'
        
        return masked_data
    
    @staticmethod
    def safe_json_encode(obj: Any) -> str:
        """안전한 JSON 인코딩"""
        try:
            return json.dumps(obj, ensure_ascii=True, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encoding failed: {e}")
            return json.dumps({"error": "데이터 인코딩 오류"})

# 응답 헤더 보안
class SecurityHeaders:
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """보안 헤더 설정"""
        return {
            # XSS 보호
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # HTTPS 강제
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # 콘텐츠 보안 정책
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' wss: ws:;"
            ),
            
            # 추천 정책
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # 권한 정책
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }
```

---

## 🔍 로깅 및 모니터링

### 보안 이벤트 로깅
```python
# app/security/security_logger.py
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class SecurityEventType(Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    FILE_UPLOAD = "file_upload"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_ERROR = "system_error"

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        # 보안 로그 전용 핸들러
        handler = logging.FileHandler("logs/security.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """보안 이벤트 로깅"""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(event_data, ensure_ascii=False))
        
        # 중요한 보안 이벤트는 즉시 알림
        if event_type in [SecurityEventType.UNAUTHORIZED_ACCESS, SecurityEventType.SUSPICIOUS_ACTIVITY]:
            self._send_security_alert(event_data)
    
    def _send_security_alert(self, event_data: Dict[str, Any]):
        """보안 경고 알림"""
        # 이메일, 슬랙, SMS 등으로 알림 발송
        # 실제 구현에서는 알림 서비스 연동
        logger.warning(f"SECURITY ALERT: {json.dumps(event_data)}")

# 보안 데코레이터
def log_security_event(event_type: SecurityEventType):
    """보안 이벤트 로깅 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            current_user = kwargs.get('current_user')
            
            try:
                result = await func(*args, **kwargs)
                
                # 성공 이벤트 로깅
                SecurityLogger().log_security_event(
                    event_type=event_type,
                    user_id=current_user.id if current_user else None,
                    ip_address=request.client.host if request else None,
                    user_agent=request.headers.get("user-agent") if request else None,
                    details={"success": True}
                )
                
                return result
                
            except Exception as e:
                # 실패 이벤트 로깅
                SecurityLogger().log_security_event(
                    event_type=SecurityEventType.SYSTEM_ERROR,
                    user_id=current_user.id if current_user else None,
                    ip_address=request.client.host if request else None,
                    user_agent=request.headers.get("user-agent") if request else None,
                    details={"error": str(e), "function": func.__name__}
                )
                raise
        
        return wrapper
    return decorator
```

### 이상 행위 탐지
```python
# app/security/anomaly_detection.py
from collections import defaultdict, deque
from datetime import datetime, timedelta
import redis
from typing import Dict, List

class AnomalyDetector:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.thresholds = {
            'login_attempts': 5,      # 5분간 최대 로그인 시도 횟수
            'api_calls': 100,         # 1분간 최대 API 호출 횟수
            'file_uploads': 10,       # 1시간간 최대 파일 업로드 횟수
            'failed_requests': 20     # 5분간 최대 실패 요청 횟수
        }
    
    def check_rate_limit(self, user_id: str, action: str, time_window: int = 300) -> bool:
        """비율 제한 확인"""
        key = f"rate_limit:{user_id}:{action}"
        current_time = int(datetime.utcnow().timestamp())
        
        # 시간 윈도우 내의 요청 횟수 확인
        pipe = self.redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, current_time - time_window)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.zcard(key)
        pipe.expire(key, time_window)
        results = pipe.execute()
        
        request_count = results[2]
        threshold = self.thresholds.get(action, 10)
        
        if request_count > threshold:
            self._log_rate_limit_exceeded(user_id, action, request_count)
            return False
        
        return True
    
    def detect_suspicious_pattern(self, user_id: str, ip_address: str, user_agent: str) -> bool:
        """의심스러운 패턴 탐지"""
        suspicious_indicators = []
        
        # 1. 여러 IP에서 동시 접근
        ip_key = f"user_ips:{user_id}"
        self.redis_client.sadd(ip_key, ip_address)
        self.redis_client.expire(ip_key, 3600)  # 1시간
        
        ip_count = self.redis_client.scard(ip_key)
        if ip_count > 3:  # 1시간 내 3개 이상 IP
            suspicious_indicators.append("multiple_ips")
        
        # 2. 비정상적인 User-Agent
        if self._is_suspicious_user_agent(user_agent):
            suspicious_indicators.append("suspicious_user_agent")
        
        # 3. 시간대별 접근 패턴 (업무 시간 외 대량 접근)
        if self._is_off_hours_activity(user_id):
            suspicious_indicators.append("off_hours_activity")
        
        # 4. 연속적인 실패 요청
        if self._has_excessive_failures(user_id):
            suspicious_indicators.append("excessive_failures")
        
        if len(suspicious_indicators) >= 2:
            self._log_suspicious_activity(user_id, ip_address, suspicious_indicators)
            return True
        
        return False
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """의심스러운 User-Agent 확인"""
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper',
            'curl', 'wget', 'python-requests',
            'nikto', 'sqlmap', 'nmap'
        ]
        
        if not user_agent:
            return True
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def _is_off_hours_activity(self, user_id: str) -> bool:
        """업무 시간 외 활동 확인"""
        current_hour = datetime.now().hour
        
        # 업무 시간: 9시-18시
        if not (9 <= current_hour <= 18):
            # 업무 시간 외 API 호출 횟수 확인
            key = f"off_hours_activity:{user_id}"
            count = self.redis_client.incr(key)
            self.redis_client.expire(key, 3600)  # 1시간
            
            return count > 50  # 업무 시간 외 1시간에 50회 이상
        
        return False
    
    def _has_excessive_failures(self, user_id: str) -> bool:
        """과도한 실패 요청 확인"""
        key = f"failures:{user_id}"
        count = self.redis_client.get(key)
        return int(count or 0) > self.thresholds['failed_requests']
    
    def _log_rate_limit_exceeded(self, user_id: str, action: str, count: int):
        """비율 제한 초과 로깅"""
        SecurityLogger().log_security_event(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            user_id=user_id,
            details={
                "type": "rate_limit_exceeded",
                "action": action,
                "count": count,
                "threshold": self.thresholds.get(action)
            }
        )
    
    def _log_suspicious_activity(self, user_id: str, ip_address: str, indicators: List[str]):
        """의심스러운 활동 로깅"""
        SecurityLogger().log_security_event(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "type": "pattern_detection",
                "indicators": indicators,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# 미들웨어로 적용
class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        self.anomaly_detector = AnomalyDetector()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = scope
            user_id = self._extract_user_id(request)
            ip_address = self._get_client_ip(request)
            user_agent = self._get_user_agent(request)
            
            # 이상 행위 탐지
            if user_id and self.anomaly_detector.detect_suspicious_pattern(
                user_id, ip_address, user_agent
            ):
                # 의심스러운 활동 감지 시 차단
                response = PlainTextResponse(
                    "접근이 차단되었습니다. 보안팀에 문의하세요.",
                    status_code=403
                )
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)
```

---

## 📋 컴플라이언스 준수

### GDPR 준수 체계
```python
# app/compliance/gdpr.py
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class GDPRCompliance:
    """GDPR 규정 준수 관리"""
    
    def __init__(self):
        self.data_retention_periods = {
            'user_data': 365 * 3,      # 3년
            'analysis_data': 365 * 5,  # 5년
            'log_data': 365 * 1,       # 1년
            'audit_data': 365 * 7      # 7년
        }
    
    def handle_data_subject_request(self, user_id: str, request_type: str) -> Dict[str, Any]:
        """개인정보 주체 요청 처리"""
        if request_type == "access":
            return self._handle_access_request(user_id)
        elif request_type == "rectification":
            return self._handle_rectification_request(user_id)
        elif request_type == "erasure":
            return self._handle_erasure_request(user_id)
        elif request_type == "portability":
            return self._handle_portability_request(user_id)
        else:
            raise ValueError(f"지원되지 않는 요청 유형: {request_type}")
    
    def _handle_access_request(self, user_id: str) -> Dict[str, Any]:
        """정보 접근 요청 처리 (GDPR Article 15)"""
        user_data = {
            "personal_data": self._get_personal_data(user_id),
            "processing_purposes": [
                "인재 분석 및 평가",
                "시스템 개선을 위한 통계 분석",
                "법적 의무 준수"
            ],
            "data_categories": [
                "식별 정보", "성과 데이터", "분석 결과", "시스템 로그"
            ],
            "retention_periods": self.data_retention_periods,
            "third_parties": [],  # 제3자 공유 없음
            "data_source": "직접 제공 및 시스템 생성"
        }
        
        # 접근 로깅
        SecurityLogger().log_security_event(
            event_type=SecurityEventType.DATA_ACCESS,
            user_id=user_id,
            details={"request_type": "gdpr_access"}
        )
        
        return user_data
    
    def _handle_erasure_request(self, user_id: str) -> Dict[str, Any]:
        """삭제 요청 처리 (GDPR Article 17 - Right to be forgotten)"""
        try:
            # 1. 법적 근거 확인
            if self._has_legal_basis_for_retention(user_id):
                return {
                    "status": "rejected",
                    "reason": "법적 의무 준수를 위해 데이터 보존이 필요합니다"
                }
            
            # 2. 데이터 삭제 실행
            deletion_results = self._execute_data_deletion(user_id)
            
            # 3. 삭제 로깅
            SecurityLogger().log_security_event(
                event_type=SecurityEventType.DATA_ACCESS,
                user_id=user_id,
                details={
                    "request_type": "gdpr_erasure",
                    "deletion_results": deletion_results
                }
            )
            
            return {
                "status": "completed",
                "deleted_data": deletion_results,
                "completion_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"GDPR 삭제 요청 처리 실패: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _execute_data_deletion(self, user_id: str) -> Dict[str, bool]:
        """실제 데이터 삭제 실행"""
        deletion_results = {}
        
        try:
            # 사용자 개인정보
            deletion_results["personal_data"] = self._delete_personal_data(user_id)
            
            # 분석 결과 (익명화)
            deletion_results["analysis_data"] = self._anonymize_analysis_data(user_id)
            
            # 업로드 파일
            deletion_results["uploaded_files"] = self._delete_uploaded_files(user_id)
            
            # 로그 데이터 (최소 보존 기간 후)
            deletion_results["log_data"] = self._clean_log_data(user_id)
            
        except Exception as e:
            logger.error(f"데이터 삭제 중 오류: {e}")
            deletion_results["error"] = str(e)
        
        return deletion_results
    
    def _anonymize_analysis_data(self, user_id: str) -> bool:
        """분석 데이터 익명화"""
        try:
            # 개인 식별 정보 제거하고 통계적 가치는 보존
            query = """
            UPDATE analysis_results 
            SET uid = 'ANONYMIZED_' || id,
                personal_info = NULL,
                updated_at = NOW()
            WHERE uid = %s
            """
            # 실제 데이터베이스 업데이트 실행
            return True
        except Exception as e:
            logger.error(f"분석 데이터 익명화 실패: {e}")
            return False

class DataRetentionManager:
    """데이터 보존 기간 관리"""
    
    def __init__(self):
        self.retention_policies = {
            'user_sessions': timedelta(days=30),
            'analysis_results': timedelta(days=1825),  # 5년
            'audit_logs': timedelta(days=2555),        # 7년
            'system_logs': timedelta(days=365),        # 1년
            'temporary_files': timedelta(days=7)       # 1주일
        }
    
    async def cleanup_expired_data(self):
        """만료된 데이터 정리"""
        for data_type, retention_period in self.retention_policies.items():
            cutoff_date = datetime.utcnow() - retention_period
            
            try:
                deleted_count = await self._delete_expired_data(data_type, cutoff_date)
                logger.info(f"{data_type}: {deleted_count}개 레코드 정리 완료")
                
            except Exception as e:
                logger.error(f"{data_type} 정리 중 오류: {e}")
    
    async def _delete_expired_data(self, data_type: str, cutoff_date: datetime) -> int:
        """특정 데이터 타입의 만료 데이터 삭제"""
        if data_type == 'user_sessions':
            # 세션 데이터 정리
            return await self._cleanup_sessions(cutoff_date)
        elif data_type == 'temporary_files':
            # 임시 파일 정리
            return await self._cleanup_temp_files(cutoff_date)
        # ... 기타 데이터 타입 처리
        
        return 0
```

### 개인정보보호법 준수
```python
# app/compliance/privacy.py
class PrivacyCompliance:
    """개인정보보호법 준수 관리"""
    
    def __init__(self):
        self.sensitive_data_fields = [
            'name', 'email', 'phone', 'address', 
            'social_security_number', 'employee_id'
        ]
        self.processing_purposes = [
            "인사평가 및 관리",
            "업무성과 분석",
            "조직 관리 및 운영"
        ]
    
    def validate_data_processing(self, data: dict, purpose: str) -> bool:
        """개인정보 처리 적법성 검증"""
        
        # 1. 처리 목적 적법성 확인
        if purpose not in self.processing_purposes:
            logger.warning(f"승인되지 않은 처리 목적: {purpose}")
            return False
        
        # 2. 최소 수집 원칙 검증
        if not self._validate_data_minimization(data, purpose):
            return False
        
        # 3. 민감정보 처리 근거 확인
        if self._contains_sensitive_data(data):
            if not self._has_sensitive_data_consent(purpose):
                logger.warning("민감정보 처리 동의 없음")
                return False
        
        return True
    
    def _validate_data_minimization(self, data: dict, purpose: str) -> bool:
        """최소 수집 원칙 검증"""
        required_fields = self._get_required_fields_for_purpose(purpose)
        
        for field in data.keys():
            if field not in required_fields:
                logger.warning(f"목적에 불필요한 필드: {field}")
                return False
        
        return True
    
    def _get_required_fields_for_purpose(self, purpose: str) -> List[str]:
        """처리 목적별 필수 필드"""
        purpose_fields = {
            "인사평가 및 관리": ['uid', 'name', 'department', 'position'],
            "업무성과 분석": ['uid', 'performance_data', 'analysis_date'],
            "조직 관리 및 운영": ['uid', 'department', 'position', 'hire_date']
        }
        return purpose_fields.get(purpose, [])
    
    def generate_privacy_impact_assessment(self, processing_activity: dict) -> dict:
        """개인정보 영향평가 보고서 생성"""
        assessment = {
            "activity_description": processing_activity.get("description"),
            "data_types": processing_activity.get("data_types", []),
            "processing_purposes": processing_activity.get("purposes", []),
            "legal_basis": processing_activity.get("legal_basis"),
            "risk_assessment": self._assess_privacy_risks(processing_activity),
            "mitigation_measures": self._get_mitigation_measures(),
            "assessment_date": datetime.utcnow().isoformat(),
            "next_review_date": (datetime.utcnow() + timedelta(days=365)).isoformat()
        }
        
        return assessment
    
    def _assess_privacy_risks(self, activity: dict) -> dict:
        """개인정보 처리 위험성 평가"""
        risks = {
            "identification_risk": "medium",
            "discrimination_risk": "low",
            "financial_damage_risk": "low",
            "reputation_damage_risk": "medium",
            "freedom_restriction_risk": "low"
        }
        
        # AI 편향 위험 평가
        if "ai_analysis" in activity.get("processing_methods", []):
            risks["discrimination_risk"] = "medium"
            risks["automated_decision_risk"] = "medium"
        
        return risks
```

---

## 🔒 배포 보안

### 운영 환경 보안 설정
```python
# app/config/production_security.py
class ProductionSecurityConfig:
    """운영 환경 보안 설정"""
    
    def __init__(self):
        self.security_settings = {
            # HTTPS 강제
            "FORCE_HTTPS": True,
            "HSTS_MAX_AGE": 31536000,  # 1년
            "HSTS_INCLUDE_SUBDOMAINS": True,
            
            # 세션 보안
            "SESSION_COOKIE_SECURE": True,
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SAMESITE": "Strict",
            
            # 보안 헤더
            "X_CONTENT_TYPE_OPTIONS": "nosniff",
            "X_FRAME_OPTIONS": "DENY",
            "X_XSS_PROTECTION": "1; mode=block",
            
            # CORS 설정
            "CORS_ORIGINS": [
                "https://airiss.okfinancial.com",
                "https://web-production-4066.up.railway.app"
            ],
            
            # 로깅
            "LOG_LEVEL": "INFO",
            "SECURITY_LOG_RETENTION": 90,  # 90일
            
            # 인증
            "JWT_SECRET_ROTATION_DAYS": 30,
            "PASSWORD_MIN_LENGTH": 12,
            "PASSWORD_COMPLEXITY": True,
            "MFA_REQUIRED": True
        }
    
    def apply_security_middleware(self, app):
        """보안 미들웨어 적용"""
        
        @app.middleware("http")
        async def security_headers_middleware(request, call_next):
            response = await call_next(request)
            
            # 보안 헤더 추가
            security_headers = SecurityHeaders.get_security_headers()
            for header, value in security_headers.items():
                response.headers[header] = value
            
            return response
        
        @app.middleware("http")
        async def rate_limiting_middleware(request, call_next):
            client_ip = request.client.host
            
            # IP별 요청 제한 (분당 100회)
            if not self._check_rate_limit(client_ip):
                return PlainTextResponse(
                    "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
                    status_code=429
                )
            
            return await call_next(request)

# 환경별 설정 분리
class EnvironmentConfig:
    @staticmethod
    def get_config():
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            return ProductionSecurityConfig()
        elif env == "staging":
            return StagingSecurityConfig()
        else:
            return DevelopmentSecurityConfig()

# Railway 배포 시 보안 설정
class RailwaySecurityConfig:
    """Railway 플랫폼 보안 설정"""
    
    @staticmethod
    def configure_railway_security():
        """Railway 환경 보안 구성"""
        return {
            # 환경변수 암호화
            "secrets": [
                "JWT_SECRET_KEY",
                "DATABASE_PASSWORD", 
                "ENCRYPTION_KEY"
            ],
            
            # 네트워크 보안
            "network_policies": {
                "ingress": {
                    "allowed_ports": [80, 443],
                    "protocol": "HTTPS"
                },
                "egress": {
                    "allowed_domains": [
                        "*.postgresql.com",
                        "*.railway.app"
                    ]
                }
            },
            
            # 리소스 제한
            "resource_limits": {
                "memory": "2Gi",
                "cpu": "1000m",
                "storage": "10Gi"
            },
            
            # 로그 설정
            "logging": {
                "level": "INFO",
                "retention_days": 30,
                "structured": True
            }
        }
```

---

## 📋 보안 체크리스트

### 개발 단계 보안 검증
- [ ] **인증/인가**
  - [ ] JWT 토큰 검증 구현
  - [ ] 역할 기반 접근 제어 (RBAC)
  - [ ] 세션 타임아웃 설정
  - [ ] 비밀번호 정책 적용

- [ ] **데이터 보호**
  - [ ] 민감한 데이터 암호화
  - [ ] 데이터베이스 연결 보안
  - [ ] 백업 데이터 암호화
  - [ ] 데이터 마스킹 적용

- [ ] **입력 검증**
  - [ ] 모든 입력 데이터 검증
  - [ ] SQL Injection 방지
  - [ ] XSS 공격 방지
  - [ ] 파일 업로드 보안

- [ ] **출력 보안**
  - [ ] 응답 데이터 정화
  - [ ] 에러 정보 노출 방지
  - [ ] 민감한 정보 마스킹
  - [ ] 보안 헤더 설정

### 배포 전 보안 검증
- [ ] **환경 설정**
  - [ ] 운영/개발 환경 분리
  - [ ] 환경변수 암호화
  - [ ] 디버그 모드 비활성화
  - [ ] 불필요한 서비스 제거

- [ ] **네트워크 보안**
  - [ ] HTTPS 강제 적용
  - [ ] 방화벽 설정
  - [ ] 포트 접근 제한
  - [ ] CDN 보안 설정

- [ ] **모니터링**
  - [ ] 보안 로그 설정
  - [ ] 이상 행위 탐지
  - [ ] 알림 시스템 구성
  - [ ] 정기 보안 감사

---

**"보안은 선택이 아닌 필수입니다. 다층 보안으로 안전한 AIRISS를 구축하세요!"** 🛡️