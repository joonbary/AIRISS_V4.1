#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 Server Runner
Simplified startup script for Railway deployment
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import and run the app
if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    port = int(os.getenv("PORT", 8002))
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    
    print(f"Starting AIRISS v4.0 server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )