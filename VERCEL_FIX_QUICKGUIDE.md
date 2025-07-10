# VERCEL 250MB ERROR - QUICK FIX GUIDE

## ❌ PROBLEM
- Serverless Function exceeded 250MB limit
- Deployment failed on Vercel

## ✅ SOLUTION FILES CREATED
1. `.vercelignore` - Excludes large files
2. `requirements_vercel_ultralight.txt` - Minimal dependencies  
3. `vercel_optimized.json` - Size-optimized config
4. `api/index_ultralight.py` - Lightweight API
5. `deploy_vercel_safe.bat` - Safe deployment script

## 🚀 QUICK DEPLOYMENT (3 STEPS)

### OPTION A: One-Click Deploy
```cmd
deploy_oneclick.bat
```

### OPTION B: Manual Steps  
```cmd
1. test_ultralight_local.bat     (Test locally first)
2. deploy_vercel_safe.bat        (Deploy to Vercel)  
3. Check: https://vercel.com/dashboard
```

### OPTION C: Emergency Rollback
```cmd
rollback_vercel.bat              (If deployment fails)
```

## 📊 WHAT WAS OPTIMIZED

### Files Excluded (.vercelignore)
- Development files (venv/, __pycache__/)
- Database files (*.db, *.sqlite)  
- Documentation (docs/, *.md)
- Scripts (*.bat, *.ps1)
- Test data (test_data/, uploads/)

### Dependencies Reduced
- Removed: scikit-learn, tensorflow, large ML libs
- Kept: fastapi, uvicorn, pandas, numpy (essential only)
- Size: ~200MB → ~15MB

### Configuration Optimized  
- Function size limit: 15MB
- Runtime: Python 3.9
- Excludes: Large files and folders

## 🔍 VERIFICATION STEPS

1. **Local Test**: Run `test_ultralight_local.bat`
2. **Deploy**: Run `deploy_vercel_safe.bat`  
3. **Check**: https://vercel.com/dashboard
4. **Test Live**: Visit your Vercel URL
5. **Monitor**: Check for errors in dashboard

## 🆘 IF PROBLEMS OCCUR

1. **Deployment Still Fails**: Run `rollback_vercel.bat`
2. **Local Test Fails**: Check Python/pip installation
3. **Size Still Too Large**: Check .vercelignore coverage
4. **Import Errors**: Verify requirements_vercel_ultralight.txt

## 📞 SUCCESS INDICATORS

- ✅ Vercel build completes successfully
- ✅ Live URL responds with AIRISS homepage  
- ✅ /health endpoint returns status "healthy"
- ✅ /docs shows API documentation
- ✅ No error messages in Vercel dashboard

## 🎯 NEXT STEPS AFTER SUCCESS

1. Test all endpoints work correctly
2. Monitor performance and errors
3. Add back features gradually if needed
4. Consider upgrading Vercel plan for larger deployments

---
**Need help?** Check Vercel dashboard logs for specific error details.
