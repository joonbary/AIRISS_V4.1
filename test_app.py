#!/usr/bin/env python
"""Test app for Railway deployment debugging"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=== Railway Test App Starting ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Port: {os.getenv('PORT', 'Not set')}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Files in directory: {os.listdir('.')[:10]}")

# Test FastAPI import
try:
    from fastapi import FastAPI
    logger.info("✓ FastAPI imported successfully")
    
    app = FastAPI(title="Railway Test")
    
    @app.get("/")
    def root():
        return {"status": "Railway test app running", "port": os.getenv("PORT")}
    
    @app.get("/health")
    def health():
        return {"status": "healthy"}
    
    # Try to import main app
    try:
        from app.main import app as main_app
        app = main_app
        logger.info("✓ Main AIRISS app loaded successfully")
    except Exception as e:
        logger.error(f"! Could not load main app: {e}")
        logger.info("! Using test app instead")
    
    # Start server
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except Exception as e:
    logger.error(f"Failed to start: {e}")
    import traceback
    traceback.print_exc()
    
    # Keep the process alive for debugging
    logger.info("Keeping process alive for debugging...")
    import time
    while True:
        time.sleep(60)
        logger.info("Still running...")