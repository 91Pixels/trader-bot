"""
Test to verify entry price persistence in database
"""
import unittest
import os
from database import TradingDatabase


class TestEntryPricePersistence(unittest.TestCase):
    """Test entry price is saved and loaded from database"""
    
    def setUp(self):
        """Create test database"""
        self.test_db_path = "test_entry_persistence.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = TradingDatabase(self.test_db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_save_and_restore_entry_price(self):
        """Test that entry price is saved and can be restored"""
        # Simulate syncing entry price from Coinbase
        entry_price = 112413.63
        position_size = 6.88
        btc_amount = 0.00006117
        target_price = 115919.49
        stop_loss = 111289.49
        
        # Save to database
        self.db.save_session(
            last_buy_price=entry_price,
            position_size=position_size,
            btc_amount=btc_amount,
            target_price=target_price,
            stop_loss=stop_loss
        )
        
        print(f"\n✅ Saved entry price to DB: ${entry_price:,.2f}")
        
        # Retrieve from database
        session = self.db.get_active_session()
        
        # Verify
        self.assertIsNotNone(session, "Session should exist")
        self.assertEqual(session['last_buy_price'], entry_price)
        self.assertEqual(session['position_size'], position_size)
        self.assertEqual(session['btc_amount'], btc_amount)
        self.assertEqual(session['target_price'], target_price)
        
        print(f"✅ Retrieved entry price from DB: ${session['last_buy_price']:,.2f}")
        print(f"✅ Entry price persistence: WORKING")
    
    def test_entry_price_persists_after_db_close(self):
        """Test entry price survives database close/reopen"""
        # Save entry price
        entry_price = 112413.63
        self.db.save_session(
            last_buy_price=entry_price,
            position_size=6.88,
            btc_amount=0.00006117,
            target_price=115919.49,
            stop_loss=111289.49
        )
        
        # Close database
        self.db.close()
        
        # Reopen database (simulating app restart)
        self.db = TradingDatabase(self.test_db_path)
        
        # Retrieve entry price
        session = self.db.get_active_session()
        
        # Verify
        self.assertIsNotNone(session)
        self.assertEqual(session['last_buy_price'], entry_price)
        
        print(f"\n✅ Entry price survived DB close/reopen: ${entry_price:,.2f}")
    
    def test_entry_price_updates_correctly(self):
        """Test that entry price can be updated"""
        # Initial entry
        initial_entry = 110000.00
        self.db.save_session(
            last_buy_price=initial_entry,
            position_size=5.00,
            btc_amount=0.00004545,
            target_price=113430.58,
            stop_loss=108900.00
        )
        
        # Update with new entry (from Coinbase sync)
        new_entry = 112413.63
        self.db.save_session(
            last_buy_price=new_entry,
            position_size=6.88,
            btc_amount=0.00006117,
            target_price=115919.49,
            stop_loss=111289.49
        )
        
        # Retrieve
        session = self.db.get_active_session()
        
        # Verify it's the new entry
        self.assertEqual(session['last_buy_price'], new_entry)
        self.assertNotEqual(session['last_buy_price'], initial_entry)
        
        print(f"\n✅ Entry price updated: ${initial_entry:,.2f} → ${new_entry:,.2f}")
    
    def test_no_entry_price_initially(self):
        """Test behavior when no entry price exists"""
        # Try to get session when none exists
        session = self.db.get_active_session()
        
        # Should return None or empty
        if session:
            # If session exists (from previous run), entry should be 0
            self.assertEqual(session.get('last_buy_price', 0), 0)
        else:
            # No session exists
            self.assertIsNone(session)
        
        print("\n✅ Handled case with no entry price")
    
    def test_entry_price_with_multiple_sessions(self):
        """Test that only the latest entry price is active"""
        # Save first session
        self.db.save_session(
            last_buy_price=110000.00,
            position_size=5.00,
            btc_amount=0.00004545,
            target_price=113430.58,
            stop_loss=108900.00
        )
        
        # Save second session (should deactivate first)
        self.db.save_session(
            last_buy_price=112413.63,
            position_size=6.88,
            btc_amount=0.00006117,
            target_price=115919.49,
            stop_loss=111289.49
        )
        
        # Get active session
        session = self.db.get_active_session()
        
        # Should be the second (latest) entry
        self.assertEqual(session['last_buy_price'], 112413.63)
        
        print("\n✅ Only latest entry price is active: $112,413.63")


if __name__ == '__main__':
    unittest.main(verbosity=2)
