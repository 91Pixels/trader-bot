"""
SQLite Database Manager for BTC Trading Bot
Handles persistence of trades, sessions, and statistics
"""
import sqlite3
import json
import sys
import os
from datetime import datetime
from typing import Optional, Dict, List


class TradingDatabase:
    """Manages SQLite database for trading bot persistence"""
    
    def __init__(self, db_path: str = "trading_bot.db"):
        # When running as PyInstaller executable, save DB in same folder as exe
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
            self.db_path = os.path.join(application_path, db_path)
            print(f"📁 Running as executable, DB path: {self.db_path}")
        else:
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
    
    def export_to_html(self, filename: str = "trade_report.html"):
        """Export comprehensive trading report to HTML"""
        try:
            trades = self.get_trade_history(limit=1000)
            summary = self.get_profit_summary()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Build HTML content
            html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC Trading Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        .stat-card .label {{
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-card .value {{
            color: #1e3c72;
            font-size: 2em;
            font-weight: bold;
        }}
        .stat-card.profit {{
            border-left: 4px solid #28a745;
        }}
        .stat-card.profit .value {{
            color: #28a745;
        }}
        .stat-card.loss {{
            border-left: 4px solid #dc3545;
        }}
        .stat-card.loss .value {{
            color: #dc3545;
        }}
        .trades-section {{
            padding: 30px;
        }}
        .trades-section h2 {{
            color: #1e3c72;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
        }}
        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        tbody tr {{
            transition: background 0.3s;
        }}
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        .trade-type {{
            font-weight: bold;
            padding: 5px 12px;
            border-radius: 5px;
            display: inline-block;
            font-size: 0.9em;
        }}
        .trade-type.buy {{
            background: #d4edda;
            color: #155724;
        }}
        .trade-type.sell {{
            background: #f8d7da;
            color: #721c24;
        }}
        .profit-positive {{
            color: #28a745;
            font-weight: bold;
        }}
        .profit-negative {{
            color: #dc3545;
            font-weight: bold;
        }}
        .mode-badge {{
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .mode-live {{
            background: #ff6b6b;
            color: white;
        }}
        .mode-dry {{
            background: #4ecdc4;
            color: white;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .stat-card:hover {{
                transform: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 BTC Trading Bot Report</h1>
            <p>Generated: {timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="label">Total Trades</div>
                <div class="value">{summary.get('total_trades', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="label">Winning Trades</div>
                <div class="value">{summary.get('winning_trades', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="label">Win Rate</div>
                <div class="value">{summary.get('win_rate', 0):.1f}%</div>
            </div>
            <div class="stat-card {'profit' if summary.get('total_profit', 0) >= 0 else 'loss'}">
                <div class="label">Total Profit/Loss</div>
                <div class="value">${summary.get('total_profit', 0):+.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Profit</div>
                <div class="value">${summary.get('avg_profit', 0):+.2f}</div>
            </div>
            <div class="stat-card profit">
                <div class="label">Best Trade</div>
                <div class="value">${summary.get('max_profit', 0):+.2f}</div>
            </div>
        </div>
        
        <div class="trades-section">
            <h2>📊 Trade History</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date/Time</th>
                        <th>Type</th>
                        <th>Price</th>
                        <th>Amount USD</th>
                        <th>Amount BTC</th>
                        <th>Fee</th>
                        <th>Profit/Loss</th>
                        <th>Mode</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            # Add trade rows
            for trade in trades:
                trade_type = trade['trade_type']
                trade_class = trade_type.lower()
                profit = trade['profit']
                profit_class = 'profit-positive' if profit >= 0 else 'profit-negative'
                mode_class = 'mode-live' if trade['mode'] == 'LIVE' else 'mode-dry'
                
                html_content += f"""
                    <tr>
                        <td>{trade['timestamp']}</td>
                        <td><span class="trade-type {trade_class}">{trade_type}</span></td>
                        <td>${trade['price']:,.2f}</td>
                        <td>${trade['amount_usd']:,.2f}</td>
                        <td>{trade['amount_btc']:.8f}</td>
                        <td>${trade['fee']:.2f}</td>
                        <td class="{profit_class}">${profit:+.2f}</td>
                        <td><span class="mode-badge {mode_class}">{trade['mode']}</span></td>
                        <td>{trade['notes'] or '-'}</td>
                    </tr>
"""
            
            html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>🔒 BTC Trading Bot - Confidential Trading Report</p>
            <p>Keep this report secure and private</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML report exported to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting HTML: {e}")
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
