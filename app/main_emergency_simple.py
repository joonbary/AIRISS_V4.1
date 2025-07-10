# AIRISS v4.1 Emergency - 최소 기능 FastAPI
# Railway 배포 성공을 위한 초간단 버전

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# FastAPI 앱 (최소 설정)
app = FastAPI(title="AIRISS v4.1 Emergency")

@app.get("/health")
async def health():
    """간단 헬스체크"""
    return {"status": "healthy", "time": datetime.now().isoformat()}

@app.get("/")
async def root():
    """루트 경로"""
    return {
        "message": "AIRISS v4.1 Emergency Mode",
        "status": "running",
        "port": os.getenv("PORT", "8002")
    }

@app.get("/api")
async def api():
    """API 정보"""
    return {
        "service": "AIRISS v4.1 Emergency",
        "version": "emergency",
        "react_build": os.path.exists("./static"),
        "status": "ok"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
