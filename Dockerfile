# AIRISS v4.1 Railway Multi-stage Dockerfile - Optimized
# React + FastAPI Complete Integration

# Stage 1: React Frontend Build
FROM node:18-slim as frontend-builder

WORKDIR /app/frontend

# Install Node.js dependencies (production + dev for build)
COPY airiss-v4-frontend/package*.json ./
RUN npm ci

# Copy React source and build
COPY airiss-v4-frontend/ ./

# Set build environment variables
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV GENERATE_SOURCEMAP=false
ENV DISABLE_ESLINT_PLUGIN=true
ENV CI=false

# Build with increased memory
RUN npm run build

# Stage 2: Python FastAPI + React Static Files  
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy React build results
COPY --from=frontend-builder /app/frontend/build ./static

# Upgrade pip first
RUN pip install --upgrade pip

# Create minimal requirements for faster startup
COPY requirements.txt .

# Copy install script and install OpenAI FIRST
COPY install_openai.sh .
RUN chmod +x install_openai.sh && ./install_openai.sh

# Install only essential dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0 \
    sqlalchemy>=2.0.0 \
    aiosqlite>=0.19.0 \
    pydantic>=2.5.0 \
    aiofiles==23.2.1

# Then install the rest
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/uploads /app/results /app/temp_data

# Environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///data/airiss.db
ENV SERVER_HOST=0.0.0.0
ENV REACT_BUILD_PATH=/app/static
ENV NODE_ENV=production
ENV DISABLE_ESLINT_PLUGIN=true

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Railway dynamic port support
EXPOSE 8000

# Install OpenAI on startup if not available, then start server
CMD ["sh", "-c", "./install_openai.sh && python check_openai.py && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"]