# Stock Tracker

A modular Python application that monitors stock prices and sends email notifications when price targets are met.

## Features

- **Multiple Target Types**: Support for Buy, Sell, DCA (Dollar Cost Averaging), and Trim alerts
- **Flexible Alert Logic**:
  - Buy/DCA: Alert when price drops below target
  - Sell/Trim: Alert when price rises above target
- **SQLite Database**: Persistent storage for stocks, targets, notes, and alert history
- **Web Interface**: Vue.js frontend with rich text notes and real-time price updates
- **Email Notifications**: Automated alerts via SMTP
- **Modular Architecture**: Easy to extend and maintain

## Project Structure

```
stock-tracker/
├── .claude/                   # AI assistant context & session history
│   ├── CLAUDE.md             # AI collaboration guide
│   ├── sessions/             # Session handovers
│   ├── context/              # Project context files
│   └── guides/               # Patterns & best practices
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── db_manager.py          # Database operations (SQLite)
│   ├── stock_fetcher.py       # Stock price fetching (yfinance)
│   ├── stock_service.py       # Business logic layer
│   ├── alert_checker.py       # Alert logic
│   ├── email_notifier.py      # Email notifications (smtplib)
│   └── models.py              # Data models
├── web/
│   ├── app.py                 # Flask REST API
│   ├── routes/                # API routes
│   └── frontend/              # Vue.js frontend
├── scripts/
│   ├── start_daemon.sh        # Start daemon script
│   ├── stop_daemon.sh         # Stop daemon script
│   ├── status_daemon.sh       # Check daemon status
│   ├── start_all.sh           # Start all services
│   ├── start_web.sh           # Start web server
│   ├── start_frontend.sh      # Start frontend dev server
│   ├── fresh_start.sh         # Fresh start script
│   └── test_flask.sh          # Test Flask server
├── daemon.py                  # Background daemon mode
├── cli.py                     # Command-line interface
├── stock_tracker.db           # SQLite database
└── requirements.txt           # Python dependencies
```

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure email settings**:

   Option A: Using `.env` file (recommended):
   ```bash
   cp .env.example .env
   # Edit .env with your email credentials
   ```

   Option B: Edit `config.json` directly:
   ```json
   {
     "email": {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender_email": "your-email@gmail.com",
       "sender_password": "your-app-password",
       "recipient_email": "recipient@example.com"
     }
   }
   ```

   **Note for Gmail users**: Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

4. **Add stocks to your watchlist**:

   Using the CLI:
   ```bash
   python3 cli.py add AAPL --target-type Buy --target-price 150.00
   python3 cli.py add NVDA --target-type Sell --target-price 800.00
   ```

   Or use the Web Interface (see Web Setup section below).

## Usage

### Option 1: Run in Background (Recommended)

Start the daemon to continuously monitor stocks:

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start the background daemon
./scripts/start_daemon.sh

# Check daemon status
./scripts/status_daemon.sh

# Stop the daemon
./scripts/stop_daemon.sh
```

The daemon will check prices every hour from 9 AM to 5 PM.

### Option 2: CLI Commands

Use the CLI to interact with the tracker:

```bash
# Get current price for a specific ticker
python cli.py price AAPL
python cli.py price HIMS

# Check status of all monitored stocks
python cli.py status

# View recent logs
python cli.py logs
python cli.py logs --lines 100

# List all stocks in watchlist
python cli.py list

# Add a stock to watchlist
python cli.py add NVDA Buy 800.00
python cli.py add TSLA Trim 250.00 --trim-percentage 30

# Remove a stock from watchlist
python cli.py remove NVDA
python cli.py remove TSLA --target-type Trim

# Run a manual check
python cli.py check
```

### Price Target Fields

When adding stocks, you can specify the following:

- `symbol` (required): Stock ticker symbol (e.g., "AAPL")
- `target_type` (required): One of "Buy", "Sell", "DCA", or "Trim"
- `target_price` (required): Target price in USD
- `trim_percentage` (optional): Percentage to sell (only for "Trim" type)

### Target Types Explained

- **Buy**: Alert when price drops to or below target (good entry point)
- **DCA**: Alert when price drops to or below target (dollar-cost averaging opportunity)
- **Sell**: Alert when price rises to or above target (take profits)
- **Trim**: Alert when price rises to or above target (sell a specific percentage)

## Running as a System Service (macOS)

To run the tracker as a permanent system service that starts on boot:

1. **Edit the plist file** `com.user.stocktracker.plist`:
   - Replace `ABSOLUTE_PATH_TO_PROJECT` with your actual project path
   - Replace `/usr/local/bin/python3` with your Python path (find with `which python3`)

2. **Install the service**:
```bash
# Copy to LaunchAgents
cp com.user.stocktracker.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.user.stocktracker.plist

# Start the service
launchctl start com.user.stocktracker
```

3. **Manage the service**:
```bash
# Check status
launchctl list | grep stocktracker

# Stop the service
launchctl stop com.user.stocktracker

# Unload the service
launchctl unload ~/Library/LaunchAgents/com.user.stocktracker.plist
```

### Alternative: Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Run every hour during market hours (9 AM - 5 PM EST, Mon-Fri)
0 9-17 * * 1-5 cd /path/to/stock-tracker && python main.py
```

### Windows Task Scheduler
Create a task that runs `python daemon.py` at startup.

## Extending the Application

The modular design makes it easy to add new features:

### Adding a new data source:
Create a new class implementing the same interface as `StockFetcher`:
```python
class AlphaVantageFetcher:
    def get_current_price(self, symbol: str) -> Optional[float]:
        # Your implementation
        pass
```

### Adding a UI:
Import the modules in your UI code:
```python
from src.db_manager import DatabaseManager
from src.stock_fetcher import StockFetcher
from src.stock_service import StockService
from src.alert_checker import AlertChecker

# Use the modules in your UI framework
```

### Adding more notification methods:
Create a new notifier class similar to `EmailNotifier`:
```python
class SlackNotifier:
    def send_alert(self, message: str):
        # Send to Slack
        pass
```

## Logging

Logs are written to:
- `stock_tracker.log` - All log entries
- `stock_tracker_error.log` - Errors only (when using launchd)

View logs using:
```bash
# View recent logs
python cli.py logs

# View last 100 lines
python cli.py logs --lines 100

# Tail logs in real-time
tail -f stock_tracker.log
```

## Security Notes

- Never commit `.env` or `config.json` with real credentials
- Use app-specific passwords for email services
- Consider using environment variables in production
- The `.gitignore` file is configured to exclude sensitive files

## License

This project is provided as-is for educational and personal use.
