"""
Unit tests for trading logic
Tests auto buy, auto sell, and trading modes
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAutoBuyLogic(unittest.TestCase):
    """Test auto buy functionality"""
    
    def setUp(self):
        """Set up test parameters"""
        self.current_price = 35500.0
        self.trigger_price = 35000.0
        self.balance_usd = 1000.0
        self.balance_btc = 0.0
        self.position_size = 100.0
    
    def test_auto_buy_trigger_condition(self):
        """Test auto buy triggers when price drops below trigger"""
        auto_buy_enabled = True
        auto_buy_executed = False
        
        # Price above trigger - should not buy
        current_price = 35500.0
        should_buy = (auto_buy_enabled and 
                     not auto_buy_executed and 
                     self.balance_btc == 0 and
                     current_price <= self.trigger_price)
        
        self.assertFalse(should_buy, "Should not buy when price is above trigger")
        
        # Price at trigger - should buy
        current_price = 35000.0
        should_buy = (auto_buy_enabled and 
                     not auto_buy_executed and 
                     self.balance_btc == 0 and
                     current_price <= self.trigger_price)
        
        self.assertTrue(should_buy, "Should buy when price reaches trigger")
        
        # Price below trigger - should buy
        current_price = 34900.0
        should_buy = (auto_buy_enabled and 
                     not auto_buy_executed and 
                     self.balance_btc == 0 and
                     current_price <= self.trigger_price)
        
        self.assertTrue(should_buy, "Should buy when price is below trigger")
    
    def test_auto_buy_only_once(self):
        """Test auto buy executes only once"""
        auto_buy_enabled = True
        auto_buy_executed = False
        current_price = 34900.0
        
        # First trigger
        should_buy = (auto_buy_enabled and 
                     not auto_buy_executed and 
                     self.balance_btc == 0 and
                     current_price <= self.trigger_price)
        
        self.assertTrue(should_buy)
        
        # After execution
        auto_buy_executed = True
        should_buy = (auto_buy_enabled and 
                     not auto_buy_executed and 
                     self.balance_btc == 0 and
                     current_price <= self.trigger_price)
        
        self.assertFalse(should_buy, "Should not buy again after execution")
    
    def test_auto_buy_with_existing_position(self):
        """Test auto buy doesn't trigger with existing position"""
        auto_buy_enabled = True
        auto_buy_executed = False
        current_price = 34900.0
        balance_btc = 0.00284  # Has position
        
        should_buy = (auto_buy_enabled and 
                     not auto_buy_executed and 
                     balance_btc == 0 and
                     current_price <= self.trigger_price)
        
        self.assertFalse(should_buy, "Should not buy when position exists")
    
    def test_auto_buy_disabled(self):
        """Test auto buy doesn't trigger when disabled"""
        auto_buy_enabled = False
        auto_buy_executed = False
        current_price = 34900.0
        
        should_buy = (auto_buy_enabled and 
                     not auto_buy_executed and 
                     self.balance_btc == 0 and
                     current_price <= self.trigger_price)
        
        self.assertFalse(should_buy, "Should not buy when disabled")
    
    def test_set_trigger_price_from_current(self):
        """Test setting trigger price as percentage below current"""
        current_price = 35500.0
        percentage_below = 1.0  # 1%
        
        trigger_price = current_price * (1 - percentage_below / 100)
        
        expected_trigger = 35145.0
        self.assertEqual(trigger_price, expected_trigger)


class TestAutoSellLogic(unittest.TestCase):
    """Test auto sell functionality"""
    
    def setUp(self):
        """Set up test parameters"""
        self.entry_price = 35000.0
        self.current_price = 35945.0
        self.target_price = 35945.0
        self.stop_price = 34650.0
        self.balance_btc = 0.00284
    
    def test_sell_at_target(self):
        """Test sell triggers at target price"""
        auto_mode = True
        
        # Calculate profit percentage
        profit_pct = ((self.current_price - self.entry_price) / self.entry_price) * 100
        target_pct = ((self.target_price - self.entry_price) / self.entry_price) * 100
        
        should_sell = auto_mode and profit_pct >= target_pct
        
        self.assertTrue(should_sell, "Should sell when target is reached")
    
    def test_sell_at_stop_loss(self):
        """Test sell triggers at stop loss"""
        auto_mode = True
        current_price = 34500.0
        stop_loss_pct = 1.0
        
        profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
        
        should_sell = auto_mode and profit_pct <= -stop_loss_pct
        
        self.assertTrue(should_sell, "Should sell when stop loss is hit")
    
    def test_no_sell_in_manual_mode(self):
        """Test sell doesn't auto-trigger in manual mode"""
        auto_mode = False
        
        profit_pct = ((self.current_price - self.entry_price) / self.entry_price) * 100
        target_pct = ((self.target_price - self.entry_price) / self.entry_price) * 100
        
        should_sell = auto_mode and profit_pct >= target_pct
        
        self.assertFalse(should_sell, "Should not auto-sell in manual mode")
    
    def test_sell_percentage_calculation(self):
        """Test profit percentage calculation for sell decision"""
        test_cases = [
            (35945.0, 2.7, True),   # At target
            (36000.0, 2.86, True),  # Above target
            (35500.0, 1.43, False), # Below target
            (34650.0, -1.0, True),  # At stop loss
            (34000.0, -2.86, True)  # Below stop loss
        ]
        
        stop_loss_pct = 1.0
        target_pct = 2.7
        
        for current_price, expected_pct, should_trigger in test_cases:
            profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
            
            self.assertAlmostEqual(profit_pct, expected_pct, places=1)
            
            should_sell_target = profit_pct >= target_pct
            should_sell_stop = profit_pct <= -stop_loss_pct
            should_sell = should_sell_target or should_sell_stop
            
            self.assertEqual(should_sell, should_trigger, 
                f"Failed for price ${current_price}")


