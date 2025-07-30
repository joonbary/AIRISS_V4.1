#!/usr/bin/env python
"""Test script to verify basic FastAPI functionality"""
import os
import sys

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))

try:
    from app.main import app
    print("✓ Successfully imported FastAPI app")
    
    # Test if app has required endpoints
    routes = [route.path for route in app.routes]
    print(f"✓ Found {len(routes)} routes")
    print("Routes:", routes[:10])  # Show first 10 routes
    
    if '/health' in routes:
        print("✓ Health endpoint found")
    else:
        print("✗ Health endpoint NOT found")
        
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStarting uvicorn...")
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))