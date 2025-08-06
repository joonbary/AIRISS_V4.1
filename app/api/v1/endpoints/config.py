"""
Configuration API endpoints
환경변수 기반 설정 정보 제공
"""
from fastapi import APIRouter, HTTPException
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api-key-status")
async def get_api_key_status():
    """
    OpenAI API 키 설정 상태 확인
    키 값은 노출하지 않고 설정 여부와 마스킹된 형태만 반환
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY", "")
        
        if not api_key:
            return {
                "configured": False,
                "masked_key": "",
                "message": "API 키가 설정되지 않았습니다"
            }
        
        # 키가 있으면 앞 7자리와 뒤 4자리만 보여주고 나머지는 마스킹
        if len(api_key) > 15:
            masked_key = f"{api_key[:7]}...{api_key[-4:]}"
        else:
            masked_key = "***"
            
        return {
            "configured": True,
            "masked_key": masked_key,
            "message": "API 키가 설정되어 있습니다"
        }
        
    except Exception as e:
        logger.error(f"API key status check failed: {e}")
        return {
            "configured": False,
            "masked_key": "",
            "message": "API 키 상태 확인 실패"
        }

@router.get("/default-model")
async def get_default_model():
    """기본 OpenAI 모델 설정 반환"""
    return {
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    }