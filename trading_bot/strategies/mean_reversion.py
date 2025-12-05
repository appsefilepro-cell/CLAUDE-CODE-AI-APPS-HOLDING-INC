"""
Mean Reversion Trading Strategy
Trades based on RSI oversold/overbought and Bollinger Band reversals
"""

import pandas as pd
import logging
from typing import Optional, Dict


class MeanReversionStrategy:
    """Mean Reversion strategy using RSI and Bollinger Bands"""

    def __init__(self, config: Dict):
        """
        Initialize strategy

        Args:
            config: Strategy configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Strategy parameters
        self.rsi_entry_low = config['strategies']['mean_reversion']['rsi_entry_low']
        self.rsi_entry_high = config['strategies']['mean_reversion']['rsi_entry_high']
        self.bb_std_dev = config['strategies']['mean_reversion']['bb_std_dev']

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
            # Get latest values
            current = df.iloc[-1]
            rsi = current['rsi']
            close = current['close']
            bb_lower = current['bb_lower']
            bb_upper = current['bb_upper']

            # Buy signals: RSI oversold OR price below lower BB
            if rsi < self.rsi_entry_low or close < bb_lower:
                self.logger.info(f"Mean Reversion BUY signal: RSI={rsi:.2f}, Close={close:.2f}, BB_Lower={bb_lower:.2f}")
                return 'buy'

            # Sell signals: RSI overbought OR price above upper BB
            if rsi > self.rsi_entry_high or close > bb_upper:
                self.logger.info(f"Mean Reversion SELL signal: RSI={rsi:.2f}, Close={close:.2f}, BB_Upper={bb_upper:.2f}")
                return 'sell'

            return None

        except Exception as e:
            self.logger.error(f"Error generating mean reversion signal: {e}")
            return None

    def get_strategy_info(self) -> Dict:
        """Get strategy information"""
        return {
            'name': 'Mean Reversion',
            'type': 'counter-trend',
            'parameters': {
                'rsi_entry_low': self.rsi_entry_low,
                'rsi_entry_high': self.rsi_entry_high,
                'bb_std_dev': self.bb_std_dev
            }
        }
