"""
Kraken Exchange Client - US Accessible
Handles all exchange interactions with proper error handling
"""

import ccxt
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd


class KrakenClient:
    """Kraken exchange client with comprehensive error handling"""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Kraken client

        Args:
            api_key: Kraken API key
            api_secret: Kraken API secret
            testnet: Use testnet (paper trading)
        """
        self.logger = logging.getLogger(__name__)

        try:
            self.exchange = ccxt.kraken({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })

            if testnet:
                self.exchange.set_sandbox_mode(True)
                self.logger.info("Kraken client initialized in TESTNET mode")
            else:
                self.logger.info("Kraken client initialized in LIVE mode")

            # Test connection
            self.exchange.load_markets()
            self.logger.info(f"Connected to Kraken. Available markets: {len(self.exchange.markets)}")

        except Exception as e:
            self.logger.error(f"Failed to initialize Kraken client: {e}")
            raise

    def get_balance(self) -> Dict[str, float]:
        """
        Get account balance

        Returns:
            Dictionary of currency balances
        """
        try:
            balance = self.exchange.fetch_balance()
            return balance['total']
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return {}

    def get_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 100) -> pd.DataFrame:
        """
        Get OHLCV candlestick data

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            timeframe: Timeframe (e.g., '5m', '15m', '1h')
            limit: Number of candles to fetch

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()

    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Get current ticker information

        Args:
            symbol: Trading pair

        Returns:
            Ticker dictionary or None
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None

    def place_market_order(self, symbol: str, side: str, amount: float) -> Optional[Dict]:
        """
        Place market order

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Order amount

        Returns:
            Order information or None
        """
        try:
            order = self.exchange.create_market_order(symbol, side, amount)
            self.logger.info(f"Market {side} order placed: {amount} {symbol}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            return None

    def place_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Optional[Dict]:
        """
        Place limit order

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            amount: Order amount
            price: Limit price

        Returns:
            Order information or None
        """
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            self.logger.info(f"Limit {side} order placed: {amount} {symbol} @ {price}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            return None

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an open order

        Args:
            order_id: Order ID
            symbol: Trading pair

        Returns:
            Success status
        """
        try:
            self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open orders

        Args:
            symbol: Trading pair (optional)

        Returns:
            List of open orders
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            self.logger.error(f"Error fetching open orders: {e}")
            return []

    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """
        Get order status

        Args:
            order_id: Order ID
            symbol: Trading pair

        Returns:
            Order information or None
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            self.logger.error(f"Error fetching order status: {e}")
            return None

    def calculate_position_size(self, symbol: str, capital: float,
                               risk_percent: float) -> Tuple[float, float]:
        """
        Calculate position size based on available capital and risk

        Args:
            symbol: Trading pair
            capital: Available capital
            risk_percent: Risk percentage (e.g., 2.0 for 2%)

        Returns:
            Tuple of (position_size, position_value)
        """
        try:
            ticker = self.get_ticker(symbol)
            if not ticker:
                return 0.0, 0.0

            current_price = ticker['last']
            position_value = capital * (risk_percent / 100.0)
            position_size = position_value / current_price

            # Round to exchange precision
            markets = self.exchange.load_markets()
            precision = markets[symbol]['precision']['amount']
            position_size = round(position_size, precision)

            return position_size, position_value
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0, 0.0
