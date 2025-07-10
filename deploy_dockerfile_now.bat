git add Dockerfile
git add railway.json
git commit -m "Add Dockerfile for Railway multi-stage build"
git push origin main
echo.
echo SUCCESS: Dockerfile added and pushed!
echo.
echo Railway will now:
echo 1. Detect new Dockerfile
echo 2. Run React build stage
echo 3. Run Python build stage  
echo 4. Deploy with correct PORT
echo.
echo Test URL: https://web-production-4066.up.railway.app/health
pause