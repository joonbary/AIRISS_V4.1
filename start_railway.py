#!/usr/bin/env python
"""Railway-specific startup script with enhanced health checks"""
import os
import sys
import time
import logging
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
directories = ['data', 'uploads', 'results', 'temp_data']
for directory in directories:
    Path(directory).mkdir(exist_ok=True)
    logger.info(f"Created directory: {directory}")

# Get port from environment
PORT = int(os.getenv("PORT", 8000))
logger.info(f"Starting AIRISS v4.0 on port {PORT}")

# Set environment variables
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///data/airiss.db')
os.environ['PYTHONPATH'] = '/app'
os.environ['SERVER_HOST'] = '0.0.0.0'

# Log environment
logger.info(f"Database URL: {os.environ['DATABASE_URL']}")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

# Import FastAPI app after setting environment
try:
    from app.main import app
    logger.info("Successfully imported FastAPI app")
except Exception as e:
    logger.error(f"Failed to import app: {e}")
    sys.exit(1)

# Create a simple health check endpoint if it doesn't exist
@app.get("/health")
async def health_check():
    """Railway health check endpoint"""
    return {"status": "healthy", "service": "AIRISS v4.0", "port": PORT}

# Start uvicorn
if __name__ == "__main__":
    import uvicorn
    
    # Railway expects the server to be ready quickly
    logger.info("Starting Uvicorn server...")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=PORT,
            log_level="info",
            access_log=True,
            # Disable reload in production
            reload=False,
            # Use a single worker for Railway
            workers=1
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)