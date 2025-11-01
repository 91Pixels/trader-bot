"""
Pytest configuration and fixtures
Automatically skip tests that require API credentials when not available
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "requires_credentials: mark test as requiring API credentials"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically skip tests that require credentials when they're not available
    """
    # Check if we have valid credentials
    has_credentials = (
        Config.COINBASE_API_KEY and 
        len(Config.COINBASE_API_KEY) > 10 and
        Config.COINBASE_API_SECRET and 
        len(Config.COINBASE_API_SECRET) > 10
    )
    
    skip_credentials = pytest.mark.skip(reason="API credentials not available in CI environment")
    
    for item in items:
        # Skip tests that check for credentials
        if "test_coinbase_credentials.py" in str(item.fspath) or "test_wallet_balance.py" in str(item.fspath):
            if any(name in item.name for name in [
                "test_api_key_format",
                "test_api_secret_format", 
                "test_authenticated_endpoints_in_live_mode",
                "test_config_loads_credentials",
                "test_credentials_not_default",
                "test_credentials_not_hardcoded",
                "test_credentials_authentication"
            ]):
                if not has_credentials:
                    item.add_marker(skip_credentials)
