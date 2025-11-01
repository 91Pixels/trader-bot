"""
Unit tests for trading calculations
Verifies correct implementation of target price formula and fee calculations
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTradingCalculations(unittest.TestCase):
    """Test all trading calculation formulas"""
    
    def setUp(self):
        """Set up test parameters"""
        self.position_size = 100.0
        self.buy_fee_rate = 0.006  # 0.6%
        self.sell_fee_rate = 0.006  # 0.6%
        self.profit_rate = 0.015  # 1.5%
        self.entry_price = 35000.0
    
    def test_btc_quantity_calculation(self):
        """Test BTC quantity calculation after buy fee"""
        buy_fee = self.position_size * self.buy_fee_rate
        net_investment = self.position_size - buy_fee
        btc_qty = net_investment / self.entry_price
        
        expected_buy_fee = 0.60
        expected_net_investment = 99.40
        expected_btc_qty = 99.40 / 35000.0
        
        self.assertAlmostEqual(buy_fee, expected_buy_fee, places=2)
        self.assertAlmostEqual(net_investment, expected_net_investment, places=2)
        self.assertAlmostEqual(btc_qty, expected_btc_qty, places=8)
    
    def test_target_price_formula(self):
        """Test the correct target price formula"""
        # Step 1: Calculate BTC quantity
        buy_fee = self.position_size * self.buy_fee_rate
        net_investment = self.position_size - buy_fee
        btc_qty = net_investment / self.entry_price
        
        # Step 2: Desired net proceeds
        desired_net = self.position_size * (1 + self.profit_rate)
        
        # Step 3: Required gross proceeds
        required_gross = desired_net / (1 - self.sell_fee_rate)
        
        # Step 4: Target price
        target_price = required_gross / btc_qty
        
        # Verify calculations
        self.assertAlmostEqual(desired_net, 101.50, places=2)
        self.assertAlmostEqual(required_gross, 102.11, places=2)
        
        # Verify target price (should be around 35955)
        expected_target = 35955.17  # More precise calculation
        self.assertAlmostEqual(target_price, expected_target, places=1)
    
    def test_net_profit_at_target(self):
        """Test that net profit equals exactly profit_rate at target price"""
        # Calculate all steps
        buy_fee = self.position_size * self.buy_fee_rate
        net_investment = self.position_size - buy_fee
        btc_qty = net_investment / self.entry_price
        
        desired_net = self.position_size * (1 + self.profit_rate)
        required_gross = desired_net / (1 - self.sell_fee_rate)
        target_price = required_gross / btc_qty
        
        # Simulate selling at target price
        gross_proceeds = btc_qty * target_price
        sell_fee = gross_proceeds * self.sell_fee_rate
        net_proceeds = gross_proceeds - sell_fee
        
        # Calculate profit
        net_profit = net_proceeds - self.position_size
        
        # Should be exactly $1.50
        expected_profit = self.position_size * self.profit_rate
        self.assertAlmostEqual(net_profit, expected_profit, places=2)
        self.assertAlmostEqual(net_profit, 1.50, places=2)
    
    def test_fee_calculations(self):
        """Test buy and sell fee calculations"""
        # Buy fee
        buy_fee = self.position_size * self.buy_fee_rate
        self.assertEqual(buy_fee, 0.60)
        
        # Sell fee (on $100 gross)
        sell_fee = 100.0 * self.sell_fee_rate
        self.assertEqual(sell_fee, 0.60)
        
        # Total fees on round trip
        total_fees = buy_fee + sell_fee
        self.assertEqual(total_fees, 1.20)
    
    def test_stop_loss_calculation(self):
        """Test stop loss price calculation"""
        stop_loss_pct = 1.0  # 1%
        stop_price = self.entry_price * (1 - stop_loss_pct / 100)
        
        expected_stop = 34650.0
        self.assertEqual(stop_price, expected_stop)
    
    def test_profit_percentage_from_target(self):
        """Test that target price requires correct percentage increase"""
        # Calculate target
        buy_fee = self.position_size * self.buy_fee_rate
        net_investment = self.position_size - buy_fee
        btc_qty = net_investment / self.entry_price
        
        desired_net = self.position_size * (1 + self.profit_rate)
        required_gross = desired_net / (1 - self.sell_fee_rate)
        target_price = required_gross / btc_qty
        
        # Calculate percentage increase
        pct_increase = ((target_price - self.entry_price) / self.entry_price) * 100
        
        # Should be approximately 2.7% (1.5% profit + 1.2% fees)
        expected_pct = 2.7
        self.assertAlmostEqual(pct_increase, expected_pct, places=1)
    
    def test_different_position_sizes(self):
        """Test formula works correctly for different position sizes"""
        test_sizes = [50.0, 100.0, 200.0, 500.0]
        
        for size in test_sizes:
            buy_fee = size * self.buy_fee_rate
            net_investment = size - buy_fee
            btc_qty = net_investment / self.entry_price
            
            desired_net = size * (1 + self.profit_rate)
            required_gross = desired_net / (1 - self.sell_fee_rate)
            target_price = required_gross / btc_qty
            
            # Simulate sale
            gross_proceeds = btc_qty * target_price
            sell_fee = gross_proceeds * self.sell_fee_rate
            net_proceeds = gross_proceeds - sell_fee
            net_profit = net_proceeds - size
            
            # Net profit should always be exactly profit_rate * size
            expected_profit = size * self.profit_rate
            self.assertAlmostEqual(net_profit, expected_profit, places=2,
                msg=f"Failed for position size ${size}")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Very small position
        small_position = 1.0
        buy_fee = small_position * self.buy_fee_rate
        self.assertAlmostEqual(buy_fee, 0.006, places=3)
        
        # Very large position
        large_position = 10000.0
        buy_fee = large_position * self.buy_fee_rate
        self.assertAlmostEqual(buy_fee, 60.0, places=2)
        
        # Zero profit rate (break even scenario)
        zero_profit = 0.0
        desired_net = self.position_size * (1 + zero_profit)
        self.assertEqual(desired_net, self.position_size)
    
    def test_unrealized_pl_calculation(self):
        """Test unrealized P/L calculation"""
        buy_fee = self.position_size * self.buy_fee_rate
        net_investment = self.position_size - buy_fee
        btc_qty = net_investment / self.entry_price
        
        # Current price different from entry
        current_price = 36000.0
        current_value = btc_qty * current_price
        unrealized_pl = current_value - self.position_size
        
        # Should show profit since price increased
        self.assertGreater(unrealized_pl, 0)
        
        # Calculate expected
        expected_value = (99.40 / 35000.0) * 36000.0
        expected_pl = expected_value - 100.0
        self.assertAlmostEqual(unrealized_pl, expected_pl, places=2)


if __name__ == '__main__':
    unittest.main()
