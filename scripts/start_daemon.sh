#!/bin/bash
# Script to start the stock tracker daemon in the background

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/stock_tracker.pid"
LOG_FILE="$SCRIPT_DIR/stock_tracker.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stock tracker daemon is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Start the daemon
echo "Starting stock tracker daemon..."
nohup python3 daemon.py >> "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

echo "Stock tracker daemon started (PID: $PID)"
echo "Logs: $LOG_FILE"
echo ""
echo "To stop: ./stop_daemon.sh"
echo "To check status: ./status_daemon.sh"
