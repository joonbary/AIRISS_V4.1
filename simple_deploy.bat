@echo off
cd /d "%~dp0"
copy requirements_vercel.txt requirements.txt
git init
git add .
git commit -m "deploy"
echo Go to: https://github.com/new
echo Name: airiss-v4
echo Then: git remote add origin https://github.com/USER/airiss-v4.git
echo Then: git push -u origin main
echo Then: https://vercel.com/new
pause
start https://github.com/new
