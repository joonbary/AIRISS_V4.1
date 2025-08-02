#!/usr/bin/env python
"""
Enable AI mode by setting environment variable
"""
import os

# Set OpenAI API key if available
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ OPENAI_API_KEY found: {api_key[:10]}...")
    # Write to .env file for backup
    with open(".env", "a") as f:
        f.write(f"\nOPENAI_API_KEY={api_key}\n")
else:
    print("⚠️ OPENAI_API_KEY not found in environment")
    print("Using mock mode for analysis")