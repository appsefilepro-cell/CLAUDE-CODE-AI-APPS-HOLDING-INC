# AgentX Trading Bot

**APPS Holdings WY, Inc.**

Advanced autonomous cryptocurrency trading bot with multi-strategy support, comprehensive risk management, and 24-hour operation.

## Features

### Exchange Integration
- **Kraken API** (US accessible)
- Paper trading mode for safe testing
- Real-time market data
- Order execution and management

### Technical Indicators
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- EMA (Exponential Moving Average) crossovers
- ADX (Average Directional Index)
- Candlestick pattern detection

### Trading Strategies
1. **Mean Reversion**
   - RSI oversold/overbought signals
   - Bollinger Band reversals
   - Counter-trend trading

2. **Trend Following**
   - EMA crossover signals
   - ADX trend strength confirmation
   - MACD momentum

### Risk Management
- Position sizing (% of capital)
- Stop-loss and take-profit automation
- Trailing stops
- Maximum drawdown protection
- Daily loss limits
- Maximum concurrent positions

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your Kraken API credentials
nano .env
```

## Configuration

### Environment Variables (.env)

```bash
# Kraken API (get from https://www.kraken.com/u/security/api)
KRAKEN_API_KEY=your_api_key_here
KRAKEN_API_SECRET=your_api_secret_here

# Trading Settings
TRADING_MODE=paper          # paper or live
TRADING_PAIR=BTC/USD
INITIAL_CAPITAL=10000
POSITION_SIZE_PERCENT=2.0   # 2% of capital per trade
STOP_LOSS_PERCENT=2.0
MAX_DRAWDOWN_PERCENT=10.0

# Strategy
STRATEGY=mean_reversion     # mean_reversion or trend_following

# Agent
LOOP_INTERVAL_SECONDS=300   # 5 minutes
```

### Strategy Configuration (config/config.yaml)

Edit `config/config.yaml` to customize:
- Trading pairs
- Indicator parameters
- Risk management rules
- Strategy settings

## Usage

### Paper Trading (Recommended First)

```bash
python main.py
```

This mode simulates trading without real money. Perfect for:
- Testing strategies
- Validating configuration
- Learning the system

### Live Trading

```bash
python main.py --live
```

⚠️ **WARNING**: This uses real money. Requires confirmation prompt.

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_indicators.py

# Run with coverage
python -m pytest --cov=. tests/
```

## How It Works

### Agent Loop

1. **Market Analysis**
   - Fetch OHLCV data from Kraken
   - Calculate technical indicators
   - Generate trading signals

2. **Risk Assessment**
   - Check position limits
   - Verify drawdown constraints
   - Calculate position size

3. **Order Execution**
   - Place orders via Kraken API
   - Set stop-loss and take-profit
   - Track position

4. **Position Management**
   - Monitor stop-loss/take-profit
   - Update trailing stops
   - Close positions when triggered

5. **Repeat**
   - Sleep for configured interval
   - Continue 24-hour operation

## Directory Structure

```
trading_bot/
├── core/
│   ├── exchange_client.py    # Kraken API client
│   ├── trading_agent.py      # Main agent loop
│   └── risk_manager.py       # Risk management
├── indicators/
│   └── technical_indicators.py
├── strategies/
│   ├── mean_reversion.py
│   └── trend_following.py
├── tests/
│   ├── test_indicators.py
│   └── test_strategies.py
├── config/
│   └── config.yaml
├── logs/
│   └── trading_agent.log
├── main.py
├── requirements.txt
└── .env.example
```

## Logs

Trading activity is logged to:
- `logs/trading_agent.log` - Complete trading history
- Console output - Real-time status

## Safety Features

1. **Paper Trading Default** - No real money until explicitly enabled
2. **Confirmation Required** - Live mode requires typing 'YES'
3. **Stop-Loss Protection** - Automatic loss limiting
4. **Drawdown Limits** - Stops trading if losses exceed threshold
5. **Position Limits** - Maximum concurrent positions
6. **Daily Loss Limits** - Halts trading if daily losses exceeded

## Performance Monitoring

The agent logs:
- Current capital
- Open positions
- Daily P&L
- Trade executions
- Risk status

## Troubleshooting

### Common Issues

**API Connection Errors**
- Verify API keys in `.env`
- Check Kraken API permissions
- Ensure network connectivity

**No Trading Signals**
- Check market volatility
- Review strategy parameters
- Verify indicator calculations

**Position Not Closing**
- Check stop-loss/take-profit levels
- Review trailing stop settings
- Verify order execution

## Support

For issues or questions:
- Check logs in `logs/trading_agent.log`
- Review configuration settings
- Contact APPS Holdings WY, Inc.

## Disclaimer

**Trading cryptocurrencies involves substantial risk of loss. This software is provided "as-is" without warranty. Past performance does not guarantee future results. Only trade with capital you can afford to lose.**

## License

Copyright © 2024 APPS Holdings WY, Inc. All rights reserved.
