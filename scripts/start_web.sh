#!/bin/bash
# Start Flask API Server

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Start Flask
cd web
python app.py
