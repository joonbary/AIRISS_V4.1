"""Railway environment setup"""
import os

# Set default environment variables for Railway
os.environ.setdefault('DATABASE_URL', 'sqlite:///data/airiss.db')
os.environ.setdefault('PYTHONPATH', '/app')
os.environ.setdefault('ENVIRONMENT', 'production')

# Create necessary directories
import pathlib
pathlib.Path('data').mkdir(exist_ok=True)
pathlib.Path('uploads').mkdir(exist_ok=True)
pathlib.Path('results').mkdir(exist_ok=True)
pathlib.Path('temp_data').mkdir(exist_ok=True)

print("Railway environment setup complete")
print(f"Port: {os.getenv('PORT', '8000')}")
print(f"Database: {os.getenv('DATABASE_URL')}")