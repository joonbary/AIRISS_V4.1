@echo off
<<<<<<< HEAD
echo Removing problematic files...
if exist .env.aws.example del .env.aws.example
if exist start_with_cloud_db.bat del start_with_cloud_db.bat

echo Creating .gitignore...
echo .env > .gitignore
echo .env.* >> .gitignore
echo *.env >> .gitignore
echo *.tmp >> .gitignore
echo temp/ >> .gitignore
echo start_with_cloud_db.bat >> .gitignore
echo node_modules/ >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore

echo Creating safe template...
echo # AIRISS v5.0 Configuration Template > .env.template
echo PROJECT_NAME=AIRISS v5.0 >> .env.template
echo VERSION=5.0.0 >> .env.template
echo DATABASE_URL=sqlite:///./airiss_v5.db >> .env.template
echo. >> .env.template
echo # OpenAI API Key >> .env.template
echo OPENAI_API_KEY=your-openai-api-key-here >> .env.template
echo. >> .env.template
echo # AWS Configuration >> .env.template
echo AWS_ACCESS_KEY_ID=your-aws-access-key >> .env.template
echo AWS_SECRET_ACCESS_KEY=your-aws-secret-key >> .env.template

echo Staging changes...
git add .

echo Committing...
git commit -m "security: Remove sensitive files and add safe templates"

echo Pushing to GitHub...
git push origin HEAD

echo Done! Check GitHub now.
=======
echo AIRISS v4.1 Quick Fix
echo ===================

if exist venv move venv venv_backup
py -3.11 -m venv venv_new
call venv_new\Scripts\activate
python -m pip install --upgrade pip
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0
pip install sqlalchemy==2.0.23 pandas==2.1.3 aiosqlite==0.19.0
pip install python-multipart jinja2 aiofiles websockets
pip install pydantic==2.5.0 --only-binary=all
python init_database.py
start http://localhost:8002/health
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

>>>>>>> ba15bf7c5cb2c6c504d1d788a00099bd2357256f
pause
