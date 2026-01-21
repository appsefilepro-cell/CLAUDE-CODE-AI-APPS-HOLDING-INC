#!/usr/bin/env python3
"""
AgentX Trading Bot - Main Entry Point
APPS Holdings WY, Inc.

Usage:
    python main.py              # Run in paper trading mode
    python main.py --backtest   # Run backtesting
    python main.py --live       # Run in live trading mode (requires confirmation)
"""

import sys
import os
import argparse
from core.trading_agent import TradingAgent


def confirm_live_trading():
    """Confirm user wants to trade with real money"""
    print("=" * 80)
    print("WARNING: You are about to start LIVE trading with REAL money!")
    print("=" * 80)
    response = input("Are you absolutely sure? Type 'YES' to continue: ")
    return response == 'YES'


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AgentX Trading Bot')
    parser.add_argument('--live', action='store_true', help='Run in live trading mode')
    parser.add_argument('--backtest', action='store_true', help='Run backtesting')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                       help='Path to configuration file')

    args = parser.parse_args()

    # Change to trading_bot directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Set trading mode
    if args.live:
        if not confirm_live_trading():
            print("Live trading cancelled.")
            sys.exit(0)
        os.environ['TRADING_MODE'] = 'live'
    elif args.backtest:
        print("Backtesting mode not yet implemented")
        sys.exit(1)
    else:
        os.environ['TRADING_MODE'] = 'paper'
        print("Starting in PAPER TRADING mode (no real money)")

    # Initialize and run agent
    try:
        agent = TradingAgent(config_path=args.config)
        agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
