"""
Technical Indicators for Trading Bot
Implements RSI, MACD, Bollinger Bands, EMA, ADX, and Candlestick Patterns
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
import logging


class TechnicalIndicators:
    """Calculate technical indicators for trading decisions"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)

        Args:
            df: DataFrame with 'close' column
            period: RSI period

        Returns:
            RSI series
        """
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26,
                       signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Args:
            df: DataFrame with 'close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Tuple of (macd, signal, histogram)
        """
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return macd, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20,
                                  std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands

        Args:
            df: DataFrame with 'close' column
            period: MA period
            std_dev: Standard deviation multiplier

        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle_band = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band, middle_band, lower_band

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)

        Args:
            df: DataFrame with 'close' column
            period: EMA period

        Returns:
            EMA series
        """
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index (ADX)

        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ADX period

        Returns:
            ADX series
        """
        high = df['high']
        low = df['low']
        close = df['close']

        # Calculate +DM and -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # Calculate True Range (TR)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Calculate smoothed averages
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Detect candlestick patterns

        Args:
            df: DataFrame with OHLC data

        Returns:
            Dictionary of pattern signals
        """
        if len(df) < 3:
            return {}

        patterns = {}

        # Get last 3 candles
        last = df.iloc[-1]
        prev = df.iloc[-2]
        prev2 = df.iloc[-3]

        # Bullish patterns
        # Hammer
        body = abs(last['close'] - last['open'])
        lower_shadow = min(last['open'], last['close']) - last['low']
        upper_shadow = last['high'] - max(last['open'], last['close'])

        patterns['hammer'] = (
            lower_shadow > 2 * body and
            upper_shadow < body and
            last['close'] > last['open']
        )

        # Bullish Engulfing
        patterns['bullish_engulfing'] = (
            prev['close'] < prev['open'] and
            last['close'] > last['open'] and
            last['close'] > prev['open'] and
            last['open'] < prev['close']
        )

        # Morning Star
        patterns['morning_star'] = (
            prev2['close'] < prev2['open'] and
            abs(prev['close'] - prev['open']) < body * 0.3 and
            last['close'] > last['open'] and
            last['close'] > (prev2['open'] + prev2['close']) / 2
        )

        # Bearish patterns
        # Shooting Star
        patterns['shooting_star'] = (
            upper_shadow > 2 * body and
            lower_shadow < body and
            last['close'] < last['open']
        )

        # Bearish Engulfing
        patterns['bearish_engulfing'] = (
            prev['close'] > prev['open'] and
            last['close'] < last['open'] and
            last['close'] < prev['open'] and
            last['open'] > prev['close']
        )

        # Evening Star
        patterns['evening_star'] = (
            prev2['close'] > prev2['open'] and
            abs(prev['close'] - prev['open']) < body * 0.3 and
            last['close'] < last['open'] and
            last['close'] < (prev2['open'] + prev2['close']) / 2
        )

        return patterns

    def add_all_indicators(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Add all technical indicators to DataFrame

        Args:
            df: OHLCV DataFrame
            config: Configuration dictionary

        Returns:
            DataFrame with all indicators added
        """
        try:
            # RSI
            df['rsi'] = self.calculate_rsi(df, config['indicators']['rsi']['period'])

            # MACD
            macd, signal, histogram = self.calculate_macd(
                df,
                config['indicators']['macd']['fast_period'],
                config['indicators']['macd']['slow_period'],
                config['indicators']['macd']['signal_period']
            )
            df['macd'] = macd
            df['macd_signal'] = signal
            df['macd_histogram'] = histogram

            # Bollinger Bands
            upper, middle, lower = self.calculate_bollinger_bands(
                df,
                config['indicators']['bollinger_bands']['period'],
                config['indicators']['bollinger_bands']['std_dev']
            )
            df['bb_upper'] = upper
            df['bb_middle'] = middle
            df['bb_lower'] = lower

            # EMAs
            df['ema_short'] = self.calculate_ema(df, config['indicators']['ema']['short_period'])
            df['ema_medium'] = self.calculate_ema(df, config['indicators']['ema']['medium_period'])
            df['ema_long'] = self.calculate_ema(df, config['indicators']['ema']['long_period'])

            # ADX
            df['adx'] = self.calculate_adx(df, config['indicators']['adx']['period'])

            return df

        except Exception as e:
            self.logger.error(f"Error adding indicators: {e}")
            return df
