"""
Unit tests for technical indicators
"""

import unittest
import pandas as pd
import numpy as np
from indicators.technical_indicators import TechnicalIndicators


class TestTechnicalIndicators(unittest.TestCase):
    """Test technical indicators"""

    def setUp(self):
        """Setup test data"""
        self.indicators = TechnicalIndicators()

        # Create sample OHLCV data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
        self.df = pd.DataFrame({
            'open': np.random.uniform(40000, 45000, 100),
            'high': np.random.uniform(45000, 50000, 100),
            'low': np.random.uniform(35000, 40000, 100),
            'close': np.random.uniform(40000, 45000, 100),
            'volume': np.random.uniform(1000, 5000, 100)
        }, index=dates)

    def test_calculate_rsi(self):
        """Test RSI calculation"""
        rsi = self.indicators.calculate_rsi(self.df, period=14)
        self.assertIsInstance(rsi, pd.Series)
        self.assertTrue(all(0 <= x <= 100 for x in rsi.dropna()))

    def test_calculate_macd(self):
        """Test MACD calculation"""
        macd, signal, histogram = self.indicators.calculate_macd(self.df)
        self.assertIsInstance(macd, pd.Series)
        self.assertIsInstance(signal, pd.Series)
        self.assertIsInstance(histogram, pd.Series)
        self.assertEqual(len(macd), len(self.df))

    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        upper, middle, lower = self.indicators.calculate_bollinger_bands(self.df)
        self.assertIsInstance(upper, pd.Series)
        self.assertIsInstance(middle, pd.Series)
        self.assertIsInstance(lower, pd.Series)
        # Upper should be greater than middle, middle greater than lower
        self.assertTrue(all(upper.dropna() >= middle.dropna()))
        self.assertTrue(all(middle.dropna() >= lower.dropna()))

    def test_calculate_ema(self):
        """Test EMA calculation"""
        ema = self.indicators.calculate_ema(self.df, period=20)
        self.assertIsInstance(ema, pd.Series)
        self.assertEqual(len(ema), len(self.df))

    def test_calculate_adx(self):
        """Test ADX calculation"""
        adx = self.indicators.calculate_adx(self.df, period=14)
        self.assertIsInstance(adx, pd.Series)
        self.assertTrue(all(0 <= x <= 100 for x in adx.dropna()))


if __name__ == '__main__':
    unittest.main()
