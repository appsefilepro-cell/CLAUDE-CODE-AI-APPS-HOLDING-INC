"""
Risk Management Module
Handles position sizing, stop-loss, take-profit, and drawdown protection
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime


class RiskManager:
    """Comprehensive risk management for trading bot"""

    def __init__(self, config: Dict):
        """
        Initialize risk manager

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Risk parameters
        self.max_position_size_percent = config['trading']['risk_management']['max_position_size_percent']
        self.max_drawdown_percent = config['trading']['risk_management']['max_drawdown_percent']
        self.stop_loss_percent = config['trading']['risk_management']['stop_loss_percent']
        self.take_profit_percent = config['trading']['risk_management']['take_profit_percent']
        self.max_open_positions = config['trading']['risk_management']['max_open_positions']
        self.daily_loss_limit = config['trading']['risk_management']['daily_loss_limit']
        self.trailing_stop = config['trading']['risk_management']['trailing_stop']
        self.trailing_stop_percent = config['trading']['risk_management']['trailing_stop_percent']

        # Tracking
        self.daily_pnl = 0.0
        self.peak_capital = 0.0
        self.open_positions = []
        self.daily_reset_time = None

    def reset_daily_stats(self):
        """Reset daily statistics"""
        current_date = datetime.now().date()
        if self.daily_reset_time is None or self.daily_reset_time != current_date:
            self.daily_pnl = 0.0
            self.daily_reset_time = current_date
            self.logger.info("Daily stats reset")

    def calculate_position_size(self, capital: float, current_price: float) -> Tuple[float, float]:
        """
        Calculate position size based on risk parameters

        Args:
            capital: Available capital
            current_price: Current asset price

        Returns:
            Tuple of (position_size, position_value)
        """
        position_value = capital * (self.max_position_size_percent / 100.0)
        position_size = position_value / current_price

        self.logger.info(f"Position size calculated: {position_size:.6f} units @ ${current_price:.2f}")
        return position_size, position_value

    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        Calculate stop-loss price

        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'

        Returns:
            Stop-loss price
        """
        if side == 'buy':
            stop_loss = entry_price * (1 - self.stop_loss_percent / 100.0)
        else:
            stop_loss = entry_price * (1 + self.stop_loss_percent / 100.0)

        return stop_loss

    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """
        Calculate take-profit price

        Args:
            entry_price: Entry price
            side: 'buy' or 'sell'

        Returns:
            Take-profit price
        """
        if side == 'buy':
            take_profit = entry_price * (1 + self.take_profit_percent / 100.0)
        else:
            take_profit = entry_price * (1 - self.take_profit_percent / 100.0)

        return take_profit

    def check_trailing_stop(self, position: Dict, current_price: float) -> bool:
        """
        Check if trailing stop should be triggered

        Args:
            position: Position dictionary
            current_price: Current price

        Returns:
            True if stop should trigger
        """
        if not self.trailing_stop:
            return False

        entry_price = position['entry_price']
        side = position['side']
        highest_price = position.get('highest_price', entry_price)
        lowest_price = position.get('lowest_price', entry_price)

        if side == 'buy':
            # Update highest price
            if current_price > highest_price:
                position['highest_price'] = current_price
                highest_price = current_price

            # Calculate trailing stop
            trailing_stop_price = highest_price * (1 - self.trailing_stop_percent / 100.0)

            if current_price < trailing_stop_price:
                self.logger.info(f"Trailing stop triggered: {current_price:.2f} < {trailing_stop_price:.2f}")
                return True
        else:
            # Update lowest price
            if current_price < lowest_price:
                position['lowest_price'] = current_price
                lowest_price = current_price

            # Calculate trailing stop
            trailing_stop_price = lowest_price * (1 + self.trailing_stop_percent / 100.0)

            if current_price > trailing_stop_price:
                self.logger.info(f"Trailing stop triggered: {current_price:.2f} > {trailing_stop_price:.2f}")
                return True

        return False

    def can_open_position(self, capital: float) -> Tuple[bool, str]:
        """
        Check if new position can be opened

        Args:
            capital: Current capital

        Returns:
            Tuple of (can_open, reason)
        """
        self.reset_daily_stats()

        # Check max open positions
        if len(self.open_positions) >= self.max_open_positions:
            return False, f"Max open positions reached ({self.max_open_positions})"

        # Check daily loss limit
        if abs(self.daily_pnl) >= self.daily_loss_limit:
            return False, f"Daily loss limit reached (${abs(self.daily_pnl):.2f})"

        # Check drawdown
        if self.peak_capital == 0:
            self.peak_capital = capital

        current_drawdown = ((self.peak_capital - capital) / self.peak_capital) * 100
        if current_drawdown > self.max_drawdown_percent:
            return False, f"Max drawdown exceeded ({current_drawdown:.2f}%)"

        # Update peak capital
        if capital > self.peak_capital:
            self.peak_capital = capital

        return True, "OK"

    def add_position(self, position: Dict):
        """
        Add position to tracking

        Args:
            position: Position dictionary
        """
        self.open_positions.append(position)
        self.logger.info(f"Position added: {position['symbol']} {position['side']} @ {position['entry_price']:.2f}")

    def remove_position(self, symbol: str, pnl: float):
        """
        Remove position from tracking

        Args:
            symbol: Trading pair
            pnl: Profit/loss for position
        """
        self.open_positions = [p for p in self.open_positions if p['symbol'] != symbol]
        self.daily_pnl += pnl
        self.logger.info(f"Position closed: {symbol}, PnL: ${pnl:.2f}, Daily PnL: ${self.daily_pnl:.2f}")

    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get position by symbol

        Args:
            symbol: Trading pair

        Returns:
            Position dictionary or None
        """
        for position in self.open_positions:
            if position['symbol'] == symbol:
                return position
        return None

    def get_risk_status(self) -> Dict:
        """
        Get current risk status

        Returns:
            Risk status dictionary
        """
        self.reset_daily_stats()

        return {
            'open_positions': len(self.open_positions),
            'max_positions': self.max_open_positions,
            'daily_pnl': self.daily_pnl,
            'daily_loss_limit': self.daily_loss_limit,
            'peak_capital': self.peak_capital,
            'positions': self.open_positions
        }
