import subprocess
import sys

# 백엔드 서버 실행
subprocess.Popen([sys.executable, "-m", "app.main"])