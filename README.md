# BTC Trading Strategy Bot

[![Tests](https://github.com/91Pixels/trader-bot/actions/workflows/pr-validation.yml/badge.svg)](https://github.com/91Pixels/trader-bot/actions/workflows/pr-validation.yml)
[![Coverage](https://img.shields.io/badge/coverage-57%25-yellow)](https://github.com/91Pixels/trader-bot)
[![Tests Passing](https://img.shields.io/badge/tests-118%20passing-brightgreen)](https://github.com/91Pixels/trader-bot)

A Python-based BTC/USD trading strategy simulator with GUI interface using Coinbase price data.

## ✅ CI/CD Pipeline

Este proyecto incluye **validación automática de tests** antes de cada merge a `main`. Ver documentación completa en [`docs/CI_CD_README.md`](docs/CI_CD_README.md).

## Features

- 📊 **Real-time BTC price monitoring** (updates every 100ms)
- 🎯 **Configurable profit targets** (default: 1.5% net profit)
- 🤖 **Auto Buy**: Automatic purchase when price drops to configured level
- 🔄 **Auto Mode**: Automatic sell at target/stop loss
- 💰 **Accurate fee calculations** (0.6% buy + 0.6% sell)
- 🧪 **Dry Run mode** for safe testing
- 📈 **Live profit/loss tracking**
- 🎨 **Clean GUI with detailed metrics**

## Correct Target Price Formula

```
BTC qty = position_usd × (1 - buy_fee_rate) / entry_price
Desired Net = position_usd × (1 + profit_rate)
Required Gross = Desired Net / (1 - sell_fee_rate)
Target Price = Required Gross / BTC qty

Example: $100 position → $1.50 net profit guaranteed
```

## Setup

### Quick Start (Simulation Mode)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the bot:
   ```bash
   python btc_trader.py
   ```

### Setup for Real Trading with Coinbase

1. **Interactive Configuration Wizard:**
   ```bash
   python setup_trading.py
   ```
   This wizard will guide you through:
   - Adding Coinbase API credentials
   - Setting safety limits
   - Configuring trading parameters
   - Choosing between SIMULATION and LIVE mode

2. **Manual Configuration:**
   ```bash
   # Copy template
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   
   # Edit .env with your settings
   ```

3. **Test Configuration:**
   ```bash
   python test_config.py
   ```

4. **Get Coinbase API Keys:**
   - Go to https://www.coinbase.com/settings/api
   - Create API key with permissions:
     - `wallet:accounts:read`
     - `wallet:buys:create`
     - `wallet:sells:create`
   - Add keys to `.env` file

📖 **See [COINBASE_SETUP.md](COINBASE_SETUP.md) for detailed setup instructions**

## Usage

### Basic Configuration
1. **Start Monitoring**: Begin live price updates
2. **Position Size**: Set investment amount (default: $100)
3. **Profit Target**: Set net profit percentage (default: 1.5%)
4. **Stop Loss**: Set maximum loss percentage (default: 1.0%)

### Auto Buy Configuration
1. Enable **Auto Buy** checkbox
2. Set trigger price (or use "Set Current -1%" button)
3. Bot will automatically buy when price drops to trigger level

### Trading Modes
- **Manual Mode**: You control all trades
- **Auto Mode**: Automatic sell at target/stop loss
- **Dry Run**: Safe testing mode (recommended)

### Example Workflow
```
1. Start Monitoring
2. Enable Auto Buy at $35,000
3. Enable Auto Mode
4. Bot buys when price drops to $35,000
5. Bot sells automatically at $35,945 (2.7% increase)
6. Cycle repeats with $1.50 net profit per trade
```

## Project Structure

```
Cripto-Agent/
├── btc_trader.py        # Main trading bot
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Strategy Details

- **Entry**: Configurable or automatic via Auto Buy
- **Target**: Calculated to guarantee exact net profit after fees
- **Fees**: 0.6% per side (1.2% total round-trip)
- **Net Profit**: Exactly as configured (e.g., $1.50 on $100)
- **API**: Coinbase public API (no authentication required)

## Testing

### Run All Tests
```bash
# Windows (Auto-opens HTML report)
run_tests.bat

# Linux/Mac or manual
python tests/run_all_tests.py

# With pytest
pytest tests/ -v
```

**Reports Generated:**
- 📊 **HTML Test Report:** `test-reports/test_report_latest.html`
- 📈 **Coverage Report:** `htmlcov/index.html`
- 📄 **JUnit XML:** `test-reports/junit_TIMESTAMP.xml`

See `HTML_REPORTS_GUIDE.md` for detailed information on test reports.

### Test Coverage
- **42+ unit tests** covering all critical functionality
- **Calculation tests**: Verify formula accuracy (10 tests)
- **API tests**: Validate Coinbase integration (12 tests)
- **Logic tests**: Auto buy/sell behavior (20+ tests)

### CI/CD Pipeline
Automated testing with Jenkins:
- ✅ Code quality checks (pylint, flake8)
- ✅ Unit test execution
- ✅ Coverage reports (85%+ required)
- ✅ Security scanning (safety, bandit)

See `Jenkinsfile` for complete pipeline configuration.

## Development

### Before Committing
```bash
# Run tests
python tests/run_all_tests.py

# Check code quality
pylint btc_trader.py
flake8 btc_trader.py --max-line-length=120

# Format code
black btc_trader.py
```

### Project Quality Standards
- All tests must pass before deployment
- Minimum 85% code coverage
- No critical security vulnerabilities
- PEP 8 compliance
