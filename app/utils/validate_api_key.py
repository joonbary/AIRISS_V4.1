"""
OpenAI API 키 검증 유틸리티
"""
import os
import logging

logger = logging.getLogger(__name__)

# 알려진 무효한 API 키 패턴들
INVALID_KEY_PATTERNS = [
    "sk-proj-example",
    "sk-1234567890",
    "your-api-key",
    "YOUR_API_KEY_HERE",
    "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "sk-placeholder",
    "sk-test",
    "test-key",
]

def is_valid_api_key(api_key: str) -> bool:
    """API 키 유효성 검증"""
    if not api_key:
        return False
    
    # 공백 제거
    api_key = api_key.strip()
    
    # 최소 길이 확인
    if len(api_key) < 20:
        logger.warning(f"API 키가 너무 짧습니다: {len(api_key)}자")
        return False
    
    # 올바른 형식 확인 (sk-로 시작)
    if not (api_key.startswith('sk-') or api_key.startswith('sess-')):
        logger.warning(f"잘못된 API 키 형식: {api_key[:10]}...")
        return False
    
    # 알려진 무효한 키 패턴 확인
    for invalid_pattern in INVALID_KEY_PATTERNS:
        if invalid_pattern in api_key.lower():
            logger.warning(f"알려진 무효한 API 키 패턴 감지: {invalid_pattern}")
            return False
    
    # 플레이스홀더 확인
    if 'xxxx' in api_key.lower() or '1234' in api_key:
        logger.warning("플레이스홀더 API 키 감지")
        return False
    
    return True

def get_valid_api_key() -> str:
    """유효한 API 키 가져오기"""
    
    # 1. 환경 변수에서 시도
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and is_valid_api_key(api_key):
        logger.info(f"✅ 환경 변수에서 유효한 API 키 로드: {api_key[:10]}...")
        return api_key
    
    # 2. 대체 환경 변수 이름들 시도
    alternative_keys = ["OPENAI_KEY", "OPEN_AI_KEY", "OPEN_AI_API_KEY"]
    for key_name in alternative_keys:
        api_key = os.getenv(key_name)
        if api_key and is_valid_api_key(api_key):
            logger.info(f"✅ {key_name}에서 유효한 API 키 로드: {api_key[:10]}...")
            return api_key
    
    # 3. 설정 파일에서 시도
    try:
        from app.core.config import settings
        if settings.OPENAI_API_KEY and is_valid_api_key(settings.OPENAI_API_KEY):
            logger.info(f"✅ 설정에서 유효한 API 키 로드: {settings.OPENAI_API_KEY[:10]}...")
            return settings.OPENAI_API_KEY
    except Exception as e:
        logger.error(f"설정에서 API 키 로드 실패: {e}")
    
    logger.warning("⚠️ 유효한 OpenAI API 키를 찾을 수 없습니다")
    return None