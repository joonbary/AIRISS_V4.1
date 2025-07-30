#!/usr/bin/env python
"""Minimal startup for Railway debugging"""
import os
import sys

print("=== AIRISS v4 Minimal Start ===")
print(f"Python: {sys.version}")
print(f"Port: {os.getenv('PORT', '8000')}")
print(f"Working directory: {os.getcwd()}")

# Create minimal FastAPI app
from fastapi import FastAPI

app = FastAPI(title="AIRISS v4 Minimal")

@app.get("/")
def root():
    return {"message": "AIRISS v4 Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Try to import main app
try:
    from app.main import app as main_app
    app = main_app
    print("✓ Main app loaded successfully")
except Exception as e:
    print(f"! Using minimal app due to: {e}")

# Start server
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")