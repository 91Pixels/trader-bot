"""
Unit tests for SQLite Database persistence
Tests all database operations: save, load, restore, export
"""
import unittest
import os
import tempfile
import shutil
import time
from datetime import datetime
from database import TradingDatabase


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection and initialization"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
        self.db = TradingDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_database_connection(self):
        """Test that database connects successfully"""
        self.assertIsNotNone(self.db.conn)
        self.assertIsNotNone(self.db.cursor)
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_tables_created(self):
        """Test that all required tables are created"""
        self.db.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in self.db.cursor.fetchall()]
        
        self.assertIn('trades', tables)
        self.assertIn('sessions', tables)
        self.assertIn('statistics', tables)


class TestTradeOperations(unittest.TestCase):
    """Test trade save and retrieve operations"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
        self.db = TradingDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_save_buy_trade(self):
        """Test saving a BUY trade"""
        trade_id = self.db.save_trade(
            trade_type="BUY",
            price=110000.0,
            amount_usd=10.0,
            amount_btc=0.00009,
            fee=0.06,
            profit=0,
            mode="DRY RUN",
            notes="Test buy"
        )
        
        self.assertIsNotNone(trade_id)
        self.assertGreater(trade_id, 0)
    
    def test_save_sell_trade(self):
        """Test saving a SELL trade with profit"""
        trade_id = self.db.save_trade(
            trade_type="SELL",
            price=114100.0,
            amount_usd=10.21,
            amount_btc=0.00009,
            fee=0.06,
            profit=0.21,
            mode="DRY RUN",
            notes="Test sell"
        )
        
        self.assertIsNotNone(trade_id)
        self.assertGreater(trade_id, 0)
    
    def test_retrieve_trade_history(self):
        """Test retrieving trade history"""
        # Save multiple trades
        self.db.save_trade("BUY", 110000, 10, 0.00009, 0.06, 0, "DRY RUN", "Buy 1")
        self.db.save_trade("SELL", 114000, 10.2, 0.00009, 0.06, 0.2, "DRY RUN", "Sell 1")
        self.db.save_trade("BUY", 112000, 10, 0.0000892, 0.06, 0, "DRY RUN", "Buy 2")
        
        history = self.db.get_trade_history(limit=10)
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['trade_type'], 'BUY')  # Most recent first
        self.assertEqual(history[1]['trade_type'], 'SELL')
        self.assertEqual(history[2]['trade_type'], 'BUY')
    
    def test_trade_data_integrity(self):
        """Test that saved trade data matches retrieved data"""
        original_data = {
            'trade_type': 'BUY',
            'price': 110500.50,
            'amount_usd': 15.75,
            'amount_btc': 0.00014251,
            'fee': 0.0945,
            'profit': 0,
            'mode': 'LIVE',
            'notes': 'Test data integrity'
        }
        
        self.db.save_trade(**original_data)
        history = self.db.get_trade_history(limit=1)
        
        retrieved = history[0]
        self.assertEqual(retrieved['trade_type'], original_data['trade_type'])
        self.assertAlmostEqual(retrieved['price'], original_data['price'], places=2)
        self.assertAlmostEqual(retrieved['amount_usd'], original_data['amount_usd'], places=2)
        self.assertAlmostEqual(retrieved['amount_btc'], original_data['amount_btc'], places=8)
        self.assertEqual(retrieved['mode'], original_data['mode'])


class TestSessionOperations(unittest.TestCase):
    """Test session save and restore operations"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
        self.db = TradingDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_save_session(self):
        """Test saving a trading session"""
        session_id = self.db.save_session(
            last_buy_price=110000.0,
            position_size=10.0,
            btc_amount=0.00009,
            target_price=114070.0,
            stop_loss=108900.0
        )
        
        self.assertIsNotNone(session_id)
        self.assertGreater(session_id, 0)
    
    def test_get_active_session(self):
        """Test retrieving active session"""
        # Save a session
        self.db.save_session(
            last_buy_price=110000.0,
            position_size=10.0,
            btc_amount=0.00009,
            target_price=114070.0,
            stop_loss=108900.0
        )
        
        session = self.db.get_active_session()
        
        self.assertIsNotNone(session)
        self.assertEqual(session['last_buy_price'], 110000.0)
        self.assertEqual(session['position_size'], 10.0)
        self.assertAlmostEqual(session['btc_amount'], 0.00009, places=8)
    
    def test_close_session(self):
        """Test closing an active session"""
        # Save and close session
        self.db.save_session(110000, 10, 0.00009, 114070, 108900)
        self.db.close_session()
        
        session = self.db.get_active_session()
        
        self.assertIsNone(session)
    
    def test_multiple_sessions_only_one_active(self):
        """Test that only one session can be active at a time"""
        # Save first session
        self.db.save_session(110000, 10, 0.00009, 114070, 108900)
        
        # Save second session (should deactivate first)
        self.db.save_session(112000, 15, 0.000133, 116240, 110880)
        
        session = self.db.get_active_session()
        
        self.assertIsNotNone(session)
        self.assertEqual(session['last_buy_price'], 112000.0)  # Second session
        self.assertEqual(session['position_size'], 15.0)


