#!/usr/bin/env python3
"""
AIRISS Railway Deployment Diagnosis Tool
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return output"""
    print(f"\n{'='*50}")
    print(f"🔍 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ SUCCESS")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"Error: {result.stderr}")
            if result.stdout.strip():
                print(f"Output: {result.stdout}")
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT (30s)")
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")

def main():
    print("🚀 AIRISS Railway Deployment Diagnosis")
    print("=" * 60)
    
    # Basic checks
    run_command("python --version", "Python Version Check")
    run_command("where railway", "Railway CLI Location")
    run_command("railway --version", "Railway CLI Version")
    
    # Railway status
    run_command("railway whoami", "Railway Login Status")
    run_command("railway status", "Railway Service Status")
    
    # Check if we can import the app
    print(f"\n{'='*50}")
    print("🔍 Testing App Import")
    print(f"{'='*50}")
    try:
        sys.path.append('.')
        from app.main import app
        print("✅ App import successful")
        print(f"App title: {app.title}")
        print(f"App version: {app.version}")
    except Exception as e:
        print(f"❌ App import failed: {e}")
    
    # Get logs
    run_command("railway logs --type build --tail 20", "Recent Build Logs")
    run_command("railway logs --type deploy --tail 20", "Recent Deploy Logs")
    run_command("railway logs --tail 30", "Recent Application Logs")
    
    # Environment check
    run_command("railway variables", "Environment Variables")
    
    print(f"\n{'='*60}")
    print("🎯 Diagnosis completed!")
    print("📋 Review the results above to identify issues.")
    print("🔧 Common solutions:")
    print("   1. railway login (if login failed)")
    print("   2. railway redeploy (force redeploy)")
    print("   3. Check build logs for dependency issues")
    print("   4. Check deploy logs for startup issues")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
