"""
Unit tests for the Buying Testing tab functionality
Tests manual buy/sell operations with both DRY RUN and LIVE modes
"""
import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBuyingTestingTab(unittest.TestCase):
    """Test the Buying Testing tab functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.root_mock = MagicMock()
        self.mock_stringvar = MagicMock()
        self.mock_booleanvar = MagicMock()
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_buying_testing_tab_created(self, mock_config, mock_api, mock_tk,
                                        mock_stringvar, mock_booleanvar, mock_ttk):
        """Test that Buying Testing tab is created with all components"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Verify tab was created
        self.assertTrue(hasattr(trader, 'testing_tab'), 
                       "Buying Testing tab should be created")
        self.assertTrue(hasattr(trader, 'test_buy_amount_var'),
                       "Test buy amount variable should exist")
        self.assertTrue(hasattr(trader, 'test_sell_amount_var'),
                       "Test sell amount variable should exist")
        self.assertTrue(hasattr(trader, 'test_buy_mode_var'),
                       "Test buy mode variable should exist")
        self.assertTrue(hasattr(trader, 'test_sell_mode_var'),
                       "Test sell mode variable should exist")
        
        print("\n✅ TEST PASSED: Buying Testing tab created with all components")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_set_test_market_price_buy(self, mock_config, mock_api, mock_tk,
                                       mock_stringvar, mock_booleanvar, mock_ttk):
        """Test setting buy price to market price"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Create StringVar mock that actually stores values
        test_buy_price_var = MagicMock()
        stored_value = None
        def set_value(val):
            nonlocal stored_value
            stored_value = val
        def get_value():
            return stored_value or "0"
        test_buy_price_var.set = set_value
        test_buy_price_var.get = get_value
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        trader.test_buy_price_var = test_buy_price_var
        trader.current_price = 95000.50
        
        # Call set_test_market_price_buy
        trader.set_test_market_price_buy()
        
        # Verify price was set
        self.assertEqual(stored_value, "95000.50",
                        "Buy price should be set to current market price")
        
        print(f"\n✅ TEST PASSED: Market price set to buy field: ${stored_value}")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_set_test_market_price_sell(self, mock_config, mock_api, mock_tk,
                                        mock_stringvar, mock_booleanvar, mock_ttk):
        """Test setting sell price to market price"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Create StringVar mock
        test_sell_price_var = MagicMock()
        stored_value = None
        def set_value(val):
            nonlocal stored_value
            stored_value = val
        test_sell_price_var.set = set_value
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        trader.test_sell_price_var = test_sell_price_var
        trader.current_price = 97500.25
        
        # Call set_test_market_price_sell
        trader.set_test_market_price_sell()
        
        # Verify price was set
        self.assertEqual(stored_value, "97500.25",
                        "Sell price should be set to current market price")
        
        print(f"\n✅ TEST PASSED: Market price set to sell field: ${stored_value}")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_set_test_all_btc(self, mock_config, mock_api, mock_tk,
                              mock_stringvar, mock_booleanvar, mock_ttk):
        """Test setting sell amount to all available BTC"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Create StringVar mock
        test_sell_amount_var = MagicMock()
        stored_value = None
        def set_value(val):
            nonlocal stored_value
            stored_value = val
        test_sell_amount_var.set = set_value
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        trader.test_sell_amount_var = test_sell_amount_var
        trader.balance_btc = 0.00123456
        
        # Call set_test_all_btc
        trader.set_test_all_btc()
        
        # Verify amount was set
        self.assertEqual(stored_value, "0.00123456",
                        "Sell amount should be set to all available BTC")
        
        print(f"\n✅ TEST PASSED: Sell amount set to all BTC: {stored_value}")


class TestBuyingTestingExecutions(unittest.TestCase):
    """Test actual buy/sell executions in the testing tab"""
    
    def setUp(self):
        """Setup test environment"""
        self.root_mock = MagicMock()
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_execute_test_buy_dry_run(self, mock_config, mock_api, mock_tk,
                                       mock_stringvar, mock_booleanvar, mock_ttk):
        """Test executing a buy in DRY RUN mode"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Setup initial state
        trader.balance_usd = 1000.0
        trader.balance_btc = 0.0
        trader.current_price = 100000.0
        trader.buy_fee_rate = 0.006
        
        # Create mock variables
        trader.test_buy_amount_var = Mock()
        trader.test_buy_amount_var.get.return_value = "200.00"
        
        trader.test_buy_price_var = Mock()
        trader.test_buy_price_var.get.return_value = "100000.00"
        
        trader.test_buy_mode_var = Mock()
        trader.test_buy_mode_var.get.return_value = True  # DRY RUN
        
        trader.test_buy_result_var = Mock()
        trader.test_balance_display_var = Mock()
        trader.balance_var = Mock()
        
        # Execute test buy
        trader.execute_test_buy()
        
        # Verify balances updated
        self.assertEqual(trader.balance_usd, 800.0,
                        "USD balance should decrease by $200")
        
        # Calculate expected BTC
        buy_fee = 200.0 * 0.006  # $1.20
        net_investment = 200.0 - buy_fee  # $198.80
        expected_btc = net_investment / 100000.0  # 0.001988
        
        self.assertAlmostEqual(trader.balance_btc, expected_btc, places=8,
                              msg="BTC balance should increase correctly")
        
        # Verify result was set (called)
        self.assertTrue(trader.test_buy_result_var.set.called,
                       "Result message should be set")
        
        print(f"\n✅ TEST PASSED: DRY RUN buy executed")
        print(f"   USD: ${trader.balance_usd:.2f}")
        print(f"   BTC: {trader.balance_btc:.8f}")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_execute_test_sell_dry_run(self, mock_config, mock_api, mock_tk,
                                        mock_stringvar, mock_booleanvar, mock_ttk):
        """Test executing a sell in DRY RUN mode"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Setup initial state
        trader.balance_usd = 500.0
        trader.balance_btc = 0.002
        trader.current_price = 100000.0
        trader.sell_fee_rate = 0.006
        
        # Create mock variables
        trader.test_sell_amount_var = Mock()
        trader.test_sell_amount_var.get.return_value = "0.001"
        
        trader.test_sell_price_var = Mock()
        trader.test_sell_price_var.get.return_value = "100000.00"
        
        trader.test_sell_mode_var = Mock()
        trader.test_sell_mode_var.get.return_value = True  # DRY RUN
        
        trader.test_sell_result_var = Mock()
        trader.test_balance_display_var = Mock()
        trader.balance_var = Mock()
        
        # Execute test sell
        trader.execute_test_sell()
        
        # Verify balances updated
        self.assertEqual(trader.balance_btc, 0.001,
                        "BTC balance should decrease by 0.001")
        
        # Calculate expected USD
        gross_proceeds = 0.001 * 100000.0  # $100
        sell_fee = gross_proceeds * 0.006  # $0.60
        net_proceeds = gross_proceeds - sell_fee  # $99.40
        expected_usd = 500.0 + net_proceeds  # $599.40
        
        self.assertAlmostEqual(trader.balance_usd, expected_usd, places=2,
                              msg="USD balance should increase correctly")
        
        # Verify result was set
        self.assertTrue(trader.test_sell_result_var.set.called,
                       "Result message should be set")
        
        print(f"\n✅ TEST PASSED: DRY RUN sell executed")
        print(f"   USD: ${trader.balance_usd:.2f}")
        print(f"   BTC: {trader.balance_btc:.8f}")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_execute_test_buy_insufficient_funds(self, mock_config, mock_api, mock_tk,
                                                  mock_stringvar, mock_booleanvar, mock_ttk):
        """Test buy fails with insufficient funds in LIVE mode"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Setup initial state - insufficient balance
        trader.balance_usd = 50.0
        trader.balance_btc = 0.0
        trader.current_price = 100000.0
        
        # Create mock variables
        trader.test_buy_amount_var = Mock()
        trader.test_buy_amount_var.get.return_value = "200.00"  # More than available
        
        trader.test_buy_price_var = Mock()
        trader.test_buy_price_var.get.return_value = "100000.00"
        
        trader.test_buy_mode_var = Mock()
        trader.test_buy_mode_var.get.return_value = False  # LIVE mode validates balance
        
        trader.test_buy_result_var = Mock()
        
        # Mock price validation to pass (so we can test balance validation)
        trader.validate_price_before_execution = Mock(return_value=(True, 100000.0, None))
        
        # Execute test buy
        trader.execute_test_buy()
        
        # Verify balances unchanged
        self.assertEqual(trader.balance_usd, 50.0,
                        "USD balance should not change")
        self.assertEqual(trader.balance_btc, 0.0,
                        "BTC balance should not change")
        
        # Verify error message was set
        call_args = trader.test_buy_result_var.set.call_args
        self.assertIsNotNone(call_args, "Error message should be set")
        error_msg = call_args[0][0]
        self.assertIn("Insufficient", error_msg,
                     "Error message should mention insufficient balance or funds")
        
        print(f"\n✅ TEST PASSED: Buy correctly rejected for insufficient funds in LIVE mode")
        print(f"   Error: {error_msg}")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_execute_test_sell_insufficient_btc(self, mock_config, mock_api, mock_tk,
                                                 mock_stringvar, mock_booleanvar, mock_ttk):
        """Test sell fails with insufficient BTC in LIVE mode"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Setup initial state - insufficient BTC
        trader.balance_usd = 1000.0
        trader.balance_btc = 0.0005
        trader.current_price = 100000.0
        
        # Create mock variables
        trader.test_sell_amount_var = Mock()
        trader.test_sell_amount_var.get.return_value = "0.001"  # More than available
        
        trader.test_sell_price_var = Mock()
        trader.test_sell_price_var.get.return_value = "100000.00"
        
        trader.test_sell_mode_var = Mock()
        trader.test_sell_mode_var.get.return_value = False  # LIVE mode validates balance
        
        trader.test_sell_result_var = Mock()
        
        # Mock price validation to pass (so we can test balance validation)
        trader.validate_price_before_execution = Mock(return_value=(True, 100000.0, None))
        
        # Execute test sell
        trader.execute_test_sell()
        
        # Verify balances unchanged
        self.assertEqual(trader.balance_usd, 1000.0,
                        "USD balance should not change")
        self.assertEqual(trader.balance_btc, 0.0005,
                        "BTC balance should not change")
        
        # Verify error message was set
        call_args = trader.test_sell_result_var.set.call_args
        self.assertIsNotNone(call_args, "Error message should be set")
        error_msg = call_args[0][0]
        self.assertIn("Insufficient BTC", error_msg,
                     "Error message should mention insufficient BTC")
        
        print(f"\n✅ TEST PASSED: Sell correctly rejected for insufficient BTC in LIVE mode")
        print(f"   Error: {error_msg}")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_execute_test_buy_invalid_price(self, mock_config, mock_api, mock_tk,
                                            mock_stringvar, mock_booleanvar, mock_ttk):
        """Test buy fails with invalid price (no monitoring started)"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Setup initial state - no current price
        trader.balance_usd = 1000.0
        trader.balance_btc = 0.0
        trader.current_price = 0.0  # No price data
        
        # Create mock variables
        trader.test_buy_amount_var = Mock()
        trader.test_buy_amount_var.get.return_value = "100.00"
        
        trader.test_buy_price_var = Mock()
        trader.test_buy_price_var.get.return_value = "0"  # Use market (but no price)
        
        trader.test_buy_mode_var = Mock()
        trader.test_buy_mode_var.get.return_value = True
        
        trader.test_buy_result_var = Mock()
        
        # Execute test buy
        trader.execute_test_buy()
        
        # Verify balances unchanged
        self.assertEqual(trader.balance_usd, 1000.0,
                        "USD balance should not change")
        
        # Verify error message
        call_args = trader.test_buy_result_var.set.call_args
        self.assertIsNotNone(call_args, "Error message should be set")
        error_msg = call_args[0][0]
        self.assertIn("Invalid price", error_msg,
                     "Error message should mention invalid price")
        
        print(f"\n✅ TEST PASSED: Buy correctly rejected for invalid price")
        print(f"   Error: {error_msg}")


