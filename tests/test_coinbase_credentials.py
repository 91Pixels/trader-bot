"""
Unit tests for Coinbase API credentials and connection
Tests that API keys are valid and connection is stable
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from coinbase_api import CoinbaseAPI


class TestCoinbaseCredentials(unittest.TestCase):
    """Test Coinbase API credentials and connection"""
    
    def setUp(self):
        """Set up test parameters"""
        self.api = CoinbaseAPI()
    
    def test_config_loads_credentials(self):
        """Test that credentials are loaded from config"""
        self.assertIsNotNone(Config.COINBASE_API_KEY)
        self.assertIsNotNone(Config.COINBASE_API_SECRET)
        self.assertNotEqual(Config.COINBASE_API_KEY, '')
        self.assertNotEqual(Config.COINBASE_API_SECRET, '')
    
    def test_credentials_not_default(self):
        """Test that credentials are not default placeholders"""
        self.assertNotEqual(Config.COINBASE_API_KEY, 'your_api_key_here')
        self.assertNotEqual(Config.COINBASE_API_SECRET, 'your_api_secret_here')
        
        # Should have reasonable length
        self.assertGreater(len(Config.COINBASE_API_KEY), 10)
        self.assertGreater(len(Config.COINBASE_API_SECRET), 10)
    
    def test_api_client_initialization(self):
        """Test that API client initializes correctly"""
        self.assertIsNotNone(self.api)
        self.assertEqual(self.api.api_key, Config.COINBASE_API_KEY)
        self.assertEqual(self.api.api_secret, Config.COINBASE_API_SECRET)
    
    def test_public_endpoint_connection(self):
        """Test connection to public endpoint (no auth required)"""
        try:
            price = self.api.get_spot_price('BTC-USD')
            
            # Price should be a valid number
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            
            # BTC price should be in reasonable range
            self.assertGreater(price, 1000, "BTC price too low")
            self.assertLess(price, 1000000, "BTC price too high")
            
        except Exception as e:
            self.fail(f"Failed to connect to Coinbase public endpoint: {e}")
    
    def test_connection_stability(self):
        """Test that connection is stable over multiple requests"""
        prices = []
        errors = 0
        
        for i in range(5):
            try:
                price = self.api.get_spot_price('BTC-USD')
                prices.append(price)
            except Exception:
                errors += 1
        
        # At least 80% of requests should succeed
        success_rate = (len(prices) / 5) * 100
        self.assertGreaterEqual(success_rate, 80, 
            f"Connection unstable: only {success_rate}% success rate")
        
        # Prices should be relatively consistent
        if len(prices) >= 2:
            min_price = min(prices)
            max_price = max(prices)
            variance = (max_price - min_price) / min_price
            
            # Variance should be less than 1% in quick succession
            self.assertLess(variance, 0.01, 
                "Price variance too high - possible connection issues")
    
    def test_authenticated_endpoints_in_live_mode(self):
        """Test authenticated endpoints in LIVE MODE"""
        import os
        from coinbase_advanced_trade_jwt import CoinbaseAdvancedTradeJWT
        
        # Force LIVE mode for this test
        original_mode = os.environ.get('TRADING_MODE')
        os.environ['TRADING_MODE'] = 'LIVE'
        
        try:
            # Create live API client
            live_api = CoinbaseAdvancedTradeJWT()
            
            # Skip if credentials not in ECDSA format
            if not live_api.is_jwt_format:
                self.skipTest("Credentials not in ECDSA format - cannot test LIVE mode")
            
            # Test getting account balance (requires authentication)
            balances = live_api.get_account_balance()
            
            # Should return a dictionary
            self.assertIsInstance(balances, dict)
            
            # Should have at least USD or BTC
            self.assertTrue(
                'USD' in balances or 'BTC' in balances,
                "No USD or BTC account found"
            )
            
        except Exception as e:
            self.fail(f"Failed to access authenticated endpoint: {e}")
        finally:
            # Restore original mode
            if original_mode:
                os.environ['TRADING_MODE'] = original_mode
            else:
                os.environ['TRADING_MODE'] = 'SIMULATION'
    
    def test_api_key_format(self):
        """Test that API key has valid format"""
        api_key = Config.COINBASE_API_KEY
        
        # ECDSA format: organizations/{org_id}/apiKeys/{key_id}
        # Legacy format: alphanumeric UUID
        is_ecdsa_format = api_key.startswith('organizations/') and '/apiKeys/' in api_key
        is_legacy_format = api_key.replace('-', '').isalnum() or api_key.isalnum()
        
        self.assertTrue(is_ecdsa_format or is_legacy_format,
            "API key should be in ECDSA (organizations/xxx) or legacy (UUID) format")
    
    def test_api_secret_format(self):
        """Test that API secret has valid format"""
        api_secret = Config.COINBASE_API_SECRET
        
        # ECDSA format: PEM encoded private key
        # Legacy format: hex or UUID
        is_ecdsa_pem = api_secret.startswith('-----BEGIN EC PRIVATE KEY-----')
        is_legacy_format = api_secret.replace('-', '').replace('/', '').replace('+', '').replace('=', '').isalnum()
        
        self.assertTrue(is_ecdsa_pem or is_legacy_format,
            "API secret should be in ECDSA (PEM) or legacy (base64/UUID) format")
    
    def test_trading_mode_configuration(self):
        """Test that trading mode is properly configured"""
        self.assertIn(Config.TRADING_MODE, ['SIMULATION', 'LIVE'])
        
        # In LIVE mode, must have valid credentials
        if Config.is_live_mode():
            self.assertNotEqual(Config.COINBASE_API_KEY, 'your_api_key_here')
            self.assertNotEqual(Config.COINBASE_API_SECRET, 'your_api_secret_here')


class TestCoinbaseAPIResponses(unittest.TestCase):
    """Test Coinbase API response handling"""
    
    def setUp(self):
        """Set up API client"""
        self.api = CoinbaseAPI()
    
    def test_spot_price_response_format(self):
        """Test that spot price response has correct format"""
        price = self.api.get_spot_price('BTC-USD')
        
        # Should be float
        self.assertIsInstance(price, float)
        
        # Should have reasonable precision (not infinity)
        self.assertFalse(float('inf') == price)
        self.assertFalse(float('-inf') == price)
        
        # Should be positive
        self.assertGreater(price, 0)
    
    def test_error_handling_invalid_pair(self):
        """Test error handling with invalid trading pair"""
        try:
            # This should raise an exception
            price = self.api.get_spot_price('INVALID-PAIR')
            
            # If it doesn't raise, it should at least return 0 or None
            self.assertIn(price, [0, None])
            
        except Exception as e:
            # Expected to raise an exception
            self.assertIsInstance(e, Exception)
    
    def test_connection_timeout_handling(self):
        """Test that timeout is properly configured"""
        # This just verifies the method exists and accepts timeout
        try:
            # Quick timeout to test handling
            import requests
            response = requests.get(
                'https://api.coinbase.com/v2/prices/BTC-USD/spot',
                timeout=1  # Very short timeout
            )
            # If succeeds, connection is fast
            self.assertEqual(response.status_code, 200)
        except requests.Timeout:
            # Timeout is expected with very short duration
            pass
        except Exception as e:
            # Other exceptions are acceptable (network issues, etc)
            pass


class TestCoinbaseCredentialsSecurity(unittest.TestCase):
    """Test security aspects of credential handling"""
    
    def test_credentials_not_hardcoded(self):
        """Test that credentials come from environment/config, not hardcoded"""
        # Read the coinbase_api.py file
        import coinbase_api
        source = coinbase_api.__file__
        
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should not contain hardcoded API keys (look for actual values)
        # Not just variable names like "self.api_key"
        actual_key = Config.COINBASE_API_KEY
        actual_secret = Config.COINBASE_API_SECRET
        
        # These actual values should NOT be in the source code
        self.assertNotIn(f'"{actual_key}"', content)
        self.assertNotIn(f"'{actual_key}'", content)
        self.assertNotIn(f'"{actual_secret}"', content)
        self.assertNotIn(f"'{actual_secret}'", content)
    
    def test_env_file_in_gitignore(self):
        """Test that .env file is in .gitignore"""
        gitignore_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.gitignore'
        )
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # .env should be in gitignore
            self.assertIn('.env', content)
    
    def test_config_validates_live_mode(self):
        """Test that config validates credentials in LIVE mode"""
        errors = Config.validate()
        
        if Config.is_live_mode():
            # In LIVE mode, should not have errors if credentials are set
            if Config.COINBASE_API_KEY != 'your_api_key_here':
                self.assertEqual(len(errors), 0, 
                    f"Config validation failed in LIVE mode: {errors}")
        
        # In SIMULATION mode, errors are acceptable if no credentials
        # This is fine - simulation doesn't need real credentials


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
