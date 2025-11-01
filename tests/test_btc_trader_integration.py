"""
Integration test for btc_trader.py
Tests REAL code behavior with Coinbase wallet balance
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBTCTraderRealBalanceIntegration(unittest.TestCase):
    """Test actual btc_trader.py code with real Coinbase balance"""
    
    def setUp(self):
        """Setup test environment"""
        # Mock tkinter to avoid GUI creation
        self.root_mock = MagicMock()
        
        # Mock tkinter variables
        self.mock_stringvar = MagicMock()
        self.mock_doublevar = MagicMock()
        self.mock_intvar = MagicMock()
        self.mock_booleanvar = MagicMock()
        
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.IntVar')
    @patch('btc_trader.tk.DoubleVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_real_balance_displays_btc_value_not_100(self, mock_config, mock_api, mock_tk, 
                                                      mock_stringvar, mock_doublevar, mock_intvar, mock_booleanvar):
        """
        CRITICAL TEST: When real balance is loaded from Coinbase,
        Initial Investment should show BTC value, NOT $100
        """
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = True
        
        # Mock API with real balance
        api_instance = Mock()
        api_instance.is_jwt_format = True
        api_instance.list_accounts.return_value = {
            'accounts': [
                {'currency': 'BTC', 'available_balance': {'value': '0.00004323'}},
                {'currency': 'USD', 'available_balance': {'value': '0.00'}}
            ]
        }
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        
        trader = BTCTrader()
        
        # Verify real balance was loaded
        self.assertEqual(trader.balance_btc, 0.00004323,
                        "BTC balance should be loaded from Coinbase")
        self.assertTrue(trader.using_real_balance,
                       "using_real_balance should be True")
        
        # Mock amount_labels (would be created by create_gui)
        trader.amount_labels = {}
        for label in ['Initial Investment:', 'Buy Fee (0.6%):', 'Actual BTC Purchase:', 
                      '--- Current Position ---', 'Current BTC Value:', 'Current P/L (if sold now):',
                      '--- At Target Price ---', 'Value at Target:', 'Sell Fee (0.6%):', 
                      'Final Profit (at target):']:
            label_mock = Mock()
            label_mock.configure = Mock()
            trader.amount_labels[label] = label_mock
        
        # Set current price
        trader.current_price = 109839.76
        
        # Call check_position (this is what updates the display)
        trader.check_position()
        
        # Get the Initial Investment value that was set
        initial_investment_call = trader.amount_labels['Initial Investment:'].configure.call_args
        
        # Extract the text argument
        if initial_investment_call:
            kwargs = initial_investment_call[1]
            initial_investment_text = kwargs.get('text', '')
            
            # Parse the value
            import re
            match = re.search(r'\$([\d,]+\.\d+)', initial_investment_text)
            if match:
                value_str = match.group(1).replace(',', '')
                initial_investment_value = float(value_str)
                
                # CRITICAL ASSERTION: Should NOT be $100
                self.assertNotEqual(initial_investment_value, 100.0,
                                   f"Initial Investment should NOT be $100 with real balance! Got: {initial_investment_text}")
                
                # Should be BTC value (around $4.75 at current price)
                expected_value = 0.00004323 * 109839.76  # ~$4.75
                self.assertAlmostEqual(initial_investment_value, expected_value, delta=1.0,
                                      msg=f"Initial Investment should be ~$4.75, got {initial_investment_text}")
                
                print(f"\n✅ TEST PASSED: Initial Investment shows ${initial_investment_value:.2f} (real BTC value)")
                print(f"   NOT $100.00 (position_size)")
            else:
                self.fail(f"Could not parse Initial Investment value from: {initial_investment_text}")
        else:
            self.fail("Initial Investment was not configured")
    
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.IntVar')
    @patch('btc_trader.tk.DoubleVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_manual_entry_price_uses_btc_value(self, mock_config, mock_api, mock_tk,
                                                mock_stringvar, mock_doublevar, mock_intvar, mock_booleanvar):
        """
        When manual entry price is set, cost basis should be: BTC × Entry Price
        NOT position_size ($100)
        """
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = True
        
        # Mock API with real balance
        api_instance = Mock()
        api_instance.is_jwt_format = True
        api_instance.list_accounts.return_value = {
            'accounts': [
                {'currency': 'BTC', 'available_balance': {'value': '0.00004323'}},
                {'currency': 'USD', 'available_balance': {'value': '0.00'}}
            ]
        }
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        
        trader = BTCTrader()
        
        # Set manual entry price
        trader.last_buy_price = 70000.00
        trader.manual_entry_price = 70000.00
        
        # Mock amount_labels
        trader.amount_labels = {}
        for label in ['Initial Investment:', 'Buy Fee (0.6%):', 'Actual BTC Purchase:', 
                      '--- Current Position ---', 'Current BTC Value:', 'Current P/L (if sold now):',
                      '--- At Target Price ---', 'Value at Target:', 'Sell Fee (0.6%):', 
                      'Final Profit (at target):']:
            label_mock = Mock()
            label_mock.configure = Mock()
            trader.amount_labels[label] = label_mock
        
        # Set current price
        trader.current_price = 109839.76
        
        # Call check_position
        trader.check_position()
        
        # Get the Initial Investment value
        initial_investment_call = trader.amount_labels['Initial Investment:'].configure.call_args
        
        if initial_investment_call:
            kwargs = initial_investment_call[1]
            initial_investment_text = kwargs.get('text', '')
            
            import re
            match = re.search(r'\$([\d,]+\.\d+)', initial_investment_text)
            if match:
                value_str = match.group(1).replace(',', '')
                initial_investment_value = float(value_str)
                
                # Should be BTC × Entry Price = 0.00004323 × 70000 = $3.0261
                expected_value = 0.00004323 * 70000.00
                
                # CRITICAL ASSERTION: Should NOT be $100
                self.assertNotEqual(initial_investment_value, 100.0,
                                   f"With manual entry, Initial Investment should NOT be $100!")
                
                # Should be ~$3.03
                self.assertAlmostEqual(initial_investment_value, expected_value, delta=0.1,
                                      msg=f"Initial Investment should be ~$3.03, got {initial_investment_text}")
                
                print(f"\n✅ TEST PASSED: With manual entry $70,000")
                print(f"   Initial Investment: ${initial_investment_value:.2f} (BTC × Entry Price)")
                print(f"   NOT $100.00 (position_size)")
            else:
                self.fail(f"Could not parse value from: {initial_investment_text}")
        else:
            self.fail("Initial Investment was not configured")
    
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.IntVar')
    @patch('btc_trader.tk.DoubleVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_using_real_balance_flag_logic(self, mock_config, mock_api, mock_tk,
                                           mock_stringvar, mock_doublevar, mock_intvar, mock_booleanvar):
        """
        Test that using_real_balance flag correctly determines which values to use
        """
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_stringvar.return_value = self.mock_stringvar
        mock_doublevar.return_value = self.mock_doublevar
        mock_intvar.return_value = self.mock_intvar
        mock_booleanvar.return_value = self.mock_booleanvar
        mock_config.is_live_mode.return_value = True
        
        # Mock API
        api_instance = Mock()
        api_instance.is_jwt_format = True
        api_instance.list_accounts.return_value = {
            'accounts': [
                {'currency': 'BTC', 'available_balance': {'value': '0.00004323'}},
                {'currency': 'USD', 'available_balance': {'value': '0.00'}}
            ]
        }
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        
        trader = BTCTrader()
        
        # Verify flags
        self.assertTrue(trader.using_real_balance,
                       "using_real_balance should be True when real balance is loaded")
        self.assertEqual(trader.balance_btc, 0.00004323,
                        "balance_btc should be from Coinbase")
        
        print(f"\n✅ TEST PASSED: Flags are correct")
        print(f"   using_real_balance: {trader.using_real_balance}")
        print(f"   balance_btc: {trader.balance_btc}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
