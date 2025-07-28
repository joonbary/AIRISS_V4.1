# AIRISS v4.1 Railway Multi-stage Dockerfile - Frontend Path Fixed
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

# Install Python dependencies
COPY requirements.txt .
# Install PyTorch CPU version first (Railway에서 가장 안정적인 버전)
RUN pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory
RUN mkdir -p /app/data

# Environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///data/airiss.db
ENV SERVER_HOST=0.0.0.0
ENV REACT_BUILD_PATH=/app/static
ENV NODE_ENV=production
ENV DISABLE_ESLINT_PLUGIN=true

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8002}/health || exit 1

# Make startup script executable
COPY startup.sh .
RUN chmod +x startup.sh

# Railway dynamic port support
EXPOSE 8002
CMD ["./startup.sh"]