class TestStatisticsOperations(unittest.TestCase):
    """Test statistics save and retrieve operations"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
        self.db = TradingDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_save_statistics(self):
        """Test saving trading statistics"""
        self.db.save_statistics(
            total_trades=10,
            winning_trades=7,
            total_profit=2.50,
            win_rate=70.0,
            roi=0.25
        )
        
        stats = self.db.get_latest_statistics()
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_trades'], 10)
        self.assertEqual(stats['winning_trades'], 7)
        self.assertAlmostEqual(stats['total_profit'], 2.50, places=2)
    
    def test_statistics_update(self):
        """Test updating statistics over time"""
        # First snapshot
        self.db.save_statistics(5, 3, 1.25, 60.0, 0.125)
        
        # Get first stats
        stats1 = self.db.get_latest_statistics()
        self.assertEqual(stats1['total_trades'], 5)
        
        # Second snapshot
        self.db.save_statistics(10, 7, 2.50, 70.0, 0.25)
        
        # Get latest stats
        stats2 = self.db.get_latest_statistics()
        self.assertEqual(stats2['total_trades'], 10)  # Latest values
        self.assertEqual(stats2['winning_trades'], 7)


class TestProfitAnalysis(unittest.TestCase):
    """Test profit summary and analysis functions"""
    
    def setUp(self):
        """Create temporary database with sample data"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
        self.db = TradingDatabase(self.db_path)
        
        # Create sample trades
        self.db.save_trade("BUY", 110000, 10, 0.00009, 0.06, 0, "DRY RUN", "Buy 1")
        self.db.save_trade("SELL", 114000, 10.25, 0.00009, 0.06, 0.25, "DRY RUN", "Profit sell")
        
        self.db.save_trade("BUY", 112000, 10, 0.0000892, 0.06, 0, "DRY RUN", "Buy 2")
        self.db.save_trade("SELL", 116000, 10.30, 0.0000892, 0.06, 0.30, "DRY RUN", "Profit sell")
        
        self.db.save_trade("BUY", 115000, 10, 0.0000869, 0.06, 0, "DRY RUN", "Buy 3")
        self.db.save_trade("SELL", 114500, 9.85, 0.0000869, 0.06, -0.15, "DRY RUN", "Loss sell")
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_profit_summary_calculations(self):
        """Test profit summary statistics"""
        summary = self.db.get_profit_summary()
        
        self.assertEqual(summary['total_trades'], 3)
        self.assertEqual(summary['winning_trades'], 2)
        self.assertAlmostEqual(summary['total_profit'], 0.40, places=2)
        self.assertAlmostEqual(summary['win_rate'], 66.666, places=1)
    
    def test_max_and_min_profit(self):
        """Test max and min profit calculations"""
        summary = self.db.get_profit_summary()
        
        self.assertAlmostEqual(summary['max_profit'], 0.30, places=2)
        self.assertAlmostEqual(summary['min_profit'], -0.15, places=2)
    
    def test_average_profit(self):
        """Test average profit calculation"""
        summary = self.db.get_profit_summary()
        
        expected_avg = (0.25 + 0.30 - 0.15) / 3
        self.assertAlmostEqual(summary['avg_profit'], expected_avg, places=2)
    
    def test_profit_summary_no_trades(self):
        """Test profit summary with no trades"""
        # Create empty database
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "empty.db")
        empty_db = TradingDatabase(db_path)
        
        summary = empty_db.get_profit_summary()
        
        self.assertEqual(summary['total_trades'], 0)
        self.assertEqual(summary['winning_trades'], 0)
        self.assertEqual(summary['total_profit'], 0)
        
        empty_db.close()
        shutil.rmtree(temp_dir)


