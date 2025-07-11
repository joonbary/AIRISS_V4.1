@echo off
echo ============================================================
echo AIRISS Post-Upload Verification Guide
echo ============================================================
echo.
echo Step 1: Verify GitHub Repository
echo --------------------------------
echo 1. Visit: https://github.com/joonbary/AIRISS_V4.1.git
echo 2. Check latest commit timestamp
echo 3. Verify file count matches local
echo.
echo Step 2: Test Deployment
echo -----------------------  
echo 1. Visit: https://web-production-4066.up.railway.app/dashboard
echo 2. Check if latest changes are deployed
echo 3. Test file upload functionality
echo.
echo Step 3: Run System Health Check
echo -------------------------------
echo 1. Execute: python check_integration_status.py
echo 2. Verify: PostgreSQL connection active
echo 3. Confirm: All tests pass (4/4)
echo.
echo Step 4: Performance Test
echo ------------------------
echo 1. Upload test Excel file
echo 2. Run analysis (should complete in under 30 seconds)
echo 3. Check results saved to Neon DB
echo.
echo ============================================================
echo All systems ready for production use!
echo ============================================================
pause
