"""
Unit tests for Coinbase API connection
Tests API connectivity, response format, and error handling
"""
import unittest
import requests
from unittest.mock import patch, Mock
import json


class TestCoinbaseAPI(unittest.TestCase):
    """Test Coinbase API integration"""
    
    def setUp(self):
        """Set up test parameters"""
        self.api_url = 'https://api.coinbase.com/v2/prices/BTC-USD/spot'
        self.timeout = 10
    
    def test_api_connectivity(self):
        """Test that we can connect to Coinbase API"""
        try:
            response = requests.get(self.api_url, timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
        except requests.RequestException as e:
            self.fail(f"Failed to connect to Coinbase API: {e}")
    
    def test_api_response_format(self):
        """Test that API returns correct JSON format"""
        response = requests.get(self.api_url, timeout=self.timeout)
        
        # Should return JSON
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        
        # Parse JSON
        data = response.json()
        
        # Check structure
        self.assertIn('data', data)
        self.assertIn('amount', data['data'])
        self.assertIn('currency', data['data'])
        
        # Check currency is USD
        self.assertEqual(data['data']['currency'], 'USD')
    
    def test_price_is_numeric(self):
        """Test that price can be converted to float"""
        response = requests.get(self.api_url, timeout=self.timeout)
        data = response.json()
        
        price_str = data['data']['amount']
        price = float(price_str)
        
        # Price should be positive
        self.assertGreater(price, 0)
        
        # Price should be reasonable (BTC between $1,000 and $1,000,000)
        self.assertGreater(price, 1000)
        self.assertLess(price, 1000000)
    
    def test_api_timeout_handling(self):
        """Test handling of API timeout"""
        with self.assertRaises(requests.Timeout):
            requests.get(self.api_url, timeout=0.001)
    
    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors"""
        # Mock 500 error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        response = mock_get(self.api_url)
        self.assertEqual(response.status_code, 500)
    
    @patch('requests.get')
    def test_invalid_json_handling(self, mock_get):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        mock_get.return_value = mock_response
        
        response = mock_get(self.api_url)
        with self.assertRaises(json.JSONDecodeError):
            response.json()
    
    @patch('requests.get')
    def test_missing_data_field(self, mock_get):
        """Test handling when 'data' field is missing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'error': 'Invalid response'}
        mock_get.return_value = mock_response
        
        response = mock_get(self.api_url)
        data = response.json()
        
        self.assertNotIn('data', data)
    
    @patch('requests.get')
    def test_missing_amount_field(self, mock_get):
        """Test handling when 'amount' field is missing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'currency': 'USD'}}
        mock_get.return_value = mock_response
        
        response = mock_get(self.api_url)
        data = response.json()
        
        self.assertNotIn('amount', data['data'])
    
    def test_multiple_requests_consistency(self):
        """Test that multiple requests return consistent data"""
        prices = []
        
        for _ in range(3):
            response = requests.get(self.api_url, timeout=self.timeout)
            data = response.json()
            price = float(data['data']['amount'])
            prices.append(price)
        
        # All prices should be within 5% of each other (reasonable for quick succession)
        min_price = min(prices)
        max_price = max(prices)
        variance = (max_price - min_price) / min_price
        
        self.assertLess(variance, 0.05, "Price variance too high between requests")
    
    @patch('requests.get')
    def test_successful_response_mock(self, mock_get):
        """Test mocked successful API response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'amount': '35000.00',
                'currency': 'USD'
            }
        }
        mock_get.return_value = mock_response
        
        response = mock_get(self.api_url)
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['amount'], '35000.00')
        self.assertEqual(float(data['data']['amount']), 35000.0)


class TestAPIRateLimiting(unittest.TestCase):
    """Test API rate limiting behavior"""
    
    def test_rapid_requests(self):
        """Test that rapid requests don't cause failures"""
        api_url = 'https://api.coinbase.com/v2/prices/BTC-USD/spot'
        success_count = 0
        
        # Make 10 rapid requests
        for _ in range(10):
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    success_count += 1
            except requests.RequestException:
                pass
        
        # At least 50% should succeed
        self.assertGreaterEqual(success_count, 5, 
            "Too many requests failed - possible rate limiting")


if __name__ == '__main__':
    unittest.main()
