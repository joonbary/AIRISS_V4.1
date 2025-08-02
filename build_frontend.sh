#!/bin/bash
# Build React frontend locally
echo "Building React frontend..."
cd airiss-v4-frontend
export CI=false
export DISABLE_ESLINT_PLUGIN=true
export GENERATE_SOURCEMAP=false
npm install --legacy-peer-deps
npm run build
echo "Build completed!"