class TestBuyingTestingFeeCalculations(unittest.TestCase):
    """Test fee calculations in the testing tab"""
    
    def setUp(self):
        """Setup test environment"""
        self.root_mock = MagicMock()
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_buy_fee_calculation(self, mock_config, mock_api, mock_tk,
                                 mock_stringvar, mock_booleanvar, mock_ttk):
        """Test buy fee is calculated correctly at 0.6%"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Setup test
        trader.balance_usd = 1000.0
        trader.balance_btc = 0.0
        trader.current_price = 100000.0
        trader.buy_fee_rate = 0.006  # 0.6%
        
        # Create mock variables
        trader.test_buy_amount_var = Mock()
        trader.test_buy_amount_var.get.return_value = "500.00"
        
        trader.test_buy_price_var = Mock()
        trader.test_buy_price_var.get.return_value = "100000.00"
        
        trader.test_buy_mode_var = Mock()
        trader.test_buy_mode_var.get.return_value = True
        
        trader.test_buy_result_var = Mock()
        trader.test_balance_display_var = Mock()
        trader.balance_var = Mock()
        
        # Execute buy
        trader.execute_test_buy()
        
        # Calculate expected values
        buy_amount = 500.0
        buy_fee = buy_amount * 0.006  # $3.00
        net_investment = buy_amount - buy_fee  # $497.00
        btc_received = net_investment / 100000.0  # 0.00497
        
        self.assertAlmostEqual(trader.balance_btc, btc_received, places=8,
                              msg=f"BTC should be {btc_received:.8f}")
        
        print(f"\n✅ TEST PASSED: Buy fee calculation correct")
        print(f"   Buy Amount: ${buy_amount:.2f}")
        print(f"   Buy Fee (0.6%): ${buy_fee:.2f}")
        print(f"   Net Investment: ${net_investment:.2f}")
        print(f"   BTC Received: {btc_received:.8f}")
    
    @patch('btc_trader.ttk')
    @patch('btc_trader.tk.BooleanVar')
    @patch('btc_trader.tk.StringVar')
    @patch('btc_trader.tk.Tk')
    @patch('btc_trader.CoinbaseCompleteAPI')
    @patch('btc_trader.Config')
    def test_sell_fee_calculation(self, mock_config, mock_api, mock_tk,
                                  mock_stringvar, mock_booleanvar, mock_ttk):
        """Test sell fee is calculated correctly at 0.6%"""
        # Setup mocks
        mock_tk.return_value = self.root_mock
        mock_config.is_live_mode.return_value = False
        
        api_instance = Mock()
        api_instance.is_jwt_format = False
        mock_api.return_value = api_instance
        
        # Import and create BTCTrader
        from btc_trader import BTCTrader
        trader = BTCTrader()
        
        # Setup test
        trader.balance_usd = 0.0
        trader.balance_btc = 0.005
        trader.current_price = 100000.0
        trader.sell_fee_rate = 0.006  # 0.6%
        
        # Create mock variables
        trader.test_sell_amount_var = Mock()
        trader.test_sell_amount_var.get.return_value = "0.005"
        
        trader.test_sell_price_var = Mock()
        trader.test_sell_price_var.get.return_value = "100000.00"
        
        trader.test_sell_mode_var = Mock()
        trader.test_sell_mode_var.get.return_value = True
        
        trader.test_sell_result_var = Mock()
        trader.test_balance_display_var = Mock()
        trader.balance_var = Mock()
        
        # Execute sell
        trader.execute_test_sell()
        
        # Calculate expected values
        btc_sold = 0.005
        gross_proceeds = btc_sold * 100000.0  # $500.00
        sell_fee = gross_proceeds * 0.006  # $3.00
        net_proceeds = gross_proceeds - sell_fee  # $497.00
        
        self.assertAlmostEqual(trader.balance_usd, net_proceeds, places=2,
                              msg=f"USD should be ${net_proceeds:.2f}")
        
        print(f"\n✅ TEST PASSED: Sell fee calculation correct")
        print(f"   BTC Sold: {btc_sold:.8f}")
        print(f"   Gross Proceeds: ${gross_proceeds:.2f}")
        print(f"   Sell Fee (0.6%): ${sell_fee:.2f}")
        print(f"   Net Proceeds: ${net_proceeds:.2f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
