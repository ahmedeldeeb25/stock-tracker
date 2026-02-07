# Stock Tracker - Quick Reference

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure email (edit `.env` or `config.json`)

3. Start the background daemon:
   ```bash
   ./scripts/start_daemon.sh
   ```

## 📋 Common Commands

### Daemon Control
```bash
./scripts/start_daemon.sh      # Start monitoring in background
./scripts/stop_daemon.sh       # Stop the daemon
./scripts/status_daemon.sh     # Check if daemon is running
```

### Check Prices
```bash
python cli.py price AMZN     # Get current price for AMZN
python cli.py price HIMS     # Get current price for HIMS
python cli.py status         # Check all stocks and targets
```

### View Logs
```bash
python cli.py logs           # View recent logs
python cli.py logs -n 100    # View last 100 lines
tail -f stock_tracker.log    # Live log streaming
```

### Manage Watchlist
```bash
python cli.py list                              # Show all stocks
python cli.py add AAPL Buy 150.00              # Add buy target
python cli.py add TSLA Trim 300 --trim-percentage 25  # Add trim target
python cli.py remove AAPL                       # Remove all AAPL entries
python cli.py remove TSLA --target-type Buy    # Remove specific target
```

### Manual Check
```bash
python cli.py check    # Run one-time check and send alerts
```

## 📊 Example Workflow

```bash
# 1. Start the daemon
./scripts/start_daemon.sh

# 2. Check what's being monitored
python cli.py status

# 3. Check current price for a specific stock
python cli.py price NVDA

# 4. Add a new stock to watch
python cli.py add NVDA Sell 900.00

# 5. View recent activity
python cli.py logs -n 20

# 6. Check daemon is running
./scripts/status_daemon.sh
```

## 🔧 Customization

### Change Check Frequency
Edit `daemon.py` line 70-72 to customize hours:
```python
for hour in range(9, 18):  # 9 AM to 5 PM
    schedule.every().day.at(f"{hour:02d}:00").do(check_stocks)
```

### Check Every 30 Minutes
Replace the schedule section in `daemon.py` with:
```python
schedule.every(30).minutes.do(check_stocks)
```

## 📧 Email Setup (Gmail)

1. Enable 2-factor authentication on Google account
2. Generate app password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-16-char-app-password
   RECIPIENT_EMAIL=where-to-send@example.com
   ```

## 🐛 Troubleshooting

### Daemon won't start
```bash
# Check if already running
ps aux | grep daemon.py

# Check logs for errors
tail -n 50 stock_tracker.log

# Kill any stuck processes
pkill -f daemon.py
rm stock_tracker.pid
```

### Can't fetch prices
- Check internet connection
- Verify stock symbols are correct
- Check if yfinance is working: `python -c "import yfinance; print(yfinance.Ticker('AAPL').history(period='1d'))"`

### Not receiving emails
- Check email credentials in `.env`
- Look for error messages in logs: `python cli.py logs | grep -i email`
- Test SMTP connection manually

## 📁 File Locations

- Database: `stock_tracker.db`
- Configuration: `config.json` or `.env`
- Logs: `stock_tracker.log`
- Process ID: `stock_tracker.pid`
