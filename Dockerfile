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

# Install Python dependencies
COPY requirements.txt .
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

# Railway dynamic port support
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8002}"]