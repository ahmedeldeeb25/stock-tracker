#!/bin/bash
# Complete startup script - Start both backend and frontend

cd /Users/aeldeeb/Ahmed/git/stock-tracker

echo "╔════════════════════════════════════════════════════╗"
echo "║     Stock Tracker - Complete Startup              ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check if Flask is already running
if lsof -ti:5555 > /dev/null 2>&1; then
    echo "✅ Flask API already running on port 5555"
else
    echo "🔧 Starting Flask API..."
    cd web
    source ../venv/bin/activate
    nohup python app.py > /tmp/flask.log 2>&1 &
    sleep 4

    if lsof -ti:5555 > /dev/null 2>&1; then
        echo "✅ Flask API started on http://localhost:5555"
    else
        echo "❌ Failed to start Flask API"
        echo "Check logs: tail /tmp/flask.log"
        exit 1
    fi
    cd ..
fi

echo ""
echo "🚀 Starting Vue.js frontend..."
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:5555"
echo ""
echo "Press Ctrl+C to stop the frontend"
echo "To stop Flask: pkill -f 'python app.py'"
echo ""

./start_frontend.sh
