"""Stock price fetching using yfinance."""

import yfinance as yf
from typing import Dict, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class StockFetcher:
    """Fetches current stock prices using yfinance."""

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
            Dictionary with company info (name, sector, industry) or None if failed
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

            # Extract relevant info
            company_info = {
                'name': company_name,
                'sector': info.get('sector', ''),
                'industry': info.get('industry', '')
            }

            logger.info(f"Fetched info for {symbol}: {company_info['name']}")
            return company_info

        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}", exc_info=True)
            return None

    def get_multiple_prices(self, symbols: list) -> Dict[str, Optional[float]]:
        """Get current prices for multiple stocks.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary mapping symbols to prices
        """
        prices = {}
        for symbol in symbols:
            prices[symbol] = self.get_current_price(symbol)
        return prices

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
