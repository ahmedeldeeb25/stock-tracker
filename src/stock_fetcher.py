"""Stock price fetching using yfinance."""

import yfinance as yf
import requests
from typing import Dict, Optional, List
import logging
import pandas as pd
import concurrent.futures
import time

logger = logging.getLogger(__name__)


class StockFetcher:
    """Fetches current stock prices using yfinance with caching."""

    def __init__(self, cache_ttl: int = 60):
        """Initialize stock fetcher with cache.

        Args:
            cache_ttl: Cache time-to-live in seconds (default 60)
        """
        self._cache = {}
        self._cache_ttl = cache_ttl
        logger.info(f"StockFetcher initialized with {cache_ttl}s cache TTL")

    def _get_cached_or_fetch(self, key: str, fetch_func, ttl: int = None):
        """Generic cache wrapper.

        Args:
            key: Cache key
            fetch_func: Function to call if cache miss
            ttl: Optional override for cache TTL

        Returns:
            Cached or freshly fetched data
        """
        ttl = ttl or self._cache_ttl
        now = time.time()

        # Check cache
        if key in self._cache:
            cached_data, timestamp = self._cache[key]
            if now - timestamp < ttl:
                logger.debug(f"Cache hit for {key}")
                return cached_data

        # Cache miss - fetch fresh data
        logger.debug(f"Cache miss for {key}, fetching...")
        data = fetch_func()
        self._cache[key] = (data, now)
        return data

    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get the current price for a stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Current price or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')

            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None

            current_price = data['Close'].iloc[-1]
            logger.info(f"{symbol}: ${current_price:.2f}")
            return float(current_price)

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_rsi(self, symbol: str, period: int = 14) -> Optional[float]:
        """Calculate RSI (Relative Strength Index) for a stock.

        Args:
            symbol: Stock ticker symbol
            period: RSI period (default 14 days)

        Returns:
            RSI value (0-100) or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            # Get enough historical data (need period + 1 for calculation)
            data = ticker.history(period='3mo')

            if data.empty or len(data) < period + 1:
                logger.warning(f"Insufficient data for RSI calculation: {symbol}")
                return None

            # Calculate price changes
            delta = data['Close'].diff()

            # Separate gains and losses
            gains = delta.copy()
            losses = delta.copy()
            gains[gains < 0] = 0
            losses[losses > 0] = 0
            losses = abs(losses)

            # Calculate average gains and losses
            avg_gains = gains.rolling(window=period).mean()
            avg_losses = losses.rolling(window=period).mean()

            # Calculate RS and RSI
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))

            # Get the most recent RSI value
            current_rsi = rsi.iloc[-1]

            if pd.isna(current_rsi):
                logger.warning(f"RSI calculation resulted in NaN for {symbol}")
                return None

            logger.info(f"{symbol} RSI: {current_rsi:.2f}")
            return float(current_rsi)

        except Exception as e:
            logger.error(f"Error calculating RSI for {symbol}: {e}", exc_info=True)
            return None

    def get_company_info(self, symbol: str) -> Optional[Dict[str, str]]:
        """Get company information for a stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dictionary with company info (name, sector, industry, exchange) or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)

            # Try to get info - this can be slow, so we add a timeout
            info = ticker.info

            if not info or not isinstance(info, dict):
                logger.warning(f"No valid info available for {symbol}")
                return None

            # Extract company name - try multiple fields
            company_name = (
                info.get('longName') or
                info.get('shortName') or
                info.get('name') or
                ''
            )

            if not company_name:
                logger.warning(f"No company name found for {symbol}")
                return None

            # Extract exchange - try multiple fields
            exchange = (
                info.get('exchange') or
                info.get('exchangeName') or
                ''
            )

            # Extract relevant info
            company_info = {
                'name': company_name,
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'exchange': exchange if exchange else None
            }

            logger.info(f"Fetched info for {symbol}: {company_info['name']} ({company_info['exchange']})")
            return company_info

        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}", exc_info=True)
            return None

    def get_multiple_prices(self, symbols: list) -> Dict[str, Optional[float]]:
        """Get current prices for multiple stocks using batch download with caching.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary mapping symbols to prices
        """
        if not symbols:
            return {}

        # Create cache key from sorted symbols
        cache_key = f"prices_{'_'.join(sorted(symbols))}"

        def fetch_prices():
            try:
                # Use yfinance.download for faster batch fetching
                logger.info(f"Fetching prices for {len(symbols)} stocks in batch...")
                data = yf.download(
                    tickers=' '.join(symbols),
                    period='1d',
                    group_by='ticker',
                    threads=True,  # Enable multi-threading
                    progress=False,
                    show_errors=False
                )

                prices = {}
                for symbol in symbols:
                    try:
                        if len(symbols) == 1:
                            # Single ticker returns different structure
                            if not data.empty and 'Close' in data:
                                prices[symbol] = float(data['Close'].iloc[-1])
                            else:
                                prices[symbol] = None
                        else:
                            # Multiple tickers
                            if symbol in data and not data[symbol].empty:
                                prices[symbol] = float(data[symbol]['Close'].iloc[-1])
                            else:
                                logger.warning(f"No data for {symbol}")
                                prices[symbol] = None
                    except Exception as e:
                        logger.warning(f"Error processing {symbol}: {e}")
                        prices[symbol] = None

                logger.info(f"Batch fetch completed: {len([p for p in prices.values() if p])} successful")
                return prices

            except Exception as e:
                logger.error(f"Error in batch download: {e}")
                # Fallback to individual fetching
                logger.info("Falling back to sequential fetching...")
                prices = {}
                for symbol in symbols:
                    prices[symbol] = self.get_current_price(symbol)
                return prices

        return self._get_cached_or_fetch(cache_key, fetch_prices, ttl=60)

    def get_multiple_info(self, symbols: list) -> Dict[str, Optional[dict]]:
        """Get ticker.info for multiple stocks in parallel with caching.

        This is much faster than calling get_after_hours_price() or ticker.info
        sequentially for each stock. Use this when you need info for multiple stocks.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary mapping symbols to ticker.info dictionaries
        """
        if not symbols:
            return {}

        # Create cache key from sorted symbols
        cache_key = f"info_{'_'.join(sorted(symbols))}"

        def fetch_info():
            logger.info(f"Fetching ticker info for {len(symbols)} stocks in parallel...")

            def fetch_single_info(symbol: str) -> tuple:
                """Fetch info for a single symbol."""
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    if info and isinstance(info, dict):
                        return (symbol, info)
                    else:
                        logger.warning(f"No valid info for {symbol}")
                        return (symbol, None)
                except Exception as e:
                    logger.error(f"Error fetching info for {symbol}: {e}")
                    return (symbol, None)

            # Fetch all in parallel using ThreadPoolExecutor
            info_dict = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_symbol = {
                    executor.submit(fetch_single_info, symbol): symbol
                    for symbol in symbols
                }

                for future in concurrent.futures.as_completed(future_to_symbol):
                    try:
                        symbol, info = future.result()
                        info_dict[symbol] = info
                    except Exception as e:
                        symbol = future_to_symbol[future]
                        logger.error(f"Error processing info for {symbol}: {e}")
                        info_dict[symbol] = None

            successful = len([i for i in info_dict.values() if i])
            logger.info(f"Info fetch completed: {successful}/{len(symbols)} successful")
            return info_dict

        return self._get_cached_or_fetch(cache_key, fetch_info, ttl=60)

    def get_after_hours_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get after-hours price information for a stock.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dictionary with after-hours price info or None if not available
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or not isinstance(info, dict):
                logger.warning(f"No valid info available for {symbol}")
                return None

            result = {}

            # Check for post-market (after-hours) price
            if 'postMarketPrice' in info and info['postMarketPrice']:
                result['price'] = float(info['postMarketPrice'])
                result['change'] = float(info.get('postMarketChange', 0))
                result['change_percent'] = float(info.get('postMarketChangePercent', 0))
                result['time'] = info.get('postMarketTime', '')
                logger.info(f"{symbol} after-hours: ${result['price']:.2f}")
                return result

            # Check for pre-market price
            if 'preMarketPrice' in info and info['preMarketPrice']:
                result['price'] = float(info['preMarketPrice'])
                result['change'] = float(info.get('preMarketChange', 0))
                result['change_percent'] = float(info.get('preMarketChangePercent', 0))
                result['time'] = info.get('preMarketTime', '')
                result['is_premarket'] = True
                logger.info(f"{symbol} pre-market: ${result['price']:.2f}")
                return result

            logger.info(f"No after-hours data available for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error fetching after-hours price for {symbol}: {e}")
            return None

    def get_fundamental_data(self, symbol: str) -> Optional[Dict[str, any]]:
        """Get comprehensive fundamental and technical data for a stock.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dictionary with fundamental data or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or not isinstance(info, dict):
                logger.warning(f"No valid info available for {symbol}")
                return None

            # Extract fundamental data
            fundamental_data = {
                # Valuation Metrics
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                'enterprise_to_ebitda': info.get('enterpriseToEbitda'),

                # Risk & Performance Metrics
                'beta': info.get('beta'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_day_average': info.get('fiftyDayAverage'),
                'two_hundred_day_average': info.get('twoHundredDayAverage'),

                # Trading Information
                'volume': info.get('volume'),
                'average_volume': info.get('averageVolume'),
                'average_volume_10days': info.get('averageVolume10days'),
                'bid': info.get('bid'),
                'ask': info.get('ask'),
                'bid_size': info.get('bidSize'),
                'ask_size': info.get('askSize'),

                # Dividend Information
                'dividend_rate': info.get('dividendRate'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'ex_dividend_date': info.get('exDividendDate'),

                # Profitability
                'profit_margins': info.get('profitMargins'),
                'operating_margins': info.get('operatingMargins'),
                'gross_margins': info.get('grossMargins'),
                'return_on_assets': info.get('returnOnAssets'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue': info.get('totalRevenue'),
                'revenue_per_share': info.get('revenuePerShare'),

                # Financial Health
                'total_cash': info.get('totalCash'),
                'total_debt': info.get('totalDebt'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'free_cashflow': info.get('freeCashflow'),
                'operating_cashflow': info.get('operatingCashflow'),

                # Earnings
                'earnings_growth': info.get('earningsGrowth'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
                'trailing_eps': info.get('trailingEps'),
                'forward_eps': info.get('forwardEps'),

                # Analyst Recommendations
                'recommendation': info.get('recommendationKey'),
                'target_high_price': info.get('targetHighPrice'),
                'target_low_price': info.get('targetLowPrice'),
                'target_mean_price': info.get('targetMeanPrice'),
                'target_median_price': info.get('targetMedianPrice'),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),

                # Company Info
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'full_time_employees': info.get('fullTimeEmployees'),
                'website': info.get('website'),
                'long_business_summary': info.get('longBusinessSummary'),
            }

            # Get earnings date if available
            try:
                calendar = ticker.calendar
                if calendar is not None and not calendar.empty:
                    if 'Earnings Date' in calendar.index:
                        earnings_dates = calendar.loc['Earnings Date']
                        if isinstance(earnings_dates, pd.Series) and len(earnings_dates) > 0:
                            fundamental_data['earnings_date'] = earnings_dates.iloc[0].isoformat() if pd.notna(earnings_dates.iloc[0]) else None
            except Exception as e:
                logger.warning(f"Could not fetch earnings calendar for {symbol}: {e}")

            logger.info(f"Fetched fundamental data for {symbol}")
            return fundamental_data

        except Exception as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {e}", exc_info=True)
            return None

    def search_symbols(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search for stock symbols using Yahoo Finance search API.

        Args:
            query: Search query (partial symbol or company name)
            limit: Maximum number of results to return

        Returns:
            List of dicts with symbol, name, exchange, and type
        """
        if not query or len(query) < 1:
            return []

        cache_key = f"search_{query.upper()}_{limit}"

        def fetch_search():
            try:
                url = "https://query1.finance.yahoo.com/v1/finance/search"
                params = {
                    "q": query,
                    "quotesCount": limit,
                    "newsCount": 0,
                    "listsCount": 0,
                    "enableFuzzyQuery": False,
                    "quotesQueryId": "tss_match_phrase_query"
                }
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                response = requests.get(url, params=params, headers=headers, timeout=5)
                response.raise_for_status()
                data = response.json()

                results = []
                for quote in data.get("quotes", []):
                    # Only include stocks and ETFs
                    quote_type = quote.get("quoteType", "")
                    if quote_type in ["EQUITY", "ETF"]:
                        results.append({
                            "symbol": quote.get("symbol", ""),
                            "name": quote.get("shortname") or quote.get("longname", ""),
                            "exchange": quote.get("exchange", ""),
                            "type": quote_type
                        })

                logger.info(f"Search for '{query}' returned {len(results)} results")
                return results

            except Exception as e:
                logger.error(f"Error searching for symbols: {e}")
                return []

        return self._get_cached_or_fetch(cache_key, fetch_search, ttl=300)  # Cache for 5 minutes

    def validate_symbol(self, symbol: str) -> Optional[Dict[str, str]]:
        """Validate if a stock symbol exists and get basic info.

        Args:
            symbol: Stock ticker symbol to validate

        Returns:
            Dict with symbol info if valid, None if invalid
        """
        if not symbol:
            return None

        cache_key = f"validate_{symbol.upper()}"

        def fetch_validation():
            try:
                ticker = yf.Ticker(symbol.upper())
                info = ticker.info

                # Check if we got valid data
                if not info or info.get("regularMarketPrice") is None:
                    # Try to get history as fallback validation
                    hist = ticker.history(period="1d")
                    if hist.empty:
                        logger.info(f"Symbol {symbol} is not valid")
                        return None

                return {
                    "symbol": symbol.upper(),
                    "name": info.get("shortName") or info.get("longName", ""),
                    "exchange": info.get("exchange", ""),
                    "type": info.get("quoteType", "EQUITY"),
                    "valid": True
                }

            except Exception as e:
                logger.error(f"Error validating symbol {symbol}: {e}")
                return None

        return self._get_cached_or_fetch(cache_key, fetch_validation, ttl=3600)  # Cache for 1 hour

    def get_market_overview(self) -> Dict[str, any]:
        """Get market overview data including major indices, VIX, and sentiment indicators.

        Returns:
            Dictionary with market overview data
        """
        cache_key = "market_overview"

        def fetch_market_data():
            result = {
                "indices": {},
                "vix": None,
                "treasury_10y": None,
                "fear_greed": None,
                "updated_at": None
            }

            try:
                # Define symbols to fetch
                symbols = {
                    "SPY": "S&P 500",
                    "QQQ": "NASDAQ 100",
                    "DIA": "Dow Jones",
                    "IWM": "Russell 2000",
                    "^VIX": "VIX",
                    "^TNX": "10Y Treasury"
                }

                # Fetch all data in parallel
                def fetch_single(symbol):
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        hist = ticker.history(period="2d")

                        if hist.empty:
                            return symbol, None

                        current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
                        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price

                        if current_price and prev_close:
                            change = current_price - prev_close
                            change_percent = (change / prev_close) * 100
                        else:
                            change = 0
                            change_percent = 0

                        return symbol, {
                            "price": round(float(current_price), 2) if current_price else None,
                            "change": round(float(change), 2),
                            "change_percent": round(float(change_percent), 2),
                            "name": symbols.get(symbol, symbol)
                        }
                    except Exception as e:
                        logger.error(f"Error fetching {symbol}: {e}")
                        return symbol, None

                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    futures = {executor.submit(fetch_single, sym): sym for sym in symbols.keys()}
                    for future in concurrent.futures.as_completed(futures):
                        symbol, data = future.result()
                        if data:
                            if symbol == "^VIX":
                                result["vix"] = data
                            elif symbol == "^TNX":
                                result["treasury_10y"] = data
                            else:
                                result["indices"][symbol] = data

                # Fetch Fear & Greed Index from CNN
                try:
                    fear_greed = self._fetch_fear_greed_index()
                    if fear_greed:
                        result["fear_greed"] = fear_greed
                except Exception as e:
                    logger.error(f"Error fetching Fear & Greed Index: {e}")

                result["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                logger.info("Market overview data fetched successfully")
                return result

            except Exception as e:
                logger.error(f"Error fetching market overview: {e}")
                return result

        return self._get_cached_or_fetch(cache_key, fetch_market_data, ttl=300)  # Cache for 5 minutes

    def _fetch_fear_greed_index(self) -> Optional[Dict[str, any]]:
        """Fetch CNN Fear & Greed Index.

        Returns:
            Dictionary with fear/greed data or None
        """
        try:
            # CNN Fear & Greed API endpoint
            url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and "fear_and_greed" in data:
                fg_data = data["fear_and_greed"]
                score = fg_data.get("score", 0)

                # Determine sentiment label
                if score <= 25:
                    sentiment = "Extreme Fear"
                elif score <= 45:
                    sentiment = "Fear"
                elif score <= 55:
                    sentiment = "Neutral"
                elif score <= 75:
                    sentiment = "Greed"
                else:
                    sentiment = "Extreme Greed"

                return {
                    "score": round(score),
                    "sentiment": sentiment,
                    "previous_close": round(fg_data.get("previous_close", 0)),
                    "week_ago": round(fg_data.get("previous_1_week", 0)),
                    "month_ago": round(fg_data.get("previous_1_month", 0)),
                    "year_ago": round(fg_data.get("previous_1_year", 0))
                }

            return None

        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            return None
