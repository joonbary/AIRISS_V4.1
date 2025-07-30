#!/usr/bin/env python
"""Start server with proper PORT handling for Railway"""
import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Get port from environment variable
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting AIRISS v4 server on port {port}")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )