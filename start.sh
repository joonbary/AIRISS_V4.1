#!/bin/bash
# Railway startup script
echo "Starting AIRISS v4..."
echo "Port: ${PORT:-8000}"

# Use Python to handle the port correctly
exec python -c "
import os
import uvicorn
from app.main import app

port = int(os.getenv('PORT', 8000))
print(f'Starting server on port {port}')
uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')
"