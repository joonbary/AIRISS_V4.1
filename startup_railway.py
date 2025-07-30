#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Railway Startup Script for AIRISS v4.1
Handles database initialization and server startup
"""
import os
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "/app/data",
        "/app/uploads", 
        "/app/results",
        "/app/temp_data"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Directory ensured: {dir_path}")

def initialize_database():
    """Initialize database with retry logic"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Initializing database (attempt {attempt + 1}/{max_retries})...")
            
            # Set database path
            os.environ["DATABASE_URL"] = "sqlite:///app/data/airiss.db"
            
            # Import and initialize
            from app.db.database import init_db
            init_db()
            
            logger.info("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ Failed to initialize database after all retries")
                return False
    
    return False

def start_server():
    """Start the FastAPI server"""
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting AIRISS v4.1 server on port {port}...")
    
    # Import and run uvicorn
    import uvicorn
    from app.main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )

def main():
    """Main startup sequence"""
    logger.info("🚀 AIRISS v4.1 Railway Startup")
    
    # Ensure directories exist
    ensure_directories()
    
    # Initialize database
    if not initialize_database():
        logger.error("Failed to initialize database. Starting server anyway...")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
