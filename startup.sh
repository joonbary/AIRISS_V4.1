#!/bin/bash
# AIRISS v4.0 Startup Script for Railway

echo "Starting AIRISS v4.0..."

# Set default environment variables if not set
export DATABASE_URL=${DATABASE_URL:-"sqlite:///data/airiss.db"}
export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
export SERVER_HOST=${SERVER_HOST:-"0.0.0.0"}
export PORT=${PORT:-8000}

# Create necessary directories
mkdir -p data
mkdir -p uploads
mkdir -p results
mkdir -p temp_data

echo "Directories created"
echo "Environment:"
echo "  - PORT: $PORT"
echo "  - DATABASE_URL: ${DATABASE_URL:0:30}..."
echo "  - REACT_BUILD_PATH: $REACT_BUILD_PATH"

# Check if React build exists
if [ -d "$REACT_BUILD_PATH" ]; then
    echo "React build found at: $REACT_BUILD_PATH"
    ls -la $REACT_BUILD_PATH | head -5
else
    echo "Warning: React build not found at: $REACT_BUILD_PATH"
fi

# Start the server directly with uvicorn
echo "Starting server on port $PORT..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info