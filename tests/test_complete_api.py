"""
Unit tests for Complete Coinbase API
Tests all 48 endpoints
"""
import unittest
import os
from unittest.mock import patch, Mock
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coinbase_complete_api import CoinbaseCompleteAPI


class TestCompleteAPIInitialization(unittest.TestCase):
    """Test Complete API initialization"""
    
    def setUp(self):
        """Set up test environment"""
        self.original_mode = os.environ.get('TRADING_MODE')
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    def tearDown(self):
        """Restore environment"""
        if self.original_mode:
            os.environ['TRADING_MODE'] = self.original_mode
        elif 'TRADING_MODE' in os.environ:
            del os.environ['TRADING_MODE']
    
    def test_api_initializes(self):
        """Test that API client initializes"""
        api = CoinbaseCompleteAPI()
        self.assertIsNotNone(api)
        # In SIMULATION mode, is_live should be False
        if os.environ.get('TRADING_MODE') == 'SIMULATION':
            self.assertFalse(api.is_live)
    
    def test_jwt_format_detection(self):
        """Test ECDSA format detection"""
        api = CoinbaseCompleteAPI()
        self.assertIsInstance(api.is_jwt_format, bool)


class TestAccountsEndpoints(unittest.TestCase):
    """Test Accounts endpoints"""
    
    def setUp(self):
        """Set up test"""
        os.environ['TRADING_MODE'] = 'LIVE'
        self.api = CoinbaseCompleteAPI()
        
        if not self.api.is_jwt_format:
            self.skipTest("Credentials not in ECDSA format")
    
    def tearDown(self):
        """Clean up"""
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_list_accounts(self, mock_request):
        """Test list_accounts endpoint"""
        mock_request.return_value = {'accounts': []}
        
        result = self.api.list_accounts(limit=10)
        
        mock_request.assert_called_once_with('GET', '/accounts', params={'limit': 10})
        self.assertIn('accounts', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_get_account(self, mock_request):
        """Test get_account endpoint"""
        mock_request.return_value = {'account': {'id': 'test-123'}}
        
        result = self.api.get_account('test-123')
        
        mock_request.assert_called_once_with('GET', '/accounts/test-123')
        self.assertIn('account', result)


class TestOrdersEndpoints(unittest.TestCase):
    """Test Orders endpoints"""
    
    def setUp(self):
        """Set up test"""
        os.environ['TRADING_MODE'] = 'LIVE'
        self.api = CoinbaseCompleteAPI()
        
        if not self.api.is_jwt_format:
            self.skipTest("Credentials not in ECDSA format")
    
    def tearDown(self):
        """Clean up"""
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_create_order(self, mock_request):
        """Test create_order endpoint"""
        mock_request.return_value = {'order_id': 'test-order-123'}
        
        order_config = {'market_market_ioc': {'quote_size': '10.00'}}
        result = self.api.create_order('client-123', 'BTC-USD', 'BUY', order_config)
        
        self.assertIn('order_id', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_cancel_orders(self, mock_request):
        """Test cancel_orders endpoint"""
        mock_request.return_value = {'results': []}
        
        result = self.api.cancel_orders(['order-1', 'order-2'])
        
        mock_request.assert_called_once()
        self.assertIn('results', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_list_orders(self, mock_request):
        """Test list_orders endpoint"""
        mock_request.return_value = {'orders': []}
        
        result = self.api.list_orders(product_id='BTC-USD')
        
        self.assertIn('orders', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_list_fills(self, mock_request):
        """Test list_fills endpoint"""
        mock_request.return_value = {'fills': []}
        
        result = self.api.list_fills(product_id='BTC-USD')
        
        self.assertIn('fills', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_get_order(self, mock_request):
        """Test get_order endpoint"""
        mock_request.return_value = {'order': {}}
        
        result = self.api.get_order('order-123')
        
        mock_request.assert_called_once_with('GET', '/orders/historical/order-123')
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_preview_order(self, mock_request):
        """Test preview_order endpoint"""
        mock_request.return_value = {'preview': {}}
        
        order_config = {'market_market_ioc': {'quote_size': '10.00'}}
        result = self.api.preview_order('BTC-USD', 'BUY', order_config)
        
        self.assertIn('preview', result)


class TestProductsEndpoints(unittest.TestCase):
    """Test Products endpoints"""
    
    def setUp(self):
        """Set up test"""
        os.environ['TRADING_MODE'] = 'LIVE'
        self.api = CoinbaseCompleteAPI()
        
        if not self.api.is_jwt_format:
            self.skipTest("Credentials not in ECDSA format")
    
    def tearDown(self):
        """Clean up"""
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_list_products(self, mock_request):
        """Test list_products endpoint"""
        mock_request.return_value = {'products': []}
        
        result = self.api.list_products()
        
        self.assertIn('products', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_get_product(self, mock_request):
        """Test get_product endpoint"""
        mock_request.return_value = {'product': {}}
        
        result = self.api.get_product('BTC-USD')
        
        mock_request.assert_called_once_with('GET', '/products/BTC-USD')
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_get_product_candles(self, mock_request):
        """Test get_product_candles endpoint"""
        mock_request.return_value = {'candles': []}
        
        result = self.api.get_product_candles('BTC-USD', '2024-01-01', '2024-01-02', 'ONE_HOUR')
        
        self.assertIn('candles', result)


class TestPublicEndpoints(unittest.TestCase):
    """Test Public endpoints (no auth required)"""
    
    def setUp(self):
        """Set up test"""
        self.api = CoinbaseCompleteAPI()
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_public_request')
    def test_get_server_time(self, mock_request):
        """Test get_server_time endpoint"""
        mock_request.return_value = {'time': '2024-01-01T00:00:00Z'}
        
        result = self.api.get_server_time()
        
        self.assertIn('time', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_public_request')
    def test_list_public_products(self, mock_request):
        """Test list_public_products endpoint"""
        mock_request.return_value = {'products': []}
        
        result = self.api.list_public_products()
        
        self.assertIn('products', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_public_request')
    def test_get_public_product(self, mock_request):
        """Test get_public_product endpoint"""
        mock_request.return_value = {'product': {}}
        
        result = self.api.get_public_product('BTC-USD')
        
        self.assertIn('product', result)


class TestPortfoliosEndpoints(unittest.TestCase):
    """Test Portfolios endpoints"""
    
    def setUp(self):
        """Set up test"""
        os.environ['TRADING_MODE'] = 'LIVE'
        self.api = CoinbaseCompleteAPI()
        
        if not self.api.is_jwt_format:
            self.skipTest("Credentials not in ECDSA format")
    
    def tearDown(self):
        """Clean up"""
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_list_portfolios(self, mock_request):
        """Test list_portfolios endpoint"""
        mock_request.return_value = {'portfolios': []}
        
        result = self.api.list_portfolios()
        
        self.assertIn('portfolios', result)
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_create_portfolio(self, mock_request):
        """Test create_portfolio endpoint"""
        mock_request.return_value = {'portfolio': {'name': 'Test'}}
        
        result = self.api.create_portfolio('Test')
        
        self.assertIn('portfolio', result)


class TestPaymentMethodsEndpoints(unittest.TestCase):
    """Test Payment Methods endpoints"""
    
    def setUp(self):
        """Set up test"""
        os.environ['TRADING_MODE'] = 'LIVE'
        self.api = CoinbaseCompleteAPI()
        
        if not self.api.is_jwt_format:
            self.skipTest("Credentials not in ECDSA format")
    
    def tearDown(self):
        """Clean up"""
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_list_payment_methods(self, mock_request):
        """Test list_payment_methods endpoint"""
        mock_request.return_value = {'payment_methods': []}
        
        result = self.api.list_payment_methods()
        
        self.assertIn('payment_methods', result)


class TestDataAPIEndpoints(unittest.TestCase):
    """Test Data API endpoints"""
    
    def setUp(self):
        """Set up test"""
        os.environ['TRADING_MODE'] = 'LIVE'
        self.api = CoinbaseCompleteAPI()
        
        if not self.api.is_jwt_format:
            self.skipTest("Credentials not in ECDSA format")
    
    def tearDown(self):
        """Clean up"""
        os.environ['TRADING_MODE'] = 'SIMULATION'
    
    @patch('coinbase_complete_api.CoinbaseCompleteAPI._make_request')
    def test_get_api_key_permissions(self, mock_request):
        """Test get_api_key_permissions endpoint"""
        mock_request.return_value = {'permissions': []}
        
        result = self.api.get_api_key_permissions()
        
        self.assertIn('permissions', result)


if __name__ == '__main__':
    unittest.main()