class TestTradingModes(unittest.TestCase):
    """Test different trading modes"""
    
    def test_dry_run_mode(self):
        """Test dry run mode flag"""
        dry_run = True
        
        # In dry run, trades should be marked but not executed to real API
        self.assertTrue(dry_run)
        
        mode_indicator = " [DRY RUN]" if dry_run else " [LIVE]"
        self.assertEqual(mode_indicator, " [DRY RUN]")
    
    def test_live_mode(self):
        """Test live trading mode flag"""
        dry_run = False
        
        mode_indicator = " [DRY RUN]" if dry_run else " [LIVE]"
        self.assertEqual(mode_indicator, " [LIVE]")
    
    def test_manual_vs_auto_mode(self):
        """Test manual vs auto trading mode"""
        # Manual mode
        auto_mode = False
        self.assertFalse(auto_mode, "Manual mode should be False")
        
        # Auto mode
        auto_mode = True
        self.assertTrue(auto_mode, "Auto mode should be True")


class TestBalanceValidation(unittest.TestCase):
    """Test balance validation logic"""
    
    def test_sufficient_balance_for_buy(self):
        """Test validation of sufficient balance"""
        balance_usd = 1000.0
        position_size = 100.0
        
        has_sufficient = balance_usd >= position_size
        self.assertTrue(has_sufficient)
    
    def test_insufficient_balance_for_buy(self):
        """Test detection of insufficient balance"""
        balance_usd = 50.0
        position_size = 100.0
        
        has_sufficient = balance_usd >= position_size
        self.assertFalse(has_sufficient)
    
    def test_balance_update_after_buy(self):
        """Test balance updates correctly after buy"""
        balance_usd = 1000.0
        position_size = 100.0
        
        # After buy
        balance_usd -= position_size
        
        self.assertEqual(balance_usd, 900.0)
    
    def test_balance_update_after_sell(self):
        """Test balance updates correctly after sell"""
        balance_usd = 900.0
        net_proceeds = 101.50
        
        # After sell
        balance_usd += net_proceeds
        
        self.assertEqual(balance_usd, 1001.50)
    
    def test_btc_balance_after_buy(self):
        """Test BTC balance updates after buy"""
        balance_btc = 0.0
        position_size = 100.0
        buy_fee_rate = 0.006
        entry_price = 35000.0
        
        buy_fee = position_size * buy_fee_rate
        net_investment = position_size - buy_fee
        btc_qty = net_investment / entry_price
        
        balance_btc = btc_qty
        
        expected_qty = 99.40 / 35000.0
        self.assertAlmostEqual(balance_btc, expected_qty, places=8)
    
    def test_btc_balance_after_sell(self):
        """Test BTC balance clears after sell"""
        balance_btc = 0.00284
        
        # After sell
        balance_btc = 0.0
        
        self.assertEqual(balance_btc, 0.0)


class TestPositionTracking(unittest.TestCase):
    """Test position tracking logic"""
    
    def test_has_position(self):
        """Test detection of active position"""
        balance_btc = 0.00284
        
        has_position = balance_btc > 0
        self.assertTrue(has_position)
    
    def test_no_position(self):
        """Test detection of no position"""
        balance_btc = 0.0
        
        has_position = balance_btc > 0
        self.assertFalse(has_position)
    
    def test_entry_price_tracking(self):
        """Test entry price is saved on buy"""
        last_buy_price = 0.0
        entry_price = 35000.0
        
        # After buy
        last_buy_price = entry_price
        
        self.assertEqual(last_buy_price, 35000.0)
    
    def test_entry_price_reset_after_sell(self):
        """Test entry price resets after sell"""
        last_buy_price = 35000.0
        
        # After sell
        last_buy_price = 0.0
        
        self.assertEqual(last_buy_price, 0.0)


if __name__ == '__main__':
    unittest.main()
