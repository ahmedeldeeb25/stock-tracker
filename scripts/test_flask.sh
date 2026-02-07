#!/bin/bash
cd /Users/aeldeeb/Ahmed/git/stock-tracker/web
source ../venv/bin/activate

# Kill any existing Flask processes
pkill -f "python app.py" 2>/dev/null
sleep 2

# Start Flask
python app.py > /tmp/flask_output.log 2>&1 &
echo "Flask starting..."
sleep 4

# Test API
echo ""
echo "Testing /health endpoint:"
curl -s http://localhost:5000/health
echo ""
echo ""
echo "Testing /api/stocks endpoint:"
curl -s http://localhost:5000/api/stocks | head -100
