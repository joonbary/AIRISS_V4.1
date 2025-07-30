#!/usr/bin/env python
"""Simple startup script for Railway deployment"""
import os
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs('data', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('results', exist_ok=True)
os.makedirs('temp_data', exist_ok=True)

# Get port from environment
port = int(os.getenv("PORT", 8000))

logger.info(f"Starting AIRISS v4.0 on port {port}")
logger.info(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///data/airiss.db')}")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

# Start the server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )