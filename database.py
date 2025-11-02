"""
SQLite Database Manager for BTC Trading Bot
Handles persistence of trades, sessions, and statistics
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List


class TradingDatabase:
    """Manages SQLite database for trading bot persistence"""
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.conn.cursor()
            print(f"✅ Database connected: {self.db_path}")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Trades table - stores all buy/sell trades
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    trade_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    amount_usd REAL NOT NULL,
                    amount_btc REAL NOT NULL,
                    fee REAL NOT NULL,
                    profit REAL DEFAULT 0,
                    mode TEXT NOT NULL,
                    notes TEXT
                )
            """)
            
            # Sessions table - stores open positions
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    last_buy_price REAL DEFAULT 0,
                    position_size REAL DEFAULT 0,
                    btc_amount REAL DEFAULT 0,
                    target_price REAL DEFAULT 0,
                    stop_loss REAL DEFAULT 0,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Statistics table - stores cumulative stats
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    total_profit REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    roi REAL DEFAULT 0
                )
            """)
            
            self.conn.commit()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
    
    def save_trade(self, trade_type: str, price: float, amount_usd: float, 
                   amount_btc: float, fee: float, profit: float = 0, 
                   mode: str = "DRY RUN", notes: str = ""):
        """Save a trade to database"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO trades 
                (timestamp, trade_type, price, amount_usd, amount_btc, fee, profit, mode, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, trade_type, price, amount_usd, amount_btc, fee, profit, mode, notes))
            
            self.conn.commit()
            print(f"✅ Trade saved: {trade_type} @ ${price:,.2f}")
            return self.cursor.lastrowid
        except Exception as e:
            print(f"❌ Error saving trade: {e}")
            return None
    
    def save_session(self, last_buy_price: float, position_size: float, 
                     btc_amount: float, target_price: float, stop_loss: float):
        """Save or update current session"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Deactivate previous sessions
            self.cursor.execute("UPDATE sessions SET is_active = 0")
            
            # Insert new session
            self.cursor.execute("""
                INSERT INTO sessions 
                (timestamp, last_buy_price, position_size, btc_amount, target_price, stop_loss, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (timestamp, last_buy_price, position_size, btc_amount, target_price, stop_loss))
            
            self.conn.commit()
            print(f"✅ Session saved: Buy @ ${last_buy_price:,.2f}")
            return self.cursor.lastrowid
        except Exception as e:
            print(f"❌ Error saving session: {e}")
            return None
    
    def get_active_session(self) -> Optional[Dict]:
        """Get the current active session"""
        try:
            self.cursor.execute("""
                SELECT * FROM sessions 
                WHERE is_active = 1 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'last_buy_price': row['last_buy_price'],
                    'position_size': row['position_size'],
                    'btc_amount': row['btc_amount'],
                    'target_price': row['target_price'],
                    'stop_loss': row['stop_loss']
                }
            return None
        except Exception as e:
            print(f"❌ Error getting active session: {e}")
            return None
    
    def close_session(self):
        """Close the current active session"""
        try:
            self.cursor.execute("UPDATE sessions SET is_active = 0 WHERE is_active = 1")
            self.conn.commit()
            print("✅ Session closed")
        except Exception as e:
            print(f"❌ Error closing session: {e}")
    
    def save_statistics(self, total_trades: int, winning_trades: int, 
                       total_profit: float, win_rate: float, roi: float):
        """Save current statistics"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                INSERT INTO statistics 
                (timestamp, total_trades, winning_trades, total_profit, win_rate, roi)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, total_trades, winning_trades, total_profit, win_rate, roi))
            
            self.conn.commit()
            print(f"✅ Statistics saved: {total_trades} trades, ${total_profit:+.2f} profit")
        except Exception as e:
            print(f"❌ Error saving statistics: {e}")
    
    def get_latest_statistics(self) -> Optional[Dict]:
        """Get the most recent statistics"""
        try:
            self.cursor.execute("""
                SELECT * FROM statistics 
                ORDER BY id DESC 
                LIMIT 1
            """)
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'total_trades': row['total_trades'],
                    'winning_trades': row['winning_trades'],
                    'total_profit': row['total_profit'],
                    'win_rate': row['win_rate'],
                    'roi': row['roi']
                }
            return None
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return None
    
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get recent trade history"""
        try:
            self.cursor.execute("""
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ Error getting trade history: {e}")
            return []
    
    def get_profit_summary(self) -> Dict:
        """Get profit summary statistics"""
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(profit) as total_profit,
                    AVG(profit) as avg_profit,
                    MAX(profit) as max_profit,
                    MIN(profit) as min_profit
                FROM trades 
                WHERE trade_type = 'SELL'
            """)
            
            row = self.cursor.fetchone()
            if row and row['total_trades'] > 0:
                return {
                    'total_trades': row['total_trades'],
                    'winning_trades': row['winning_trades'] or 0,
                    'total_profit': row['total_profit'] or 0,
                    'avg_profit': row['avg_profit'] or 0,
                    'max_profit': row['max_profit'] or 0,
                    'min_profit': row['min_profit'] or 0,
                    'win_rate': (row['winning_trades'] or 0) / row['total_trades'] * 100
                }
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'total_profit': 0,
                'avg_profit': 0,
                'max_profit': 0,
                'min_profit': 0,
                'win_rate': 0
            }
        except Exception as e:
            print(f"❌ Error getting profit summary: {e}")
            return {}
    
    def export_to_csv(self, filename: str = "trade_history.csv"):
        """Export trade history to CSV"""
        try:
            import csv
            
            trades = self.get_trade_history(limit=1000)
            
            with open(filename, 'w', newline='') as csvfile:
                if trades:
                    fieldnames = trades[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(trades)
            
            print(f"✅ Exported to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exporting: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")


# Test the database
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Testing Trading Database")
    print("=" * 70)
    
    db = TradingDatabase("test_trading.db")
    
    # Test saving a buy trade
    print("\n📊 Test 1: Save BUY trade")
    db.save_trade("BUY", 110000, 10, 0.00009, 0.06, 0, "DRY RUN", "Test buy")
    
    # Test saving a session
    print("\n📊 Test 2: Save session")
    db.save_session(110000, 10, 0.00009, 114070, 108900)
    
    # Test getting active session
    print("\n📊 Test 3: Get active session")
    session = db.get_active_session()
    if session:
        print(f"   Active session: Buy @ ${session['last_buy_price']:,.2f}")
    
    # Test saving a sell trade
    print("\n📊 Test 4: Save SELL trade")
    db.save_trade("SELL", 114100, 10.21, 0.00009, 0.06, 0.21, "DRY RUN", "Test sell")
    
    # Close session
    print("\n📊 Test 5: Close session")
    db.close_session()
    
    # Test statistics
    print("\n📊 Test 6: Save statistics")
    db.save_statistics(1, 1, 0.21, 100.0, 0.02)
    
    # Get profit summary
    print("\n📊 Test 7: Get profit summary")
    summary = db.get_profit_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Total profit: ${summary['total_profit']:+.2f}")
    print(f"   Win rate: {summary['win_rate']:.1f}%")
    
    # Get trade history
    print("\n📊 Test 8: Get trade history")
    history = db.get_trade_history(limit=5)
    print(f"   Found {len(history)} trades")
    
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ All tests completed")
    print("=" * 70)
