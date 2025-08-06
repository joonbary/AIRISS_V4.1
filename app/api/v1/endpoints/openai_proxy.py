"""
OpenAI API 프록시 엔드포인트
Railway 환경에서 OpenAI API 호출 우회
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
import asyncio
import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# OpenAI API 설정
OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_TIMEOUT = 60.0

async def get_openai_client():
    """OpenAI API 클라이언트 생성"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    return httpx.AsyncClient(
        base_url=OPENAI_BASE_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        timeout=httpx.Timeout(DEFAULT_TIMEOUT)
    )

@router.post("/proxy/openai/chat/completions")
async def proxy_chat_completions(request_data: Dict[str, Any]):
    """
    OpenAI Chat Completions API 프록시
    Railway → 자체 서버 → OpenAI API
    """
    
    logger.info(f"🔄 OpenAI API 프록시 호출 시작")
    
    try:
        async with await get_openai_client() as client:
            # OpenAI API 호출
            response = await client.post(
                "/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ OpenAI API 프록시 성공")
                return result
            else:
                error_text = response.text
                logger.error(f"❌ OpenAI API 오류: {response.status_code}")
                logger.error(f"   응답: {error_text}")
                
                raise HTTPException(
                    status_code=response.status_code,
                    detail={
                        "error": "OpenAI API Error",
                        "status_code": response.status_code,
                        "message": error_text
                    }
                )
                
    except httpx.ConnectError as e:
        logger.error(f"❌ OpenAI API 연결 실패: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Connection Error",
                "message": "Failed to connect to OpenAI API",
                "suggestion": "Check network connectivity or try again later"
            }
        )
    
    except httpx.TimeoutException as e:
        logger.error(f"❌ OpenAI API 타임아웃: {e}")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Timeout Error", 
                "message": "OpenAI API request timed out",
                "suggestion": "Try again with shorter content or increase timeout"
            }
        )
    
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": str(e)
            }
        )

@router.get("/proxy/openai/test")
async def test_openai_connection():
    """OpenAI API 연결 테스트"""
    
    try:
        async with await get_openai_client() as client:
            # 간단한 테스트 요청
            test_request = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "Test"}
                ],
                "max_tokens": 5
            }
            
            response = await client.post("/chat/completions", json=test_request)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "OpenAI API connection successful",
                    "proxy_working": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"OpenAI API returned {response.status_code}",
                    "proxy_working": False
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "proxy_working": False
        }