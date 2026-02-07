#!/bin/bash
# Complete fresh start for Flask API

cd /Users/aeldeeb/Ahmed/git/stock-tracker

# Kill all Flask processes
pkill -9 -f "python.*app.py" 2>/dev/null
sleep 2

# Remove ALL Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

echo "Cache cleared"
sleep 1

# Activate venv and start Flask
cd web
source ../venv/bin/activate

# Unset PYTHONDONTWRITEBYTECODE to avoid issues
unset PYTHONDONTWRITEBYTECODE

# Start Flask
python -u app.py 2>&1 | tee /tmp/flask_fresh.log &

echo "Flask starting on port 5555..."
sleep 6

# Test the API
echo ""
echo "Testing API:"
curl -s http://localhost:5555/health
echo ""
echo ""
curl -s http://localhost:5555/api/stocks | python3 -m json.tool | head -60
