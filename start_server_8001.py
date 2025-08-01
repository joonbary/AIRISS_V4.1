#!/usr/bin/env python
"""Start server on port 8001"""
import subprocess
import sys

if __name__ == "__main__":
    port = 8001
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", str(port)]
    subprocess.run(cmd)