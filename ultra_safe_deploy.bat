@echo off
title AIRISS Deploy

echo AIRISS v4.1 Deploy
echo ===================

cd /d "%~dp0"

echo Step 1: Copy requirements...
copy requirements_vercel.txt requirements.txt

echo Step 2: Git setup...
if exist .git rmdir /s /q .git
git init
git add .
git commit -m "AIRISS v4.1"

echo Step 3: Complete!
echo.
echo Manual Steps:
echo 1. https://github.com/new
echo 2. Name: airiss-v4
echo 3. git remote add origin https://github.com/USERNAME/airiss-v4.git
echo 4. git push -u origin main
echo 5. https://vercel.com/new
echo 6. Deploy

pause
start https://github.com/new
