#!/bin/bash
# Install OpenAI package forcefully
echo "Installing OpenAI package..."
pip install --no-cache-dir openai==1.54.5
echo "OpenAI installation completed"
python -c "import openai; print(f'OpenAI version: {openai.__version__}')"