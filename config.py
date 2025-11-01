"""
Configuration management for BTC Trading Bot
Loads settings from .env file and validates them
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for trading bot"""
    
    # API Credentials
    COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
    
    # Load API Secret from file if specified, otherwise from env
    PRIVATE_KEY_FILE = os.getenv('COINBASE_PRIVATE_KEY_FILE', '')
    if PRIVATE_KEY_FILE:
        try:
            key_path = Path(__file__).parent / PRIVATE_KEY_FILE
            with open(key_path, 'r') as f:
                COINBASE_API_SECRET = f.read().strip()
        except Exception as e:
            print(f"⚠️  Warning: Could not read private key file: {e}")
            COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
    else:
        COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
    
    # Trading Mode
    TRADING_MODE = os.getenv('TRADING_MODE', 'SIMULATION')
    
    # Safety Limits
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '100'))
    MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '10'))
    DAILY_LOSS_LIMIT = float(os.getenv('DAILY_LOSS_LIMIT', '50'))
    
    # Trading Pair
    TRADING_PAIR = os.getenv('TRADING_PAIR', 'BTC-USD')
    
    # Strategy Parameters
    PROFIT_TARGET = float(os.getenv('PROFIT_TARGET', '1.5'))
    STOP_LOSS = float(os.getenv('STOP_LOSS', '1.0'))
    
    # Auto Trading
    AUTO_BUY_ENABLED = os.getenv('AUTO_BUY_ENABLED', 'false').lower() == 'true'
    AUTO_SELL_ENABLED = os.getenv('AUTO_SELL_ENABLED', 'true').lower() == 'true'
    
    # Notifications
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        # Check API credentials for live trading
        if cls.TRADING_MODE == 'LIVE':
            if not cls.COINBASE_API_KEY:
                errors.append("COINBASE_API_KEY is required for live trading")
            if not cls.COINBASE_API_SECRET:
                errors.append("COINBASE_API_SECRET is required for live trading")
        
        # Validate numeric values
        if cls.MAX_POSITION_SIZE <= 0:
            errors.append("MAX_POSITION_SIZE must be positive")
        if cls.MAX_DAILY_TRADES <= 0:
            errors.append("MAX_DAILY_TRADES must be positive")
        if cls.DAILY_LOSS_LIMIT < 0:
            errors.append("DAILY_LOSS_LIMIT cannot be negative")
        if cls.PROFIT_TARGET <= 0:
            errors.append("PROFIT_TARGET must be positive")
        if cls.STOP_LOSS <= 0:
            errors.append("STOP_LOSS must be positive")
        
        # Validate trading mode
        if cls.TRADING_MODE not in ['SIMULATION', 'LIVE']:
            errors.append("TRADING_MODE must be 'SIMULATION' or 'LIVE'")
        
        return errors
    
    @classmethod
    def is_live_mode(cls):
        """Check if running in live trading mode"""
        # Read from environment to support dynamic changes in tests
        current_mode = os.getenv('TRADING_MODE', cls.TRADING_MODE)
        return current_mode == 'LIVE'
    
    @classmethod
    def is_simulation_mode(cls):
        """Check if running in simulation mode"""
        # Read from environment to support dynamic changes in tests
        current_mode = os.getenv('TRADING_MODE', cls.TRADING_MODE)
        return current_mode == 'SIMULATION'
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without secrets)"""
        print("="*70)
        print("CONFIGURATION")
        print("="*70)
        print(f"Trading Mode: {cls.TRADING_MODE}")
        print(f"Trading Pair: {cls.TRADING_PAIR}")
        print(f"Max Position Size: ${cls.MAX_POSITION_SIZE}")
        print(f"Max Daily Trades: {cls.MAX_DAILY_TRADES}")
        print(f"Daily Loss Limit: ${cls.DAILY_LOSS_LIMIT}")
        print(f"Profit Target: {cls.PROFIT_TARGET}%")
        print(f"Stop Loss: {cls.STOP_LOSS}%")
        print(f"Auto Buy: {cls.AUTO_BUY_ENABLED}")
        print(f"Auto Sell: {cls.AUTO_SELL_ENABLED}")
        print(f"API Key Configured: {'Yes' if cls.COINBASE_API_KEY else 'No'}")
        print("="*70)


# Validate configuration on load
config_errors = Config.validate()
if config_errors:
    print("\n⚠️  Configuration Errors:")
    for error in config_errors:
        print(f"   - {error}")
    if Config.TRADING_MODE == 'LIVE':
        print("\n❌ Cannot start in LIVE mode with configuration errors")
        print("   Please fix .env file and restart")