class TestDataExport(unittest.TestCase):
    """Test data export functionality"""
    
    def setUp(self):
        """Create temporary database with sample data"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
        self.db = TradingDatabase(self.db_path)
        
        # Create sample trades
        self.db.save_trade("BUY", 110000, 10, 0.00009, 0.06, 0, "DRY RUN", "Test buy")
        self.db.save_trade("SELL", 114000, 10.25, 0.00009, 0.06, 0.25, "DRY RUN", "Test sell")
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_export_to_csv(self):
        """Test exporting trade history to CSV"""
        csv_path = os.path.join(self.test_dir, "test_export.csv")
        result = self.db.export_to_csv(csv_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_path))
        
        # Verify CSV content
        with open(csv_path, 'r') as f:
            content = f.read()
            self.assertIn('BUY', content)
            self.assertIn('SELL', content)
            self.assertIn('110000', content)


class TestDatabaseRecovery(unittest.TestCase):
    """Test database recovery and persistence"""
    
    def setUp(self):
        """Create temporary directory for database"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
    
    def tearDown(self):
        """Clean up test directory"""
        # Small delay to ensure Windows releases file locks
        time.sleep(0.1)
        try:
            shutil.rmtree(self.test_dir)
        except PermissionError:
            # Retry once after longer delay on Windows
            time.sleep(0.5)
            shutil.rmtree(self.test_dir)
    
    def test_data_persists_after_close(self):
        """Test that data persists after closing database"""
        # First session: save data
        db1 = TradingDatabase(self.db_path)
        db1.save_trade("BUY", 110000, 10, 0.00009, 0.06, 0, "DRY RUN", "Persist test")
        db1.save_session(110000, 10, 0.00009, 114070, 108900)
        db1.save_statistics(1, 0, 0, 0, 0)
        db1.close()
        
        # Second session: retrieve data
        db2 = TradingDatabase(self.db_path)
        
        history = db2.get_trade_history(limit=1)
        session = db2.get_active_session()
        stats = db2.get_latest_statistics()
        
        self.assertEqual(len(history), 1)
        self.assertIsNotNone(session)
        self.assertIsNotNone(stats)
        
        db2.close()
    
    def test_session_recovery(self):
        """Test recovering an open position after restart"""
        # Simulate bot closing with open position
        db1 = TradingDatabase(self.db_path)
        db1.save_session(
            last_buy_price=110000.0,
            position_size=10.0,
            btc_amount=0.00009,
            target_price=114070.0,
            stop_loss=108900.0
        )
        db1.close()
        
        # Simulate bot restarting
        db2 = TradingDatabase(self.db_path)
        session = db2.get_active_session()
        
        self.assertIsNotNone(session)
        self.assertEqual(session['last_buy_price'], 110000.0)
        self.assertEqual(session['position_size'], 10.0)
        
        db2.close()
    
    def test_statistics_accumulation(self):
        """Test statistics accumulate correctly over sessions"""
        # First session
        db1 = TradingDatabase(self.db_path)
        db1.save_statistics(5, 3, 1.25, 60.0, 0.125)
        
        # Verify first stats saved
        stats1 = db1.get_latest_statistics()
        self.assertEqual(stats1['total_trades'], 5)
        
        # Close connection properly
        db1.conn.close()
        time.sleep(0.2)  # Ensure Windows releases lock
        
        # Second session - adds more stats
        db2 = TradingDatabase(self.db_path)
        db2.save_statistics(10, 7, 2.50, 70.0, 0.25)
        
        # Verify latest stats
        stats2 = db2.get_latest_statistics()
        self.assertEqual(stats2['total_trades'], 10)
        self.assertEqual(stats2['winning_trades'], 7)
        
        # Close connection properly
        db2.conn.close()
        time.sleep(0.2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Create temporary database"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_trading.db")
        self.db = TradingDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up"""
        self.db.close()
        shutil.rmtree(self.test_dir)
    
    def test_zero_values(self):
        """Test handling of zero values"""
        trade_id = self.db.save_trade("BUY", 110000, 0, 0, 0, 0, "TEST", "Zero test")
        self.assertIsNotNone(trade_id)
    
    def test_negative_profit(self):
        """Test handling of negative profit (loss)"""
        trade_id = self.db.save_trade("SELL", 108000, 9.50, 0.00009, 0.06, -0.50, "DRY RUN", "Loss")
        self.assertIsNotNone(trade_id)
        
        history = self.db.get_trade_history(limit=1)
        self.assertLess(history[0]['profit'], 0)
    
    def test_get_session_when_none_exists(self):
        """Test getting session when none exists"""
        session = self.db.get_active_session()
        self.assertIsNone(session)
    
    def test_get_statistics_when_none_exist(self):
        """Test getting statistics when none exist"""
        stats = self.db.get_latest_statistics()
        self.assertIsNone(stats)
    
    def test_large_values(self):
        """Test handling of large values"""
        large_price = 1000000.0
        trade_id = self.db.save_trade("BUY", large_price, 1000, 0.001, 6.0, 0, "TEST", "Large")
        
        self.assertIsNotNone(trade_id)
        history = self.db.get_trade_history(limit=1)
        self.assertEqual(history[0]['price'], large_price)


if __name__ == '__main__':
    unittest.main(verbosity=2)
