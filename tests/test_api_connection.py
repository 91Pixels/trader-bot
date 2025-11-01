"""
Unit tests for API connection testing functionality
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from btc_trader import BTCTrader
import tkinter as tk


class TestAPIConnectionTesting(unittest.TestCase):
    """Test cases for API connection testing"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level Tk instance"""
        cls.root = tk.Tk()
        cls.root.withdraw()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level Tk instance"""
        try:
            cls.root.destroy()
        except:
            pass
    
    @patch('btc_trader.CoinbaseCompleteAPI')
    def test_api_connection_success(self, mock_api):
        """Test successful API connection"""
        # Mock API responses
        mock_api_instance = Mock()
        mock_api_instance.is_jwt_format = True
        mock_api_instance.list_accounts.return_value = {
            'accounts': [
                {'currency': 'USD', 'available_balance': {'value': '100'}},
                {'currency': 'BTC', 'available_balance': {'value': '0.001'}}
            ]
        }
        mock_api.return_value = mock_api_instance
        
        # Create trader instance
        trader = BTCTrader()
        trader.api = mock_api_instance
        
        # Test connection
        result = trader.test_api_connection()
        
        # Assertions
        self.assertTrue(result)
        self.assertIn("ONLINE", trader.test_result_var.get())
        self.assertIn("Connected", trader.api_status_var.get())
        
    @patch('btc_trader.CoinbaseCompleteAPI')
    def test_api_connection_invalid_credentials(self, mock_api):
        """Test API connection with invalid credentials"""
        # Mock API with invalid format
        mock_api_instance = Mock()
        mock_api_instance.is_jwt_format = False
        mock_api.return_value = mock_api_instance
        
        # Create trader instance
        trader = BTCTrader()
        trader.api = mock_api_instance
        
        # Test connection
        result = trader.test_api_connection()
        
        # Assertions
        self.assertFalse(result)
        self.assertIn("OFFLINE", trader.test_result_var.get())
        self.assertIn("Invalid credentials", trader.test_result_var.get())
        
    @patch('btc_trader.CoinbaseCompleteAPI')
    def test_api_connection_failure(self, mock_api):
        """Test API connection failure (network error)"""
        # Mock API that raises exception
        mock_api_instance = Mock()
        mock_api_instance.is_jwt_format = True
        mock_api_instance.list_accounts.side_effect = Exception("Network error")
        mock_api.return_value = mock_api_instance
        
        # Create trader instance
        trader = BTCTrader()
        trader.api = mock_api_instance
        
        # Test connection
        result = trader.test_api_connection()
        
        # Assertions
        self.assertFalse(result)
        self.assertIn("OFFLINE", trader.test_result_var.get())
        self.assertIn("Connection failed", trader.test_result_var.get())
        
    @patch('btc_trader.CoinbaseCompleteAPI')
    def test_api_connection_no_accounts(self, mock_api):
        """Test API connection with no accounts returned"""
        # Mock API with empty accounts
        mock_api_instance = Mock()
        mock_api_instance.is_jwt_format = True
        mock_api_instance.list_accounts.return_value = {'accounts': []}
        mock_api.return_value = mock_api_instance
        
        # Create trader instance
        trader = BTCTrader()
        trader.api = mock_api_instance
        
        # Test connection
        result = trader.test_api_connection()
        
        # Assertions
        self.assertFalse(result)
        self.assertIn("PARTIAL", trader.test_result_var.get())


class TestAPIKeyVisibility(unittest.TestCase):
    """Test cases for API key visibility toggle"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level Tk instance"""
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except:
            # Reuse existing root if one exists
            pass
        
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level Tk instance"""
        try:
            if hasattr(cls, 'root'):
                cls.root.destroy()
        except:
            pass
    
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_toggle_api_key_visibility(self, mock_config, mock_api):
        """Test toggling API key visibility"""
        # Set up mock config
        mock_config.COINBASE_API_KEY = "test_key_12345678"
        mock_config.COINBASE_API_SECRET = "test_secret_12345678"
        mock_config.TRADING_MODE = "SIMULATION"
        mock_config.is_live_mode.return_value = False
        
        # Mock API
        mock_api_instance = Mock()
        mock_api_instance.is_jwt_format = False
        mock_api.return_value = mock_api_instance
        
        # Create trader instance
        trader = BTCTrader()
        
        # Initial state - key should be masked
        initial_value = trader.api_key_var.get()
        self.assertIn("*", initial_value)
        self.assertFalse(trader.api_key_visible)
        
        # Toggle to visible
        trader.toggle_api_key_visibility()
        visible_value = trader.api_key_var.get()
        self.assertEqual(visible_value, mock_config.COINBASE_API_KEY)
        self.assertTrue(trader.api_key_visible)
        
        # Toggle back to hidden
        trader.toggle_api_key_visibility()
        hidden_value = trader.api_key_var.get()
        self.assertIn("*", hidden_value)
        self.assertFalse(trader.api_key_visible)
    
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_toggle_api_secret_visibility(self, mock_config, mock_api):
        """Test toggling API secret visibility"""
        # Set up mock config
        mock_config.COINBASE_API_KEY = "test_key_12345678"
        mock_config.COINBASE_API_SECRET = "test_secret_12345678"
        mock_config.TRADING_MODE = "SIMULATION"
        mock_config.is_live_mode.return_value = False
        
        # Mock API
        mock_api_instance = Mock()
        mock_api_instance.is_jwt_format = False
        mock_api.return_value = mock_api_instance
        
        # Create trader instance
        trader = BTCTrader()
        
        # Initial state - secret should be masked
        initial_value = trader.api_secret_var.get()
        self.assertIn("*", initial_value)
        self.assertFalse(trader.api_secret_visible)
        
        # Toggle to visible
        trader.toggle_api_secret_visibility()
        visible_value = trader.api_secret_var.get()
        self.assertEqual(visible_value, mock_config.COINBASE_API_SECRET)
        self.assertTrue(trader.api_secret_visible)
        
        # Toggle back to hidden
        trader.toggle_api_secret_visibility()
        hidden_value = trader.api_secret_var.get()
        self.assertIn("*", hidden_value)
        self.assertFalse(trader.api_secret_visible)
    
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_mask_api_key(self, mock_config, mock_api):
        """Test API key masking function"""
        # Set up mock config
        mock_config.COINBASE_API_KEY = "test_key_12345678"
        mock_config.COINBASE_API_SECRET = "test_secret_12345678"
        mock_config.TRADING_MODE = "SIMULATION"
        mock_config.is_live_mode.return_value = False
        
        # Mock API
        mock_api_instance = Mock()
        mock_api_instance.is_jwt_format = False
        mock_api.return_value = mock_api_instance
        
        # Create trader instance
        trader = BTCTrader()
        
        # Test masking
        masked = trader.mask_api_key("test_key_12345678")
        self.assertTrue(masked.startswith("test"))
        self.assertTrue(masked.endswith("5678"))
        self.assertIn("*", masked)
        
        # Test short key
        masked_short = trader.mask_api_key("short")
        self.assertEqual(masked_short, "Not Set")
        
        # Test empty key
        masked_empty = trader.mask_api_key("")
        self.assertEqual(masked_empty, "Not Set")


if __name__ == '__main__':
    unittest.main()
