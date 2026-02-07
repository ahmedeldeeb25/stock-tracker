#!/bin/bash
# Script to stop the stock tracker daemon

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/stock_tracker.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Stock tracker daemon is not running (no PID file found)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "Stopping stock tracker daemon (PID: $PID)..."
    kill $PID
    rm "$PID_FILE"
    echo "Stock tracker daemon stopped"
else
    echo "Stock tracker daemon is not running (stale PID file)"
    rm "$PID_FILE"
fi
