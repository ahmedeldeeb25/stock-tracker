#!/bin/bash
# Script to check the status of the stock tracker daemon

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/stock_tracker.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Stock tracker daemon is NOT running"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Stock tracker daemon is running (PID: $PID)"
    echo ""
    echo "Recent activity:"
    tail -n 10 "$SCRIPT_DIR/stock_tracker.log"
else
    echo "❌ Stock tracker daemon is NOT running (stale PID file)"
    rm "$PID_FILE"
    exit 1
fi
