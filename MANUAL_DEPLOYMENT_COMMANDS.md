# AIRISS v4.1 Complete - Manual Deployment Commands
# Use these commands if batch files have encoding issues

## 1. Git Status Check
git status

## 2. Add All Changes
git add -A

## 3. Commit Changes
git commit -m "feat: Complete React + FastAPI hybrid project integration - Dockerfile: Multi-stage build with React app included - main.py: StaticFiles for React static file serving - railway.json: Added REACT_BUILD_PATH environment variable - SPA routing support for all frontend routes - Health check endpoint includes React build status"

## 4. Push to GitHub
git push origin main

## 5. Railway Deployment Steps
# Go to: https://railway.app
# Login with GitHub account
# Select your project: AIRISS_V4.1
# Click "Deploy" or wait for auto-deploy
# Monitor build logs for React build process

## 6. Test Commands (replace [URL] with your Railway domain)
curl [URL]/health
curl [URL]/api
curl [URL]/api/status

## 7. Expected Results
# Health Check: {"status": "healthy", "components": {"react_build": "available"}}
# API: {"message": "AIRISS v4.1 Complete API", "features": {"react_frontend": true}}
# Frontend: Should return HTML with React app

## Files Modified:
# - Dockerfile (multi-stage build)
# - app/main.py (static file serving)
# - railway.json (environment variables)

## Backup Files Created:
# - Dockerfile.backup.emergency
# - app/main_emergency.py
# - railway.json.backup
