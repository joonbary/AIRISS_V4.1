# EMERGENCY ULTRA-MINIMAL main.py for Railway
# Absolute minimum to pass health check

from fastapi import FastAPI
import os

app = FastAPI(title="AIRISS Emergency")

@app.get("/")
def root():
    return {"status": "live", "message": "AIRISS Railway Emergency Deploy"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "airiss"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
