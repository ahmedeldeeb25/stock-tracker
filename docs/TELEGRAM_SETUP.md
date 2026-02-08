# Telegram Notifications Setup Guide

## Overview
The Stock Tracker now supports Telegram notifications in addition to email alerts. You'll receive instant messages on Telegram whenever your price targets are met.

## Features
- ✅ Real-time notifications via Telegram
- ✅ Rich formatting with HTML support
- ✅ Works alongside email notifications
- ✅ Easy setup with @BotFather
- ✅ Secure token-based authentication

## Setup Instructions

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a chat and send: `/newbot`
3. Follow the prompts:
   - Choose a name for your bot (e.g., "My Stock Tracker")
   - Choose a username (must end in 'bot', e.g., "mystocktracker_bot")
4. **Save the bot token** provided by BotFather (it looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

1. Send any message to your new bot (e.g., "/start" or "hello")
2. Open your browser and visit:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Replace `<YOUR_BOT_TOKEN>` with the token from Step 1

3. Look for the `"chat"` section in the JSON response:
   ```json
   "chat": {
     "id": 123456789,
     "first_name": "Your Name",
     ...
   }
   ```
4. **Save your chat ID** (the number after `"id"`)

### Step 3: Configure Environment Variables

1. Open your `.env` file (or create one from `.env.example`)
2. Add your Telegram credentials:
   ```bash
   # Telegram Configuration
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

### Step 4: Test Your Setup

Run the test script to verify everything is working:

```bash
python test_telegram.py
```

You should see:
```
🤖 Telegram Notification Test
==================================================
Bot Token: ********************GHIjklMNOp
Chat ID: 123456789

Testing bot connection...
✅ Bot connection successful!

Sending test message...
✅ Test message sent successfully!

Check your Telegram to see the message.
Your Telegram notifications are configured correctly! 🎊
```

### Step 5: Start the Daemon

Once configured, start the daemon to begin receiving notifications:

```bash
python daemon.py
```

or use the start script:

```bash
./start_daemon.sh
```

## How It Works

### Notification Flow

1. **Price Check**: The daemon checks stock prices every hour during market hours
2. **Target Match**: If a price target is met, an alert is created
3. **Multi-Channel Send**: Notifications are sent via:
   - ✉️ Email (if configured)
   - 📱 Telegram (if configured)
4. **Delivery**: You receive the alert on both channels

### Message Format

Telegram messages are formatted with HTML for better readability:

```
🔔 Stock Alert: 2 Target(s) Met
══════════════════════════════

1. AAPL
Target Type: Buy
Current Price: $145.00
Target Price: $150.00
Price dropped below target! Consider buying.

──────────────────────────────

2. TSLA
Target Type: Sell
Current Price: $255.00
Target Price: $250.00
Price rose above target! Consider selling.

📱 Automated message from Stock Tracker
```

## Configuration Options

### Both Email and Telegram (Recommended)
Configure both channels for redundancy:
- Email notifications work even if Telegram is down
- Telegram notifications are instant and mobile-friendly

### Telegram Only
To use only Telegram notifications:
1. Configure Telegram credentials in `.env`
2. Leave email credentials empty or remove them

### Disable Telegram
To disable Telegram notifications:
1. Remove or comment out Telegram credentials in `.env`:
   ```bash
   # TELEGRAM_BOT_TOKEN=your-token-here
   # TELEGRAM_CHAT_ID=your-chat-id-here
   ```

## Troubleshooting

### Bot doesn't respond
- **Issue**: Bot doesn't send messages
- **Solution**:
  - Verify bot token is correct
  - Make sure you've sent at least one message to the bot
  - Check that chat ID is correct (it should be a number)

### "Unauthorized" error
- **Issue**: API returns 401 Unauthorized
- **Solution**:
  - Double-check your bot token
  - Make sure there are no extra spaces in `.env`
  - Generate a new token from @BotFather if needed

### "Chat not found" error
- **Issue**: Bot can't find the chat
- **Solution**:
  - Verify chat ID is correct
  - Send a message to your bot first
  - Use the `/getUpdates` endpoint to get the correct chat ID

### Test script fails
- **Issue**: `test_telegram.py` shows errors
- **Solution**:
  - Check that `.env` file exists and has correct values
  - Verify you have `requests` library installed: `pip install requests`
  - Check internet connection

### No notifications received
- **Issue**: Daemon runs but no Telegram messages
- **Solution**:
  - Check daemon logs: `tail -f stock_tracker.log`
  - Verify targets are active in the database
  - Run test script to verify credentials
  - Check that bot isn't blocked

## API Reference

### TelegramNotifier Class

```python
from src.telegram_notifier import TelegramNotifier

# Initialize
notifier = TelegramNotifier(
    bot_token="your-bot-token",
    chat_id="your-chat-id"
)

# Test connection
if notifier.test_connection():
    print("Connected!")

# Send simple message
notifier.send_message("<b>Hello</b> from Stock Tracker!")

# Send alert
notifier.send_alert(
    subject="Price Alert",
    body="AAPL reached target price"
)

# Send multiple alerts (used by daemon)
alerts = [alert1, alert2, alert3]
notifier.send_multiple_alerts(alerts)
```

## Security Notes

### Protecting Your Bot Token
- ✅ Never commit your bot token to version control
- ✅ Keep `.env` file in `.gitignore`
- ✅ Use environment variables for production
- ✅ Regenerate token if accidentally exposed

### Privacy
- Your bot token and chat ID are private
- Only you can send messages to your bot
- Messages are sent directly to your Telegram account
- No data is stored by Telegram Bot API for these notifications

## Advanced Usage

### Group Notifications
To send alerts to a Telegram group:
1. Add your bot to the group
2. Make the bot an admin (optional, but recommended)
3. Get the group chat ID (it will be negative, like `-123456789`)
4. Use the group chat ID in your `.env` file

### Multiple Recipients
To send to multiple people:
- **Option 1**: Create a Telegram group and add everyone
- **Option 2**: Run multiple daemon instances with different chat IDs
- **Option 3**: Modify `telegram_notifier.py` to support multiple chat IDs

### Custom Formatting
Edit `telegram_notifier.py` line 67-102 to customize message format:
- Change emojis
- Adjust formatting
- Add more details
- Include charts or links

## Files Modified

- **Created**:
  - `src/telegram_notifier.py` - Telegram notification implementation
  - `test_telegram.py` - Test script for verification
  - `docs/TELEGRAM_SETUP.md` - This guide

- **Modified**:
  - `src/config.py` - Added Telegram configuration support
  - `daemon.py` - Integrated Telegram notifications
  - `.env.example` - Added Telegram credentials template

## Benefits

### Why Use Telegram?
1. **Instant Delivery**: Messages arrive in seconds
2. **Mobile-Friendly**: Native mobile apps for iOS/Android
3. **Rich Formatting**: Support for bold, code, links, etc.
4. **Reliable**: 99.9% uptime, worldwide infrastructure
5. **Free**: No cost for bot API usage
6. **No Setup Hassles**: No SMTP servers or email configuration
7. **Cross-Platform**: Works on phone, tablet, desktop, web

### Comparison with Email

| Feature | Telegram | Email |
|---------|----------|-------|
| Delivery Speed | Instant (1-2s) | Variable (5-60s) |
| Mobile Notifications | ✅ Push | ✅ Push |
| Rich Formatting | ✅ HTML | ✅ HTML |
| Setup Complexity | Easy | Moderate |
| Spam Filtering | Never | Sometimes |
| Read Receipts | ✅ Yes | ❌ No |
| Archive/Search | ✅ Yes | ✅ Yes |

## Future Enhancements

Potential features for future versions:
- Interactive buttons (e.g., "Mark as read", "Disable target")
- Charts and price graphs
- Voice messages for critical alerts
- Scheduled digest messages
- Custom notification preferences per stock
- Integration with Telegram channels for public alerts

---

**Need Help?**
- Check the logs: `tail -f stock_tracker.log`
- Run the test script: `python test_telegram.py`
- Review Telegram Bot API docs: https://core.telegram.org/bots/api

**Created**: February 2026
**Status**: ✅ Production Ready
