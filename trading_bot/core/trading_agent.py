"""
AgentX Trading Bot - Main Agent Loop
24-hour automated trading with multi-strategy support
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Optional
import yaml
from dotenv import load_dotenv

from core.exchange_client import KrakenClient
from core.risk_manager import RiskManager
from indicators.technical_indicators import TechnicalIndicators
from strategies.mean_reversion import MeanReversionStrategy
from strategies.trend_following import TrendFollowingStrategy


class TradingAgent:
    """Main trading agent with autonomous decision-making"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize trading agent

        Args:
            config_path: Path to configuration file
        """
        # Load environment variables
        load_dotenv()

        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.logger.info("=" * 80)
        self.logger.info("AgentX Trading Bot - APPS Holdings WY, Inc.")
        self.logger.info("=" * 80)

        # Initialize components
        self.trading_mode = os.getenv('TRADING_MODE', 'paper')
        self.initial_capital = float(os.getenv('INITIAL_CAPITAL', 10000))
        self.current_capital = self.initial_capital

        self.logger.info(f"Trading Mode: {self.trading_mode.upper()}")
        self.logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")

        # Initialize exchange client
        api_key = os.getenv('KRAKEN_API_KEY', '')
        api_secret = os.getenv('KRAKEN_API_SECRET', '')
        testnet = (self.trading_mode == 'paper')

        self.exchange = KrakenClient(api_key, api_secret, testnet)

        # Initialize risk manager
        self.risk_manager = RiskManager(self.config)

        # Initialize indicators
        self.indicators = TechnicalIndicators()

        # Initialize strategies
        strategy_name = os.getenv('STRATEGY', 'mean_reversion')
        self.active_strategy = self.load_strategy(strategy_name)

        # Agent configuration
        self.loop_interval = int(os.getenv('LOOP_INTERVAL_SECONDS', 300))
        self.running = False

        self.logger.info(f"Active Strategy: {self.active_strategy.get_strategy_info()['name']}")
        self.logger.info(f"Loop Interval: {self.loop_interval} seconds")
        self.logger.info("Initialization complete")

    def setup_logging(self):
        """Setup logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[
                logging.FileHandler('logs/trading_agent.log'),
                logging.StreamHandler()
            ]
        )

    def load_strategy(self, strategy_name: str):
        """
        Load trading strategy

        Args:
            strategy_name: Strategy name

        Returns:
            Strategy instance
        """
        if strategy_name == 'mean_reversion':
            return MeanReversionStrategy(self.config)
        elif strategy_name == 'trend_following':
            return TrendFollowingStrategy(self.config)
        else:
            self.logger.warning(f"Unknown strategy: {strategy_name}, defaulting to mean_reversion")
            return MeanReversionStrategy(self.config)

    def analyze_market(self, symbol: str) -> Optional[str]:
        """
        Analyze market and generate signal

        Args:
            symbol: Trading pair

        Returns:
            Trading signal or None
        """
        try:
            # Fetch OHLCV data
            timeframe = self.config['trading']['timeframes']['primary']
            df = self.exchange.get_ohlcv(symbol, timeframe, limit=100)

            if df.empty:
                self.logger.warning(f"No data available for {symbol}")
                return None

            # Add indicators
            df = self.indicators.add_all_indicators(df, self.config)

            # Generate signal from strategy
            signal = self.active_strategy.generate_signal(df)

            return signal

        except Exception as e:
            self.logger.error(f"Error analyzing market for {symbol}: {e}")
            return None

    def execute_trade(self, symbol: str, signal: str):
        """
        Execute trade based on signal

        Args:
            symbol: Trading pair
            signal: 'buy' or 'sell'
        """
        try:
            # Check if we can open a position
            can_open, reason = self.risk_manager.can_open_position(self.current_capital)
            if not can_open:
                self.logger.info(f"Cannot open position: {reason}")
                return

            # Get current price
            ticker = self.exchange.get_ticker(symbol)
            if not ticker:
                return

            current_price = ticker['last']

            # Calculate position size
            position_size, position_value = self.risk_manager.calculate_position_size(
                self.current_capital, current_price
            )

            if position_size == 0:
                self.logger.warning("Position size is zero, skipping trade")
                return

            # Calculate stop-loss and take-profit
            stop_loss = self.risk_manager.calculate_stop_loss(current_price, signal)
            take_profit = self.risk_manager.calculate_take_profit(current_price, signal)

            # Execute order
            if self.trading_mode == 'live':
                order = self.exchange.place_market_order(symbol, signal, position_size)
                if not order:
                    self.logger.error("Failed to place order")
                    return
            else:
                self.logger.info(f"[PAPER TRADE] {signal.upper()} {position_size:.6f} {symbol} @ ${current_price:.2f}")

            # Track position
            position = {
                'symbol': symbol,
                'side': signal,
                'entry_price': current_price,
                'size': position_size,
                'value': position_value,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_time': datetime.now(),
                'highest_price': current_price if signal == 'buy' else None,
                'lowest_price': current_price if signal == 'sell' else None
            }

            self.risk_manager.add_position(position)

            self.logger.info(f"Position opened: {symbol} {signal} @ ${current_price:.2f}")
            self.logger.info(f"Stop Loss: ${stop_loss:.2f}, Take Profit: ${take_profit:.2f}")

        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")

    def manage_positions(self):
        """Manage open positions (check stop-loss, take-profit, trailing stops)"""
        for position in self.risk_manager.open_positions[:]:  # Copy list to avoid modification issues
            try:
                symbol = position['symbol']
                ticker = self.exchange.get_ticker(symbol)
                if not ticker:
                    continue

                current_price = ticker['last']
                entry_price = position['entry_price']
                side = position['side']
                size = position['size']

                should_close = False
                close_reason = ""

                # Check stop-loss
                if side == 'buy' and current_price <= position['stop_loss']:
                    should_close = True
                    close_reason = "Stop-Loss"
                elif side == 'sell' and current_price >= position['stop_loss']:
                    should_close = True
                    close_reason = "Stop-Loss"

                # Check take-profit
                if side == 'buy' and current_price >= position['take_profit']:
                    should_close = True
                    close_reason = "Take-Profit"
                elif side == 'sell' and current_price <= position['take_profit']:
                    should_close = True
                    close_reason = "Take-Profit"

                # Check trailing stop
                if self.risk_manager.check_trailing_stop(position, current_price):
                    should_close = True
                    close_reason = "Trailing-Stop"

                if should_close:
                    # Calculate PnL
                    if side == 'buy':
                        pnl = (current_price - entry_price) * size
                    else:
                        pnl = (entry_price - current_price) * size

                    # Close position
                    if self.trading_mode == 'live':
                        close_side = 'sell' if side == 'buy' else 'buy'
                        self.exchange.place_market_order(symbol, close_side, size)
                    else:
                        self.logger.info(f"[PAPER TRADE] CLOSE {side.upper()} {size:.6f} {symbol} @ ${current_price:.2f}")

                    self.current_capital += pnl
                    self.risk_manager.remove_position(symbol, pnl)

                    self.logger.info(f"Position closed ({close_reason}): {symbol} PnL: ${pnl:.2f}")
                    self.logger.info(f"Current Capital: ${self.current_capital:,.2f}")

            except Exception as e:
                self.logger.error(f"Error managing position: {e}")

    def run_cycle(self):
        """Run one trading cycle"""
        self.logger.info("-" * 80)
        self.logger.info(f"Cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Manage existing positions
        self.manage_positions()

        # Analyze each trading pair
        for symbol in self.config['trading']['pairs']:
            try:
                # Check if we already have a position in this symbol
                if self.risk_manager.get_position(symbol):
                    self.logger.info(f"Already have position in {symbol}, skipping")
                    continue

                # Analyze market
                signal = self.analyze_market(symbol)

                if signal:
                    self.execute_trade(symbol, signal)

            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")

        # Log status
        risk_status = self.risk_manager.get_risk_status()
        self.logger.info(f"Capital: ${self.current_capital:,.2f} | "
                        f"Open Positions: {risk_status['open_positions']} | "
                        f"Daily PnL: ${risk_status['daily_pnl']:.2f}")

    def run(self):
        """Main agent loop"""
        self.running = True
        self.logger.info("Agent started - entering main loop")

        try:
            while self.running:
                self.run_cycle()
                self.logger.info(f"Sleeping for {self.loop_interval} seconds...")
                time.sleep(self.loop_interval)

        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, shutting down...")
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown agent gracefully"""
        self.logger.info("Shutting down agent...")
        self.running = False

        # Close all positions
        for position in self.risk_manager.open_positions[:]:
            try:
                symbol = position['symbol']
                side = position['side']
                size = position['size']

                close_side = 'sell' if side == 'buy' else 'buy'

                if self.trading_mode == 'live':
                    self.exchange.place_market_order(symbol, close_side, size)
                else:
                    self.logger.info(f"[PAPER TRADE] CLOSE {side.upper()} {size:.6f} {symbol}")

                self.risk_manager.remove_position(symbol, 0.0)

            except Exception as e:
                self.logger.error(f"Error closing position during shutdown: {e}")

        # Final report
        total_pnl = self.current_capital - self.initial_capital
        roi = (total_pnl / self.initial_capital) * 100

        self.logger.info("=" * 80)
        self.logger.info("FINAL REPORT")
        self.logger.info("=" * 80)
        self.logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        self.logger.info(f"Final Capital: ${self.current_capital:,.2f}")
        self.logger.info(f"Total PnL: ${total_pnl:,.2f}")
        self.logger.info(f"ROI: {roi:.2f}%")
        self.logger.info("=" * 80)
