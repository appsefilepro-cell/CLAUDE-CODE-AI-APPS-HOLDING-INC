"""
Unit tests for trading strategies
"""

import unittest
import pandas as pd
import numpy as np
import yaml
from strategies.mean_reversion import MeanReversionStrategy
from strategies.trend_following import TrendFollowingStrategy


class TestStrategies(unittest.TestCase):
    """Test trading strategies"""

    def setUp(self):
        """Setup test data"""
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        # Create sample data with indicators
        dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
        self.df = pd.DataFrame({
            'close': np.random.uniform(40000, 45000, 100),
            'rsi': np.random.uniform(20, 80, 100),
            'bb_upper': np.random.uniform(45000, 50000, 100),
            'bb_middle': np.random.uniform(40000, 45000, 100),
            'bb_lower': np.random.uniform(35000, 40000, 100),
            'ema_short': np.random.uniform(40000, 45000, 100),
            'ema_medium': np.random.uniform(40000, 45000, 100),
            'ema_long': np.random.uniform(40000, 45000, 100),
            'adx': np.random.uniform(15, 40, 100),
            'macd': np.random.uniform(-100, 100, 100),
            'macd_signal': np.random.uniform(-100, 100, 100)
        }, index=dates)

    def test_mean_reversion_strategy(self):
        """Test mean reversion strategy"""
        strategy = MeanReversionStrategy(self.config)
        signal = strategy.generate_signal(self.df)
        self.assertIn(signal, ['buy', 'sell', None])

    def test_trend_following_strategy(self):
        """Test trend following strategy"""
        strategy = TrendFollowingStrategy(self.config)
        signal = strategy.generate_signal(self.df)
        self.assertIn(signal, ['buy', 'sell', None])

    def test_strategy_info(self):
        """Test strategy info retrieval"""
        strategy = MeanReversionStrategy(self.config)
        info = strategy.get_strategy_info()
        self.assertIn('name', info)
        self.assertIn('type', info)
        self.assertIn('parameters', info)


if __name__ == '__main__':
    unittest.main()
