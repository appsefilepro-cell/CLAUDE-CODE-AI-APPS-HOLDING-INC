"""
Trend Following Trading Strategy
Trades based on EMA crossovers and ADX strength
"""

import pandas as pd
import logging
from typing import Optional, Dict


class TrendFollowingStrategy:
    """Trend Following strategy using EMA crossovers and ADX"""

    def __init__(self, config: Dict):
        """
        Initialize strategy

        Args:
            config: Strategy configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Strategy parameters
        self.adx_threshold = config['indicators']['adx']['threshold']
        self.ema_crossover = config['strategies']['trend_following']['ema_crossover']

    def generate_signal(self, df: pd.DataFrame) -> Optional[str]:
        """
        Generate trading signal

        Args:
            df: DataFrame with price data and indicators

        Returns:
            'buy', 'sell', or None
        """
        if len(df) < 2:
            return None

        try:
            # Get current and previous values
            current = df.iloc[-1]
            previous = df.iloc[-2]

            adx = current['adx']
            ema_short = current['ema_short']
            ema_medium = current['ema_medium']
            ema_long = current['ema_long']

            prev_ema_short = previous['ema_short']
            prev_ema_medium = previous['ema_medium']

            macd = current['macd']
            macd_signal = current['macd_signal']

            # Check if trend is strong enough (ADX)
            if adx < self.adx_threshold:
                return None

            # Bullish signals: Short EMA crosses above Medium EMA, MACD positive
            if (prev_ema_short <= prev_ema_medium and
                ema_short > ema_medium and
                ema_medium > ema_long and
                macd > macd_signal):
                self.logger.info(f"Trend Following BUY signal: ADX={adx:.2f}, EMA crossover detected")
                return 'buy'

            # Bearish signals: Short EMA crosses below Medium EMA, MACD negative
            if (prev_ema_short >= prev_ema_medium and
                ema_short < ema_medium and
                ema_medium < ema_long and
                macd < macd_signal):
                self.logger.info(f"Trend Following SELL signal: ADX={adx:.2f}, EMA crossover detected")
                return 'sell'

            return None

        except Exception as e:
            self.logger.error(f"Error generating trend following signal: {e}")
            return None

    def get_strategy_info(self) -> Dict:
        """Get strategy information"""
        return {
            'name': 'Trend Following',
            'type': 'trend-based',
            'parameters': {
                'adx_threshold': self.adx_threshold,
                'ema_crossover': self.ema_crossover
            }
        }
