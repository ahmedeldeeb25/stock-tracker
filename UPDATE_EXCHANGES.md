# Updating Stock Exchange Information

## Problem
When stocks were added to the system before the exchange field was implemented, they don't have exchange information stored. This causes incorrect links to Google Finance (e.g., HIMS on NYSE being linked as NASDAQ:HIMS).

## Solution
There are two ways to update exchange information for all existing stocks:

---

## Option 1: Web UI (Recommended)

This is the easiest method for most users.

### Steps:
1. **Start the backend server**:
   ```bash
   python3 web/app.py
   ```

2. **Open the dashboard** in your web browser

3. **Click the "Update Exchanges" button** in the top filter bar (next to "Refresh Prices")

4. **Wait for completion** - The system will:
   - Fetch exchange information from yfinance for all stocks without exchange data
   - Update the database
   - Show a success message with the results

5. **Refresh the page** - Your stocks will now link to the correct exchange on Google Finance

### What the button does:
- Finds all stocks missing exchange information
- Fetches the correct exchange (NYSE, NASDAQ, etc.) from yfinance
- Updates each stock in the database
- Skips stocks that already have exchange information
- Shows detailed results (updated, skipped, failed)

---

## Option 2: Command Line Script

For advanced users or batch processing.

### Steps:
1. **Navigate to the project directory**:
   ```bash
   cd /path/to/stock-tracker
   ```

2. **Run the update script**:
   ```bash
   python3 update_exchanges.py
   ```

3. **Monitor the output** - You'll see:
   ```
   INFO: Fetching exchange for HIMS...
   INFO: ✓ Updated HIMS: NYSE - Hims & Hers Health Inc
   INFO: Fetching exchange for AAPL...
   INFO: ✓ Updated AAPL: NASDAQ - Apple Inc.
   ...
   ```

4. **View the summary**:
   ```
   ==================================================
   Exchange Update Summary
   ==================================================
   Total stocks: 10
   Updated: 8
   Skipped (already had exchange): 2
   Failed: 0
   ==================================================
   ```

### Script features:
- Automatic rate limiting (1 second delay between requests)
- Skips stocks that already have exchange data
- Updates both exchange and company name if missing
- Detailed logging of all operations
- Error handling for failed updates

---

## API Endpoint (For Developers)

The exchange update functionality is also available as an API endpoint:

```
POST /api/stocks/batch/update-exchanges
```

### Example using curl:
```bash
curl -X POST http://localhost:5555/api/stocks/batch/update-exchanges \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: YOUR_CSRF_TOKEN"
```

### Response:
```json
{
  "message": "Exchange update completed",
  "total": 10,
  "updated": 8,
  "skipped": 2,
  "failed": 0,
  "results": [
    {
      "symbol": "HIMS",
      "exchange": "NYSE",
      "status": "updated"
    },
    ...
  ]
}
```

---

## Verification

After updating exchanges, verify the changes:

### 1. Check the database:
```bash
sqlite3 stock_tracker.db "SELECT symbol, exchange FROM stocks;"
```

Expected output:
```
HIMS|NYSE
AAPL|NASDAQ
TSLA|NASDAQ
...
```

### 2. Check Google Finance links:
- Go to any stock detail page
- Click on the stock symbol (links to Google Finance)
- Verify it opens the correct exchange page

---

## Common Issues

### Issue: "Could not fetch exchange for SYMBOL"
**Cause**: yfinance couldn't retrieve data for that symbol
**Solution**:
- Verify the symbol is correct
- Try again later (yfinance API might be temporarily down)
- Manually update in database if needed:
  ```sql
  UPDATE stocks SET exchange = 'NYSE' WHERE symbol = 'HIMS';
  ```

### Issue: Button shows "Updating..." forever
**Cause**: Backend request timeout or error
**Solution**:
- Check backend logs for errors
- Refresh the page
- Try the command-line script instead

### Issue: Some stocks still show wrong exchange
**Cause**: yfinance returned incorrect exchange data
**Solution**: Manually correct in the database or re-run the update

---

## Notes

- **Rate Limiting**: The update process includes delays to avoid overwhelming the yfinance API
- **One-time Operation**: You only need to run this once for existing stocks. New stocks automatically get exchange data when fetched.
- **No Data Loss**: The update only adds exchange information - it doesn't modify existing data
- **Safe to Re-run**: Running the update multiple times is safe - it skips stocks that already have exchange data

---

## Future

Once all stocks have exchange information:
- Google Finance links will always use the correct exchange
- TradingView widgets will show accurate data
- New stocks will automatically capture exchange on creation
