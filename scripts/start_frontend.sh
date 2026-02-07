#!/bin/bash
# Start Vue.js frontend development server

cd /Users/aeldeeb/Ahmed/git/stock-tracker/web/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies (first time only)..."
    npm install
    echo ""
fi

echo "🚀 Starting Vue.js development server..."
echo "Frontend will run on: http://localhost:5173"
echo "API backend should be running on: http://localhost:5555"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
