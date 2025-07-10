# AIRISS v4.1 Railway Deploy - Manual Commands
# PORT Environment Variable Fix - Final Step

## Step 1: Navigate to project directory
```cmd
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
```

## Step 2: Check Git status
```cmd
git status
```

## Step 3: Add railway.json changes
```cmd
git add railway.json
```

## Step 4: Commit PORT fix
```cmd
git commit -m "fix: Railway PORT environment variable parsing issue - use shell substitution"
```

## Step 5: Push to GitHub
```cmd
git push origin main
```

## Step 6: Monitor Railway deployment
1. Go to Railway Dashboard: https://railway.app/project/
2. Watch for auto-redeploy trigger
3. Monitor build logs (expect 2-5 minutes)
4. Check deployment success

## Step 7: Test deployment
- Health check: https://web-production-4066.up.railway.app/health
- Full app: https://web-production-4066.up.railway.app/
- API info: https://web-production-4066.up.railway.app/api

## Expected Result
```json
{
  "status": "healthy",
  "service": "AIRISS v4.1 Complete",
  "version": "4.1.0-complete",
  "message": "OK"
}
```

## If Still Failing
Run: `deploy_railway_emergency_english.bat` (Emergency minimal version)

## Notes
- Railway auto-detects GitHub pushes and redeploys
- PORT issue was the last blocker - should work now
- React build already completed and ready
- FastAPI + React integration already configured
