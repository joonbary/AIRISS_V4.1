"""
Logging Configuration
로깅 설정 및 유틸리티
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """구조화된 로그 포맷터 (JSON)"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 추가 컨텍스트
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
        
        # 예외 정보
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_format: Optional[str] = None,
    log_dir: Optional[Path] = None,
    use_json: bool = False
) -> None:
    """로깅 설정"""
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 포맷터 설정
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            log_format or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 파일 핸들러 (옵션)
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 일반 로그
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "airiss.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 에러 로그 (별도 파일)
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


class LoggerAdapter(logging.LoggerAdapter):
    """컨텍스트 정보를 추가하는 로거 어댑터"""
    
    def process(self, msg, kwargs):
        # 컨텍스트 정보 추가
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(
    name: str,
    user_id: Optional[int] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> LoggerAdapter:
    """컨텍스트가 있는 로거 생성"""
    logger = logging.getLogger(name)
    
    extra = {}
    if user_id:
        extra["user_id"] = user_id
    if request_id:
        extra["request_id"] = request_id
    extra.update(kwargs)
    
    return LoggerAdapter(logger, extra)