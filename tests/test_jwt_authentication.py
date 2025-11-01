"""
Unit tests for JWT authentication with ECDSA
Tests the current working implementation
"""
import unittest
import os
from unittest.mock import patch, Mock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coinbase_advanced_trade_jwt import CoinbaseAdvancedTradeJWT


class TestJWTAuthentication(unittest.TestCase):
    """Test JWT authentication functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Force simulation mode
        self.original_mode = os.environ.get('TRADING_MODE')
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    def tearDown(self):
        """Restore environment"""
        if self.original_mode:
            os.environ['TRADING_MODE'] = self.original_mode
        elif 'TRADING_MODE' in os.environ:
            del os.environ['TRADING_MODE']
    
    def test_client_initializes(self):
        """Test that JWT client initializes"""
        client = CoinbaseAdvancedTradeJWT()
        self.assertIsNotNone(client)
        # In SIMULATION mode, is_live should be False
        if os.environ.get('TRADING_MODE') == 'SIMULATION':
            self.assertFalse(client.is_live)
    
    def test_jwt_format_detection(self):
        """Test ECDSA format detection"""
        client = CoinbaseAdvancedTradeJWT()
        # Should detect format (True if ECDSA, False if Ed25519)
        self.assertIsInstance(client.is_jwt_format, bool)
    
    @patch('requests.get')
    def test_get_spot_price(self, mock_get):
        """Test getting BTC spot price"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'amount': '100000.00'}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = CoinbaseAdvancedTradeJWT()
        price = client.get_spot_price('BTC-USD')
        
        self.assertEqual(price, 100000.00)
    
    def test_get_accounts_simulation(self):
        """Test get_accounts in simulation mode"""
        client = CoinbaseAdvancedTradeJWT()
        accounts = client.get_accounts()
        
        self.assertIsInstance(accounts, dict)
        self.assertIn('accounts', accounts)
        self.assertIsInstance(accounts['accounts'], list)
    
    def test_get_balance_simulation(self):
        """Test get_account_balance in simulation mode"""
        client = CoinbaseAdvancedTradeJWT()
        balances = client.get_account_balance()
        
        self.assertIsInstance(balances, dict)
        self.assertIn('USD', balances)
        self.assertIn('BTC', balances)
    
    def test_create_order_simulation(self):
        """Test creating order in simulation mode"""
        client = CoinbaseAdvancedTradeJWT()
        result = client.place_market_buy_order('BTC-USD', 10.0)
        
        self.assertIsNotNone(result)
        # In simulation mode, should return simulated order
        if not client.is_live:
            self.assertIn('order_id', result)
            self.assertEqual(result['status'], 'SIMULATED')


class TestOrderPlacement(unittest.TestCase):
    """Test order placement functionality"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['TRADING_MODE'] = 'SIMULATION'
        self.client = CoinbaseAdvancedTradeJWT()
    
    def test_market_buy_order(self):
        """Test placing market buy order"""
        result = self.client.place_market_buy_order('BTC-USD', 100.0)
        
        self.assertIsNotNone(result)
        # In simulation, should have order_id
        if not self.client.is_live:
            self.assertIn('order_id', result)
    
    def test_market_sell_order(self):
        """Test placing market sell order"""
        result = self.client.place_market_sell_order('BTC-USD', 0.001)
        
        self.assertIsNotNone(result)
        # In simulation, should have order_id
        if not self.client.is_live:
            self.assertIn('order_id', result)


if __name__ == '__main__':
    unittest.main()
