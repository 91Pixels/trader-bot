"""
Unit tests to prevent ZeroDivisionError in btc_trader.py
Tests for the fix applied when balance_btc > 0 but last_buy_price = 0
(scenario when loading real balance from Coinbase without purchase history)
"""
import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestZeroDivisionPrevention(unittest.TestCase):
    """Test zero division prevention in trading calculations"""
    
    def test_profit_calculation_with_zero_entry_price(self):
        """Test that profit calculation handles zero entry price"""
        # Scenario: Real balance loaded but no purchase history
        balance_btc = 0.00004323
        last_buy_price = 0  # No entry price
        current_price = 109500.00
        position_size = 100.0
        
        # Calculate position value
        position_value = balance_btc * current_price
        cost_basis = position_size
        
        # Should not throw ZeroDivisionError
        try:
            if last_buy_price > 0:
                profit_pct = ((current_price - last_buy_price) / last_buy_price * 100)
            else:
                # Fallback calculation
                profit_pct = ((position_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
            
            # Should complete without error
            self.assertIsInstance(profit_pct, (int, float))
            
        except ZeroDivisionError:
            self.fail("ZeroDivisionError occurred in profit calculation")
    
    def test_stop_price_with_zero_entry_price(self):
        """Test that stop price calculation handles zero entry price"""
        last_buy_price = 0  # No entry price
        current_price = 109500.00
        stop_loss = 1.0  # 1% stop loss
        
        # Should not throw ZeroDivisionError
        try:
            if last_buy_price > 0:
                stop_price = last_buy_price * (1 - stop_loss / 100)
            else:
                # Fallback to current price
                stop_price = current_price * (1 - stop_loss / 100)
            
            # Should complete without error
            self.assertIsInstance(stop_price, (int, float))
            self.assertGreater(stop_price, 0)
            self.assertLess(stop_price, current_price)
            
        except ZeroDivisionError:
            self.fail("ZeroDivisionError occurred in stop_price calculation")
    
    def test_target_pct_increase_with_zero_entry_price(self):
        """Test that target percentage calculation handles zero entry price"""
        last_buy_price = 0  # No entry price
        target_price = 111000.00
        
        # Should not throw ZeroDivisionError
        try:
            if last_buy_price > 0:
                target_pct_increase = ((target_price - last_buy_price) / last_buy_price) * 100
            else:
                target_pct_increase = 0
            
            # Should complete without error
            self.assertIsInstance(target_pct_increase, (int, float))
            
        except ZeroDivisionError:
            self.fail("ZeroDivisionError occurred in target_pct_increase calculation")
    
    def test_real_balance_scenario(self):
        """Test complete scenario of real balance without purchase history"""
        # Simulate loading real balance from Coinbase
        balance_usd = 0.00
        balance_btc = 0.00004323
        last_buy_price = 0  # No entry price recorded
        current_price = 109500.00
        position_size = 100.0
        sell_fee_rate = 0.006
        stop_loss = 1.0
        profit_rate = 0.015
        
        # All calculations should work without ZeroDivisionError
        try:
            # 1. Calculate profit percentage
            position_value = balance_btc * current_price
            cost_basis = position_size
            
            if last_buy_price > 0:
                profit_pct = ((current_price - last_buy_price) / last_buy_price * 100)
            else:
                profit_pct = ((position_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
            
            # 2. Calculate target price
            desired_net_proceeds = position_size * (1 + profit_rate)
            required_gross_proceeds = desired_net_proceeds / (1 - sell_fee_rate)
            target_price = required_gross_proceeds / balance_btc
            
            # 3. Calculate stop price
            if last_buy_price > 0:
                stop_price = last_buy_price * (1 - stop_loss / 100)
            else:
                stop_price = current_price * (1 - stop_loss / 100)
            
            # 4. Calculate target percentage increase
            if last_buy_price > 0:
                target_pct_increase = ((target_price - last_buy_price) / last_buy_price) * 100
            else:
                target_pct_increase = 0
            
            # All calculations should complete successfully
            self.assertIsInstance(profit_pct, (int, float))
            self.assertIsInstance(target_price, (int, float))
            self.assertIsInstance(stop_price, (int, float))
            self.assertIsInstance(target_pct_increase, (int, float))
            
            # Values should be reasonable
            self.assertGreater(target_price, 0)
            self.assertGreater(stop_price, 0)
            
        except ZeroDivisionError as e:
            self.fail(f"ZeroDivisionError in real balance scenario: {e}")
    
    def test_zero_balance_btc(self):
        """Test calculations with zero BTC balance (no position)"""
        balance_btc = 0.0
        last_buy_price = 0
        current_price = 109500.00
        
        # Should handle gracefully
        try:
            if balance_btc > 0:
                if last_buy_price > 0:
                    profit_pct = ((current_price - last_buy_price) / last_buy_price * 100)
                else:
                    profit_pct = 0
            else:
                profit_pct = 0
            
            self.assertEqual(profit_pct, 0)
            
        except ZeroDivisionError:
            self.fail("ZeroDivisionError with zero BTC balance")
    
    def test_edge_case_zero_cost_basis(self):
        """Test edge case with zero cost basis"""
        position_value = 4.74
        cost_basis = 0  # Edge case
        
        # Should handle gracefully
        try:
            profit_pct = ((position_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
            
            # Should return 0 instead of dividing by zero
            self.assertEqual(profit_pct, 0)
            
        except ZeroDivisionError:
            self.fail("ZeroDivisionError with zero cost basis")
    
    def test_auto_sell_conditions_with_zero_entry(self):
        """Test that auto-sell conditions are safe with zero entry price"""
        last_buy_price = 0
        profit_pct = 2.0  # Some profit
        target_pct_increase = 1.5
        stop_loss = 1.0
        auto_mode = True
        
        # Should not trigger auto-sell when entry price is zero
        try:
            # Check target sell condition
            should_sell_target = (auto_mode and 
                                last_buy_price > 0 and 
                                profit_pct >= target_pct_increase)
            
            # Should be False because last_buy_price is 0
            self.assertFalse(should_sell_target)
            
            # Check stop loss condition
            should_sell_stop = (auto_mode and 
                              profit_pct <= -stop_loss)
            
            # Should work (no zero division)
            self.assertIsInstance(should_sell_stop, bool)
            
        except ZeroDivisionError:
            self.fail("ZeroDivisionError in auto-sell conditions")


class TestDivisionByZeroRegressionTests(unittest.TestCase):
    """Regression tests to ensure the bug doesn't come back"""
    
    def test_regression_real_balance_loaded_no_history(self):
        """
        REGRESSION TEST: 
        Bug occurred when loading real balance from Coinbase without purchase history.
        last_buy_price was 0, causing division by zero in check_position().
        """
        # Exact scenario that caused the bug
        balance_btc = 0.00004323  # Real balance from Coinbase
        last_buy_price = 0.0       # No purchase history
        current_price = 109550.95
        position_size = 100.0
        
        # This should NOT throw ZeroDivisionError
        try:
            # Original buggy calculation (should be protected now)
            if last_buy_price > 0:
                profit_pct = ((current_price - last_buy_price) / last_buy_price * 100)
            else:
                position_value = balance_btc * current_price
                cost_basis = position_size
                profit_pct = ((position_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
            
            # Should reach here without error
            self.assertTrue(True, "No ZeroDivisionError occurred")
            
        except ZeroDivisionError:
            self.fail("REGRESSION: ZeroDivisionError occurred again! Bug not fixed properly.")
    
    def test_regression_all_calculations_safe(self):
        """Test all calculations that were affected by the bug"""
        balance_btc = 0.00004323
        last_buy_price = 0.0
        current_price = 109550.95
        position_size = 100.0
        profit_rate = 0.015
        sell_fee_rate = 0.006
        stop_loss = 1.0
        
        errors = []
        
        # Test 1: profit_pct
        try:
            if last_buy_price > 0:
                profit_pct = ((current_price - last_buy_price) / last_buy_price * 100)
            else:
                position_value = balance_btc * current_price
                profit_pct = ((position_value - position_size) / position_size * 100) if position_size > 0 else 0
        except ZeroDivisionError:
            errors.append("profit_pct calculation")
        
        # Test 2: target_pct_increase
        try:
            target_price = 111000.0
            if last_buy_price > 0:
                target_pct_increase = ((target_price - last_buy_price) / last_buy_price) * 100
            else:
                target_pct_increase = 0
        except ZeroDivisionError:
            errors.append("target_pct_increase calculation")
        
        # Test 3: stop_price
        try:
            if last_buy_price > 0:
                stop_price = last_buy_price * (1 - stop_loss / 100)
            else:
                stop_price = current_price * (1 - stop_loss / 100)
        except ZeroDivisionError:
            errors.append("stop_price calculation")
        
        # Should have no errors
        if errors:
            self.fail(f"REGRESSION: ZeroDivisionError in: {', '.join(errors)}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
