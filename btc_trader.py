import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time
from datetime import datetime
import os
from coinbase_complete_api import CoinbaseCompleteAPI
from config import Config
from websocket_price_feed import CoinbaseWebSocketFeed
from database import TradingDatabase

class BTCTrader:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("BTC Trading Bot - Coinbase")
        self.root.geometry("650x900")
        
        # Dark Theme Colors
        self.colors = {
            'bg': '#1a1a1a',           # Casi negro
            'bg_secondary': '#51535C',  # Gris (actualizado)
            'text': '#ffffff',          # Blanco
            'button_bg': '#ffc107',     # Amarillo
            'button_fg': '#000000',     # Negro
            'success': '#4caf50',       # Verde
            'danger': '#f44336',        # Rojo
            'warning': '#ff9800',       # Naranja
            'info': '#2196f3',          # Azul
            'border': '#51535C'         # Gris (actualizado)
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Font Configuration (Futura or fallback)
        try:
            self.font_family = 'Futura'
            # Test if font exists
            import tkinter.font as tkfont
            available_fonts = tkfont.families()
            if 'Futura' not in available_fonts:
                # Fallback to similar modern fonts
                for fallback in ['Segoe UI', 'Arial', 'Helvetica']:
                    if fallback in available_fonts:
                        self.font_family = fallback
                        break
        except:
            self.font_family = 'Arial'
        
        # Apply ttk styles
        self.setup_styles()
        
        # Initialize Coinbase API
        self.api = CoinbaseCompleteAPI()
        self.using_real_balance = False
        
        # Trading variables
        self.balance_usd = 1000.0  # Default mock balance
        self.balance_btc = 0.0     # Default mock balance
        self.last_buy_price = 0.0
        self.current_price = 0.0
        self.is_running = False
        self.manual_entry_price = 0.0  # For existing BTC positions
        
        # Try to load real balance
        if Config.is_live_mode() and self.api.is_jwt_format:
            self.load_real_balance()
        
        # Strategy parameters - ALWAYS START WITH THESE VALUES
        self.profit_rate = 0.025   # ALWAYS 2.5% net profit target
        self.stop_loss = 1.0      # 1.0% stop loss
        self.position_size = 5.0  # ALWAYS $5 per trade by default
        self.min_position_size = 5.0  # Minimum $5 per trade
        self.buy_fee_rate = 0.006 # 0.6% buy fee
        self.sell_fee_rate = 0.006 # 0.6% sell fee
        self.rebuy_drop = 2.0     # 2.0% price drop for rebuy in auto-loop
        
        # Trading mode
        self.auto_mode = False
        self.dry_run = True
        
        # Auto buy settings
        self.auto_buy_enabled = False
        self.auto_buy_price = 0.0
        self.auto_buy_executed = False  # Track if auto-buy was already executed
        
        # Auto sell settings
        self.auto_sell_enabled = False
        self.auto_sell_price = 0.0
        
        # Statistics
        self.trades_count = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        
        # Connection status
        self.price_connection_ok = True
        self.balance_connection_ok = True
        self.last_price_error = None
        
        # Entry price variable (used internally, not displayed)
        self.entry_price_var = None
        
        # WebSocket price feed
        self.websocket_feed = None
        self.use_websocket = True  # Use WebSocket by default
        self.websocket_latency_ms = 0
        self.rest_latency_ms = 0
        self.last_price_update_time = 0
        
        # Price validation settings
        self.max_price_age_seconds = 2.0  # Price older than 2s is stale
        self.max_price_deviation_pct = 0.3  # Max 0.3% price change allowed
        
        # Session tracking
        self.last_load_timestamp = None  # Track when session was last loaded
        
        # Initialize database
        self.db = TradingDatabase("trading_bot.db")
        
        # Restore previous session if exists
        self.restore_session()
        
        # Create GUI elements
        self.create_gui()
        
        # Register cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def restore_session(self):
        """Restore previous session from database"""
        try:
            # Restore statistics
            stats = self.db.get_latest_statistics()
            if stats:
                self.trades_count = stats['total_trades']
                self.winning_trades = stats['winning_trades']
                self.total_profit = stats['total_profit']
                print(f"\n✅ Statistics restored: {self.trades_count} trades, ${self.total_profit:+.2f} profit")
            
            # Restore active session (open position)
            session = self.db.get_active_session()
            if session:
                # Restore entry price if exists
                if session['last_buy_price'] > 0:
                    self.last_buy_price = session['last_buy_price']
                    self.manual_entry_price = session['last_buy_price']
                    print(f"\n✅ Entry price restored from DB: ${self.last_buy_price:,.2f}")
                
                # Restore position if exists
                if session['btc_amount'] > 0:
                    self.position_size = session['position_size']
                    # Note: balance_btc will be loaded from Coinbase
                    print(f"\n🔄 Active position restored:")
                    print(f"   Buy Price: ${self.last_buy_price:,.2f}")
                    print(f"   Position Size: ${self.position_size:.2f}")
                    print(f"   Target: ${session['target_price']:,.2f}")
                    print(f"   Stop Loss: ${session['stop_loss']:,.2f}")
        except Exception as e:
            print(f"⚠️ Could not restore session: {e}")
    
    def on_closing(self):
        """Clean up before closing application"""
        try:
            print("\n🔄 Saving state before closing...")
            
            # Save current statistics
            win_rate = (self.winning_trades / self.trades_count * 100) if self.trades_count > 0 else 0
            roi = (self.total_profit / 1000 * 100) if self.total_profit != 0 else 0
            self.db.save_statistics(
                self.trades_count,
                self.winning_trades,
                self.total_profit,
                win_rate,
                roi
            )
            
            # Close database connection
            self.db.close()
            
            # Stop WebSocket
            if self.websocket_feed:
                self.websocket_feed.disconnect()
            
            print("✅ State saved successfully")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
        finally:
            self.root.destroy()
    
    # Help/Tooltip methods
    def show_help_price(self):
        """Show help for Live BTC Price section"""
        messagebox.showinfo(
            "📊 Ayuda: Live BTC Price",
            "PRECIO EN TIEMPO REAL\n\n"
            "🎯 Qué hace:\n"
            "• Muestra el precio actual de BTC en USD\n"
            "• Se actualiza automáticamente en tiempo real\n"
            "• Usa WebSocket para latencia mínima (<50ms)\n\n"
            "📡 Latencia:\n"
            "• WebSocket ⚡: <50ms (Excelente)\n"
            "• REST API 📱: 300-800ms (Fallback)\n\n"
            "✅ WebSocket Conectado: Precio real-time\n"
            "⚠️ REST API: Fallback si WebSocket falla\n\n"
            "💡 Tip:\n"
            "Latencia baja = Precio más preciso = Menos riesgo de slippage"
        )
    
    def show_help_trading_settings(self):
        """Show help for Trading Settings section"""
        messagebox.showinfo(
            "⚙️ Ayuda: Trading Settings",
            "CONFIGURACIÓN DE TRADING\n\n"
            "🎯 Profit Target (%):\n"
            "• Ganancia objetivo por trade\n"
            "• Recomendado: ≥2.5%\n"
            "• Ejemplo: 2.5% = $0.25 por cada $10\n"
            "• Incluye margen para cubrir fees (1.2%)\n\n"
            "🛡️ Dry Run (Test Mode):\n"
            "• ✅ ACTIVO: Simula trades sin dinero real\n"
            "• ❌ DESACTIVO: Ejecuta trades reales (LIVE)\n"
            "• Siempre prueba en DRY RUN primero\n\n"
            "🛑 Stop Loss (%):\n"
            "• Pérdida máxima aceptable\n"
            "• Default: 1.0% = -$0.10 por cada $10\n"
            "• Protección automática contra caídas\n\n"
            "🔄 Rebuy Drop (%):\n"
            "• % que debe bajar precio para recomprar\n"
            "• Solo en auto-loop mode\n"
            "• Ejemplo: 2% = recompra si baja $2,200"
        )
    
    def show_help_auto_buy(self):
        """Show help for Auto Buy section"""
        messagebox.showinfo(
            "🤖 Ayuda: Auto Buy Configuration",
            "COMPRA AUTOMÁTICA\n\n"
            "🎯 Qué hace:\n"
            "• Compra automáticamente cuando precio alcanza trigger\n"
            "• Se ejecuta UNA VEZ y se desactiva\n"
            "• Útil para comprar en precio objetivo\n\n"
            "⚙️ Configuración:\n"
            "1. ☑ Enable Auto Buy: Activar/Desactivar\n"
            "2. Buy Price: Precio trigger ($)\n"
            "3. 'Set Current -1%': Usa precio actual -1%\n\n"
            "📊 Estados:\n"
            "• ⚫ ACTIVE: Esperando precio trigger\n"
            "• ✅ EXECUTED: Ya se ejecutó (desactivado)\n"
            "• ⚪ DISABLED: No activo\n\n"
            "💡 Ejemplo:\n"
            "Precio actual: $110,000\n"
            "Tu trigger: $108,000\n"
            "→ Cuando baje a $108K, compra automáticamente\n\n"
            "⚠️ Importante:\n"
            "• Solo se ejecuta UNA VEZ\n"
            "• Requiere balance USD disponible (LIVE mode)\n"
            "• En DRY RUN: sin límite de balance"
        )
    
    def show_help_auto_sell(self):
        """Show help for Auto Sell section"""
        messagebox.showinfo(
            "💰 Ayuda: Auto Sell Configuration",
            "VENTA AUTOMÁTICA\n\n"
            "🎯 Qué hace:\n"
            "• Vende automáticamente cuando precio alcanza target\n"
            "• Se ejecuta UNA VEZ y se desactiva\n"
            "• Útil para tomar ganancias automáticamente\n\n"
            "⚙️ Configuración:\n"
            "1. ☑ Enable Auto Sell: Activar/Desactivar\n"
            "2. Sell Price: Precio target ($)\n"
            "3. 'Use Target Price': Usa target calculado\n"
            "4. 'Update': Recalcula con precio actual\n\n"
            "📊 Estados:\n"
            "• ⚫ ACTIVE: Esperando precio target\n"
            "• ✅ EXECUTED: Ya se ejecutó (desactivado)\n"
            "• ⚪ DISABLED: No activo\n\n"
            "💡 Ejemplo:\n"
            "Compraste a: $110,000\n"
            "Target auto: $114,084 (+3.7% para 2.5% neto)\n"
            "→ Cuando suba a $114K, vende automáticamente\n\n"
            "✅ Ventajas:\n"
            "• No necesitas estar monitoreando\n"
            "• Toma ganancias automáticamente\n"
            "• Ejecuta al precio exacto"
        )
    
    def show_help_position(self):
        """Show help for Position Calculator section"""
        messagebox.showinfo(
            "📊 Ayuda: Current Position & Profit Calculator",
            "CALCULADORA DE POSICIÓN\n\n"
            "🎯 Qué hace:\n"
            "• Muestra tu posición actual\n"
            "• Calcula profit/loss en tiempo real\n"
            "• Muestra precios target y stop loss\n\n"
            "📊 Información mostrada:\n"
            "• Entry: Precio de compra\n"
            "• Current: Precio actual\n"
            "• Initial Investment: Monto invertido\n"
            "• Current BTC Value: Valor actual de tu BTC\n"
            "• Current P/L: Ganancia/Pérdida actual\n\n"
            "🎯 TARGET PRICE:\n"
            "• Precio para alcanzar profit objetivo\n"
            "• Incluye fees de compra y venta\n"
            "• Ejemplo: $114,084 (+3.7% bruto, 2.5% neto)\n\n"
            "🛑 STOP LOSS:\n"
            "• Precio para limitar pérdidas\n"
            "• Ejemplo: $108,914 (-1%)\n\n"
            "💡 Cómo leer:\n"
            "• Verde: En ganancia\n"
            "• Rojo: En pérdida\n"
            "• Actual P/L: Ganancia si vendieras AHORA\n\n"
            "✅ Fórmula Target:\n"
            "Target = Entry × (1 + Profit% + Fees%)"
        )
    
    def show_help_balance(self):
        """Show help for Account Balance section"""
        messagebox.showinfo(
            "💰 Ayuda: Account (Real Balance from Coinbase)",
            "BALANCE DE CUENTA\n\n"
            "🎯 Qué hace:\n"
            "• Muestra tu balance REAL de Coinbase\n"
            "• Se actualiza al iniciar el programa\n"
            "• Conecta con Coinbase API\n\n"
            "📊 Información:\n"
            "• USD: Dólares disponibles\n"
            "• BTC: Bitcoin disponible\n"
            "• Cantidad exacta con 8 decimales\n\n"
            "🔄 Refresh Balance:\n"
            "• Actualiza balance desde Coinbase\n"
            "• Útil después de hacer trades externos\n"
            "• Tarda ~2 segundos\n\n"
            "✅ Connected to Coinbase:\n"
            "• Verde: API conectada correctamente\n"
            "• Rojo: Error de conexión\n\n"
            "⚠️ En DRY RUN:\n"
            "• Muestra balance real\n"
            "• Pero trades NO lo modifican\n"
            "• Balance simulado para testing\n\n"
            "💡 En LIVE:\n"
            "• Balance real se usa\n"
            "• Se actualiza después de cada trade\n"
            "• Sincronizado con Coinbase"
        )
    
    def show_help_statistics(self):
        """Show help for Statistics section"""
        messagebox.showinfo(
            "📊 Ayuda: Statistics",
            "ESTADÍSTICAS DE TRADING\n\n"
            "🎯 Qué muestra:\n"
            "• Trades: Número total de operaciones\n"
            "• Win: % de trades ganadores\n"
            "• Profit: Ganancia/Pérdida total\n"
            "• ROI: Return on Investment (%)\n\n"
            "📈 Cálculos:\n"
            "• Win Rate = (Wins / Total) × 100\n"
            "• Total Profit = Suma de todos los P/L\n"
            "• ROI = (Profit / Capital Inicial) × 100\n\n"
            "💡 Ejemplo:\n"
            "Trades: 5\n"
            "Win: 80% (4 de 5 ganadores)\n"
            "Profit: +$1.25\n"
            "ROI: +0.13%\n\n"
            "✅ Buenas métricas:\n"
            "• Win Rate: >60%\n"
            "• ROI: >0% (positivo)\n"
            "• Profit consistente\n\n"
            "📊 Se actualiza:\n"
            "• Después de cada trade completado\n"
            "• En tiempo real\n"
            "• Solo cuenta trades completados (buy+sell)"
        )
        
    def calculate_average_entry_from_coinbase(self):
        """Calculate average entry price from Coinbase order fills"""
        try:
            print("\n🔄 Calculating average entry price from Coinbase...")
            
            fills = self.api.list_fills(product_id='BTC-USD', limit=100)
            
            if not fills.get('fills'):
                print("   ⚠️ No order history found")
                return None
            
            # Calculate weighted average for BUY orders
            total_btc_bought = 0.0
            total_usd_spent = 0.0
            buy_count = 0
            
            for fill in fills.get('fills', []):
                side = fill.get('side')
                size = float(fill.get('size', 0))
                price = float(fill.get('price', 0))
                
                if side == 'BUY':
                    cost = size * price
                    total_btc_bought += size
                    total_usd_spent += cost
                    buy_count += 1
            
            if total_btc_bought > 0:
                average_entry = total_usd_spent / total_btc_bought
                
                print(f"✅ Average Entry calculated from {buy_count} buy orders:")
                print(f"   Total BTC: {total_btc_bought:.8f}")
                print(f"   Total USD: ${total_usd_spent:,.2f}")
                print(f"   📊 AVERAGE ENTRY: ${average_entry:,.2f}")
                
                return average_entry
            else:
                print("   ⚠️ No BUY orders found in history")
                return None
                
        except Exception as e:
            print(f"   ⚠️ Could not calculate average entry: {e}")
            return None
    
    def load_real_balance(self):
        """Load real balance from Coinbase"""
        try:
            print("\n🔄 Loading real balance from Coinbase...")
            accounts = self.api.list_accounts()
            
            # Extract USD and BTC balances
            for account in accounts.get('accounts', []):
                currency = account.get('currency')
                available = float(account.get('available_balance', {}).get('value', 0))
                
                if currency == 'USD':
                    self.balance_usd = available
                elif currency == 'BTC':
                    self.balance_btc = available
            
            self.using_real_balance = True
            
            # Update Position Size to reflect real BTC value
            if self.balance_btc > 0:
                try:
                    # Get current BTC price
                    import requests
                    response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot', timeout=5)
                    if response.status_code == 200:
                        btc_price = float(response.json()['data']['amount'])
                        btc_value_usd = self.balance_btc * btc_price
                        self.position_size = btc_value_usd
                        
                        print(f"✅ Real balance loaded:")
                        print(f"   USD: ${self.balance_usd:.2f}")
                        print(f"   BTC: {self.balance_btc:.8f}")
                        print(f"   BTC Value: ${btc_value_usd:.2f} (at ${btc_price:,.2f})")
                        print(f"   ✅ Position Size updated to: ${btc_value_usd:.2f}")
                        
                        # ⭐ CALCULATE AVERAGE ENTRY FROM COINBASE
                        average_entry = self.calculate_average_entry_from_coinbase()
                        if average_entry:
                            self.last_buy_price = average_entry
                            self.manual_entry_price = average_entry
                            
                            # Calculate correct sell target with FEES + PROFIT
                            print(f"\n📊 Calculating Auto Sell Target:")
                            print(f"   Entry Price: ${average_entry:,.2f}")
                            print(f"   Buy Fee: {self.buy_fee_rate*100}%")
                            print(f"   Sell Fee: {self.sell_fee_rate*100}%")
                            print(f"   Desired Profit: {self.profit_rate*100}%")
                            
                            # Formula: Need to sell at price that gives 2.5% profit AFTER both fees
                            # Target = (Cost × 1.025) / (1 - sell_fee) / btc_amount
                            desired_net = self.position_size * (1 + self.profit_rate)
                            required_gross = desired_net / (1 - self.sell_fee_rate)
                            target_sell_price = required_gross / self.balance_btc
                            
                            print(f"\n   🎯 Calculation:")
                            print(f"      Cost Basis: ${self.position_size:.2f}")
                            print(f"      Desired Net: ${desired_net:.2f} (+{self.profit_rate*100}%)")
                            print(f"      After Sell Fee: ${required_gross:.2f}")
                            print(f"      Per BTC: ${target_sell_price:,.2f}")
                            
                            # Set auto sell target
                            self.autosell_price_var.set(f"{target_sell_price:.2f}")
                            
                            profit_increase_pct = ((target_sell_price - average_entry) / average_entry) * 100
                            
                            print(f"\n   ✅ AUTO SELL TARGET SET:")
                            print(f"      Entry: ${average_entry:,.2f}")
                            print(f"      Target: ${target_sell_price:,.2f} (+{profit_increase_pct:.2f}%)")
                            print(f"      Expected Profit: ${desired_net - self.position_size:.2f}")
                            
                            # ⭐ AUTO-SAVE TO DATABASE - Persist entry price
                            self.db.save_session(
                                last_buy_price=average_entry,
                                position_size=self.position_size,
                                btc_amount=self.balance_btc,
                                target_price=target_sell_price,
                                stop_loss=average_entry * (1 - self.stop_loss / 100)
                            )
                            print(f"      💾 Auto-saved to database: Entry ${average_entry:,.2f}")
                            
                            # Update UI with entry price info
                            if hasattr(self, 'entry_info_var'):
                                self.entry_info_var.set(f"📊 Entry from Coinbase: ${average_entry:,.2f} | Target: ${target_sell_price:,.2f} (+{profit_increase_pct:.1f}%)")
                        
                    else:
                        print(f"✅ Real balance loaded:")
                        print(f"   USD: ${self.balance_usd:.2f}")
                        print(f"   BTC: {self.balance_btc:.8f}")
                except:
                    print(f"✅ Real balance loaded:")
                    print(f"   USD: ${self.balance_usd:.2f}")
                    print(f"   BTC: {self.balance_btc:.8f}")
            else:
                print(f"✅ Real balance loaded:")
                print(f"   USD: ${self.balance_usd:.2f}")
                print(f"   BTC: {self.balance_btc:.8f}")
            
        except Exception as e:
            print(f"⚠️  Could not load real balance: {e}")
            print(f"   Using mock balance: USD: ${self.balance_usd:.2f}, BTC: {self.balance_btc:.8f}")
            self.using_real_balance = False
    
    def refresh_balance(self):
        """Refresh balance from Coinbase (manual or periodic)"""
        if Config.is_live_mode() and self.api.is_jwt_format:
            try:
                self.load_real_balance()
                self.balance_connection_ok = True
                
                if hasattr(self, 'balance_var'):
                    self.balance_var.set(
                        f"USD: ${self.balance_usd:.2f}\nBTC: {self.balance_btc:.8f}"
                    )
                    
                    # Update status indicator
                    if hasattr(self, 'balance_status_var'):
                        status = "✅ Connected to Coinbase - Balance Updated" if self.using_real_balance else "⚠️ Connection Failed"
                        self.balance_status_var.set(status)
                    self.update_statistics()
                    print("✅ Balance refreshed from Coinbase")
            except Exception as e:
                self.balance_connection_ok = False
                print(f"❌ Error refreshing balance: {e}")
                if hasattr(self, 'balance_status_var'):
                    self.balance_status_var.set("❌ Sin Conexión a Coinbase")
        else:
            print("⚠️  Real balance only available in LIVE mode with ECDSA credentials")
            if hasattr(self, 'balance_status_var'):
                self.balance_status_var.set("⚠️ Using Mock Balance (Set TRADING_MODE=LIVE for real balance)")
    
    def auto_save_session(self):
        """Automatically save current session to database"""
        try:
            if self.last_buy_price > 0:
                # Calculate target and stop loss
                if self.balance_btc > 0:
                    cost_basis = self.last_buy_price * self.balance_btc
                    desired_net = cost_basis * (1 + self.profit_rate)
                    required_gross = desired_net / (1 - self.sell_fee_rate)
                    target_price = required_gross / self.balance_btc
                else:
                    target_price = self.last_buy_price * (1 + self.profit_rate + self.buy_fee_rate + self.sell_fee_rate)
                
                stop_loss = self.last_buy_price * (1 - self.stop_loss / 100)
                
                # Save to database
                self.db.save_session(
                    last_buy_price=self.last_buy_price,
                    position_size=self.position_size,
                    btc_amount=self.balance_btc,
                    target_price=target_price,
                    stop_loss=stop_loss
                )
                print(f"💾 Auto-saved: Entry ${self.last_buy_price:,.2f}")
        except Exception as e:
            print(f"⚠️ Auto-save error: {e}")
    
    def load_last_session(self):
        """Load last saved session from database with full traceability"""
        try:
            from datetime import datetime
            
            print("\n" + "="*70)
            print("📂 LOADING LAST SAVED SESSION FROM DATABASE")
            print("="*70)
            
            # Get session from database
            session = self.db.get_active_session()
            
            if not session:
                print("❌ No saved session found in database")
                self.session_info_var.set("❌ No session found")
                import tkinter.messagebox as messagebox
                messagebox.showwarning(
                    "No Session Found",
                    "No previous session data found in database.\n\n"
                    "Please sync entry price from Coinbase first."
                )
                return
            
            # Extract data
            entry_price = session.get('last_buy_price', 0)
            position_size = session.get('position_size', 0)
            btc_amount = session.get('btc_amount', 0)
            target_price = session.get('target_price', 0)
            stop_loss = session.get('stop_loss', 0)
            saved_timestamp = session.get('timestamp', 'Unknown')
            
            # Validate data
            if entry_price <= 0:
                print("❌ Invalid entry price in saved session")
                self.session_info_var.set("❌ Invalid session data")
                return
            
            # Update last load timestamp
            self.last_load_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n📊 SESSION DATA RETRIEVED:")
            print(f"   Saved: {saved_timestamp}")
            print(f"   Loaded: {self.last_load_timestamp}")
            print(f"   Entry Price: ${entry_price:,.2f}")
            print(f"   Position Size: ${position_size:.2f}")
            print(f"   BTC Amount: {btc_amount:.8f}")
            print(f"   Target Price: ${target_price:,.2f}")
            print(f"   Stop Loss: ${stop_loss:,.2f}")
            
            # Load data into bot
            self.last_buy_price = entry_price
            self.manual_entry_price = entry_price
            self.position_size = position_size
            
            # Update UI fields
            if hasattr(self, 'coinbase_avg_entry_var'):
                self.coinbase_avg_entry_var.set(f"{entry_price:.2f}")
            
            if hasattr(self, 'autosell_price_var'):
                self.autosell_price_var.set(f"{target_price:.2f}")
            
            # Update entry info label
            profit_increase_pct = ((target_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
            if hasattr(self, 'entry_info_var'):
                self.entry_info_var.set(f"📊 Entry from DB: ${entry_price:,.2f} | Target: ${target_price:,.2f} (+{profit_increase_pct:.1f}%)")
            
            # Update session info with LAST LOAD timestamp
            self.session_info_var.set(f"🕐 Last Load: {self.last_load_timestamp} | Entry: ${entry_price:,.2f}")
            
            # Update calculations
            self.check_position()
            
            # Force GUI update
            if hasattr(self, 'root'):
                self.root.update_idletasks()
            
            print("\n" + "="*70)
            print("✅ SESSION LOADED SUCCESSFULLY")
            print("="*70)
            print(f"🎯 Entry Price: ${entry_price:,.2f}")
            print(f"🎯 Target Price: ${target_price:,.2f} (+{profit_increase_pct:.2f}%)")
            print(f"💾 Saved on: {saved_timestamp}")
            print(f"🕐 Loaded on: {self.last_load_timestamp}")
            print("="*70)
            
            # Show success message
            import tkinter.messagebox as messagebox
            messagebox.showinfo(
                "Session Loaded",
                f"✅ Last session loaded successfully!\n\n"
                f"Entry Price: ${entry_price:,.2f}\n"
                f"Target Price: ${target_price:,.2f}\n"
                f"Saved: {saved_timestamp}\n"
                f"Loaded: {self.last_load_timestamp}\n\n"
                f"All data restored from database."
            )
            
        except Exception as e:
            print(f"\n❌ Error loading session: {e}")
            import traceback
            traceback.print_exc()
            self.session_info_var.set("❌ Error loading session")
    
    def save_entry_price(self):
        """Save entry price to database"""
        try:
            entry_price_str = self.coinbase_avg_entry_var.get().strip()
            
            if not entry_price_str or entry_price_str == "0":
                self.entry_save_status_var.set("❌ ERROR: Ingresa un precio válido")
                self.entry_save_status.configure(foreground='red')
                return
            
            entry_price = float(entry_price_str)
            if entry_price <= 0:
                self.entry_save_status_var.set("❌ ERROR: El precio debe ser positivo")
                self.entry_save_status.configure(foreground='red')
                return
            
            # Save to database
            self.db.save_session(
                last_buy_price=entry_price,
                position_size=self.position_size,
                btc_amount=self.balance_btc,
                target_price=entry_price * (1 + self.profit_rate + self.buy_fee_rate + self.sell_fee_rate),
                stop_loss=entry_price * (1 - self.stop_loss / 100)
            )
            
            # Update UI
            self.last_buy_price = entry_price
            self.entry_save_status_var.set(f"✅ Entry guardado: ${entry_price:,.2f}")
            self.entry_save_status.configure(foreground='green')
            
            # Clear message after 5 seconds
            self.root.after(5000, lambda: self.entry_save_status_var.set(""))
            
            print(f"\n✅ Entry Price guardado en DB: ${entry_price:,.2f}")
            
        except ValueError as e:
            self.entry_save_status_var.set("❌ ERROR: Ingresa un número válido")
            self.entry_save_status.configure(foreground='red')
            print(f"\n❌ Error guardando entry price: {e}")
    
    def set_coinbase_avg_entry(self):
        """Set Coinbase average entry and auto-calculate sell target with fees + profit"""
        try:
            entry_price_str = self.coinbase_avg_entry_var.get().strip()
            
            if not entry_price_str or entry_price_str == "0":
                print("\n❌ Please enter the Avg Entry value from Coinbase")
                return
            
            # Remove commas, dollar signs, and any other formatting
            entry_price_str = entry_price_str.replace(',', '').replace('$', '').replace(' ', '')
            entry_price = float(entry_price_str)
            
            if entry_price <= 0:
                print("\n❌ Entry price must be positive")
                return
            
            if self.balance_btc <= 0:
                print("\n❌ No BTC balance found. Cannot calculate target.")
                return
            
            # Set as last_buy_price so calculations use it
            self.last_buy_price = entry_price
            self.manual_entry_price = entry_price
            
            # Calculate cost basis
            cost_basis = entry_price * self.balance_btc
            self.position_size = cost_basis
            
            print("\n" + "="*70)
            print("🔗 COINBASE AVG ENTRY SYNCHRONIZED")
            print("="*70)
            print(f"Entry Price:          ${entry_price:,.2f}")
            print(f"BTC Amount:           {self.balance_btc:.8f}")
            print(f"Cost Basis:           ${cost_basis:.2f}")
            print()
            
            # Calculate correct sell target with FEES + PROFIT
            print("📊 Calculating Auto Sell Target:")
            print(f"   Buy Fee:           {self.buy_fee_rate*100}%")
            print(f"   Sell Fee:          {self.sell_fee_rate*100}%")
            print(f"   Desired Profit:    {self.profit_rate*100}%")
            print()
            
            # Formula: (Cost × 1.025) / (1 - sell_fee) / btc_amount
            desired_net = cost_basis * (1 + self.profit_rate)
            required_gross = desired_net / (1 - self.sell_fee_rate)
            target_sell_price = required_gross / self.balance_btc
            
            print(f"   🎯 Calculation:")
            print(f"      Cost Basis:     ${cost_basis:.2f}")
            print(f"      Desired Net:    ${desired_net:.2f} (+{self.profit_rate*100}%)")
            print(f"      Before Fee:     ${required_gross:.2f}")
            print(f"      Target Price:   ${target_sell_price:,.2f}")
            print()
            
            profit_increase_pct = ((target_sell_price - entry_price) / entry_price) * 100
            expected_profit = desired_net - cost_basis
            
            print("="*70)
            print("✅ AUTO SELL TARGET CALCULATED:")
            print("="*70)
            print(f"Entry:                ${entry_price:,.2f}")
            print(f"Target:               ${target_sell_price:,.2f} (+{profit_increase_pct:.2f}%)")
            print(f"Expected Profit:      ${expected_profit:.2f} ({self.profit_rate*100}%)")
            print("="*70)
            
            # Set auto sell target in UI
            self.autosell_price_var.set(f"{target_sell_price:.2f}")
            
            # Update entry info label
            if hasattr(self, 'entry_info_var'):
                self.entry_info_var.set(f"📊 Entry from Coinbase: ${entry_price:,.2f} | Target: ${target_sell_price:,.2f} (+{profit_increase_pct:.1f}%)")
            
            # ⭐ AUTO-SAVE TO DATABASE - Persist entry price
            self.db.save_session(
                last_buy_price=entry_price,
                position_size=cost_basis,
                btc_amount=self.balance_btc,
                target_price=target_sell_price,
                stop_loss=entry_price * (1 - self.stop_loss / 100)
            )
            print(f"\n💾 Auto-saved to database: Entry ${entry_price:,.2f}")
            
            # Update calculations - THIS WILL UPDATE THE GUI
            self.check_position()
            
            # Force GUI update
            if hasattr(self, 'root'):
                self.root.update_idletasks()
            
        except ValueError as e:
            print(f"\n❌ Invalid entry price format: {e}")
            print(f"   Please enter a number (e.g., 112413.63)")
        except Exception as e:
            print(f"\n❌ Error setting Coinbase avg entry: {e}")
            import traceback
            traceback.print_exc()
    
    def set_manual_entry_price(self):
        """Set manual average entry price for existing BTC position"""
        try:
            entry_price_str = self.avg_entry_var.get().strip()
            
            if not entry_price_str or entry_price_str == "0":
                print("\n❌ Please enter a valid entry price")
                return
            
            # Remove commas and any other formatting
            entry_price_str = entry_price_str.replace(',', '').replace('$', '')
            entry_price = float(entry_price_str)
            
            if entry_price <= 0:
                print("\n❌ Entry price must be positive")
                return
            
            # Set as last_buy_price so calculations use it
            self.last_buy_price = entry_price
            self.manual_entry_price = entry_price
            
            print("\n" + "="*70)
            print("✅ AVERAGE ENTRY PRICE SET")
            print("="*70)
            print(f"Entry Price:  ${entry_price:,.2f}")
            print(f"BTC Amount:   {self.balance_btc:.8f}")
            print(f"Cost Basis:   ${entry_price * self.balance_btc:,.2f}")
            print("="*70)
            
            # Update calculations - THIS WILL UPDATE THE GUI
            self.check_position()
            
            # Update balance status to show entry price was set
            if hasattr(self, 'balance_status_var'):
                cost = entry_price * self.balance_btc
                self.balance_status_var.set(f"✅ Entry: ${entry_price:,.2f} | Cost: ${cost:,.2f}")
            
            # Force GUI update
            if hasattr(self, 'root'):
                self.root.update_idletasks()
            
        except ValueError as e:
            print(f"\n❌ Invalid entry price format: {e}")
            print(f"   Please enter a number (e.g., 70000)")
        except Exception as e:
            print(f"\n❌ Error setting entry price: {e}")
        
    def setup_styles(self):
        """Configure dark theme styles for all UI elements"""
        style = ttk.Style()
        
        # Use 'clam' theme as base (most customizable)
        style.theme_use('clam')
        
        # Configure general ttk styles
        style.configure('.', 
            background=self.colors['bg'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['bg_secondary'],
            font=(self.font_family, 10)
        )
        
        # Frame styles
        style.configure('TFrame',
            background=self.colors['bg']
        )
        
        style.configure('TLabelframe',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            bordercolor=self.colors['border'],
            font=(self.font_family, 10, 'bold')
        )
        
        style.configure('TLabelframe.Label',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=(self.font_family, 10, 'bold')
        )
        
        # Label styles
        style.configure('TLabel',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=(self.font_family, 10)
        )
        
        # Button styles - YELLOW with BLACK text
        style.configure('TButton',
            background=self.colors['button_bg'],
            foreground=self.colors['button_fg'],
            borderwidth=0,
            focuscolor='none',
            font=(self.font_family, 10, 'bold'),
            padding=8
        )
        
        style.map('TButton',
            background=[('active', '#ffca28'), ('pressed', '#ffa000')],
            foreground=[('active', self.colors['button_fg']), ('pressed', self.colors['button_fg'])]
        )
        
        # Accent button (more prominent)
        style.configure('Accent.TButton',
            background=self.colors['button_bg'],
            foreground=self.colors['button_fg'],
            font=(self.font_family, 11, 'bold'),
            padding=10
        )
        
        style.map('Accent.TButton',
            background=[('active', '#ffca28'), ('pressed', '#ffa000')]
        )
        
        # Entry fields
        style.configure('TEntry',
            fieldbackground=self.colors['bg_secondary'],
            foreground=self.colors['text'],
            bordercolor=self.colors['border'],
            insertcolor=self.colors['text'],
            font=(self.font_family, 10)
        )
        
        # Checkbutton styles
        style.configure('TCheckbutton',
            background=self.colors['bg'],
            foreground=self.colors['text'],
            font=(self.font_family, 10)
        )
        
        style.map('TCheckbutton',
            background=[('active', self.colors['bg'])],
            foreground=[('active', self.colors['text'])]
        )
        
        # Separator
        style.configure('TSeparator',
            background=self.colors['border']
        )
        
        # Notebook (tabs)
        style.configure('TNotebook',
            background=self.colors['bg'],
            borderwidth=0
        )
        
        style.configure('TNotebook.Tab',
            background=self.colors['bg_secondary'],  # Gris #51535C
            foreground=self.colors['text'],
            padding=[20, 10],
            font=(self.font_family, 10, 'bold')
        )
        
        style.map('TNotebook.Tab',
            background=[('selected', self.colors['button_bg'])],
            foreground=[('selected', self.colors['button_fg'])],
            expand=[('selected', [1, 1, 1, 0])]
        )
    
    def create_gui(self):
        # Initialize entry_price_var (used internally, not displayed)
        self.entry_price_var = tk.StringVar(value="0")
        
        # Create Header Frame with Logo
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Load and display logo (centered, maintain aspect ratio)
        try:
            from PIL import Image, ImageTk
            import os
            import sys
            
            # Get correct path for assets when running as executable
            if getattr(sys, 'frozen', False):
                # Running as executable
                application_path = os.path.dirname(sys.executable)
                assets_dir = os.path.join(application_path, "assets")
                # If not found there, try _MEIPASS (temp folder where PyInstaller extracts)
                if not os.path.exists(assets_dir):
                    assets_dir = os.path.join(sys._MEIPASS, "assets")
            else:
                # Running as script
                assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            
            logo_path = os.path.join(assets_dir, "Cripto-Bot.png")
            
            if os.path.exists(logo_path):
                # Load image at original size
                logo_img = Image.open(logo_path)
                
                # Get original dimensions
                original_width, original_height = logo_img.size
                
                # Calculate size to fit within max dimensions while maintaining aspect ratio
                max_size = 200
                if original_width > max_size or original_height > max_size:
                    # Calculate scaling factor
                    scale = min(max_size / original_width, max_size / original_height)
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                    logo_img = logo_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    print(f"✅ Logo loaded: {new_width}x{new_height}px (scaled from {original_width}x{original_height}px)")
                else:
                    new_width, new_height = original_width, original_height
                    print(f"✅ Logo loaded: {new_width}x{new_height}px (original size)")
                
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                
                # Set window icon using the same logo
                try:
                    self.root.iconphoto(True, self.logo_photo)
                    print(f"✅ Window icon set")
                except Exception as icon_error:
                    print(f"⚠️ Could not set window icon: {icon_error}")
                
                # Create label with logo (centered)
                logo_label = tk.Label(
                    header_frame, 
                    image=self.logo_photo,
                    bg=self.colors['bg']
                )
                logo_label.pack()
            else:
                print(f"⚠️ Logo not found at: {logo_path}")
        except Exception as e:
            print(f"⚠️ Could not load logo: {e}")
        
        # Version and Creator Info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(pady=(5, 10))
        
        # Version
        version_label = tk.Label(
            info_frame,
            text="Version 1.0 Beta",
            font=(self.font_family, 9, 'bold'),
            fg='#E8E8E8',
            bg=self.colors['bg']
        )
        version_label.pack()
        
        # Creator
        creator_label = tk.Label(
            info_frame,
            text="Creator: Michael Camacho",
            font=(self.font_family, 8),
            fg='#E8E8E8',
            bg=self.colors['bg']
        )
        creator_label.pack()
        
        # License
        license_label = tk.Label(
            info_frame,
            text="License: 91pixelsusa@gmail.com",
            font=(self.font_family, 8),
            fg='#E8E8E8',
            bg=self.colors['bg']
        )
        license_label.pack()
        
        # Create Notebook (Tab Container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs with scrollable frames
        self.trading_tab_container = ttk.Frame(self.notebook)
        self.config_tab_container = ttk.Frame(self.notebook)
        self.testing_tab_container = ttk.Frame(self.notebook)
        
        self.notebook.add(self.trading_tab_container, text='📊 Trading')
        self.notebook.add(self.config_tab_container, text='⚙️ Configuration')
        self.notebook.add(self.testing_tab_container, text='🧪 Buying Testing')
        
        # Create scrollable frames for each tab
        self.trading_tab = self.create_scrollable_frame(self.trading_tab_container)
        self.config_tab = self.create_scrollable_frame(self.config_tab_container)
        self.testing_tab = self.create_scrollable_frame(self.testing_tab_container)
        
        # Create Trading Tab Content
        self.create_trading_tab()
        
        # Create Configuration Tab Content
        self.create_configuration_tab()
        
        # Create Buying Testing Tab Content
        self.create_buying_testing_tab()
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame inside a parent container"""
        # Create canvas
        canvas = tk.Canvas(parent, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        scrollable_frame = ttk.Frame(canvas)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        # Update scroll region when frame size changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        scrollable_frame.bind('<Configure>', on_frame_configure)
        
        # Update canvas window width when canvas size changes
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        return scrollable_frame
        
    def create_trading_tab(self):
        """Create the main trading interface"""
        # Price Display with help button
        price_container = ttk.Frame(self.trading_tab)
        price_container.pack(fill=tk.X, padx=10, pady=5)
        
        price_frame = ttk.LabelFrame(price_container, text="Live BTC Price", padding="10")
        price_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help button inside frame - top right corner
        help_btn_price = ttk.Button(price_frame, text="?", width=2, command=self.show_help_price)
        help_btn_price.pack(side=tk.TOP, anchor=tk.NE, pady=(0, 5))
        
        self.price_var = tk.StringVar(value="$0.00")
        ttk.Label(
            price_frame,
            textvariable=self.price_var,
            font=('Helvetica', 24, 'bold')
        ).pack()
        
        # Last update time
        self.last_update_var = tk.StringVar(value="Last update: Never")
        ttk.Label(
            price_frame,
            textvariable=self.last_update_var,
            font=('Helvetica', 8),
            foreground='gray'
        ).pack()
        
        # Connection status indicator for price
        self.price_status_var = tk.StringVar(value="⚪ Esperando conexión...")
        ttk.Label(
            price_frame,
            textvariable=self.price_status_var,
            font=('Helvetica', 8, 'bold'),
            foreground='#E8E8E8'
        ).pack()
        
        # Latency indicator
        self.latency_var = tk.StringVar(value="📡 Latency: -- ms | Source: --")
        ttk.Label(
            price_frame,
            textvariable=self.latency_var,
            font=('Helvetica', 8),
            foreground='green'
        ).pack()
        
        # Trading Settings with help button
        settings_container = ttk.Frame(self.trading_tab)
        settings_container.pack(fill=tk.X, padx=10, pady=5)
        
        self.settings_frame = ttk.LabelFrame(settings_container, text="Trading Settings", padding="10")
        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help button inside frame - top right corner
        help_btn_settings = ttk.Button(self.settings_frame, text="?", width=2, command=self.show_help_trading_settings)
        help_btn_settings.pack(side=tk.TOP, anchor=tk.NE, pady=(0, 5))
        
        # Profit target setting - ALWAYS 2.5%
        profit_frame = ttk.Frame(self.settings_frame)
        profit_frame.pack(fill=tk.X, pady=2)
        ttk.Label(profit_frame, text="Profit Target (%):").pack(side=tk.LEFT)
        self.profit_var = tk.StringVar(value="2.5")
        ttk.Entry(profit_frame, textvariable=self.profit_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Trading mode
        mode_frame = ttk.Frame(self.settings_frame)
        mode_frame.pack(fill=tk.X, pady=2)
        self.auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(mode_frame, text="Auto Mode", variable=self.auto_var).pack(side=tk.LEFT)
        self.dryrun_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(mode_frame, text="Dry Run (Test Mode)", variable=self.dryrun_var).pack(side=tk.LEFT, padx=10)
        
        # Stop loss setting
        stop_frame = ttk.Frame(self.settings_frame)
        stop_frame.pack(fill=tk.X, pady=2)
        ttk.Label(stop_frame, text="Stop Loss (%):").pack(side=tk.LEFT)
        self.stop_var = tk.StringVar(value="1.0")
        ttk.Entry(stop_frame, textvariable=self.stop_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Rebuy drop setting (for auto-loop)
        rebuy_frame = ttk.Frame(self.settings_frame)
        rebuy_frame.pack(fill=tk.X, pady=2)
        ttk.Label(rebuy_frame, text="Rebuy Drop (%):").pack(side=tk.LEFT)
        self.rebuy_drop_var = tk.StringVar(value="2.0")
        ttk.Entry(rebuy_frame, textvariable=self.rebuy_drop_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(rebuy_frame, text="(for auto-loop)", font=('Helvetica', 8), foreground='gray').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.settings_frame,
            text="Apply Settings",
            command=self.apply_settings
        ).pack(pady=5)
        
        # Auto Buy Section with help button
        autobuy_container = ttk.Frame(self.trading_tab)
        autobuy_container.pack(fill=tk.X, padx=10, pady=5)
        
        autobuy_frame = ttk.LabelFrame(autobuy_container, text="🤖 Auto Buy Configuration", padding="10")
        autobuy_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help button inside frame - top right corner
        help_btn_autobuy = ttk.Button(autobuy_frame, text="?", width=2, command=self.show_help_auto_buy)
        help_btn_autobuy.pack(side=tk.TOP, anchor=tk.NE, pady=(0, 5))
        
        # Enable Auto Buy checkbox
        enable_frame = ttk.Frame(autobuy_frame)
        enable_frame.pack(fill=tk.X, pady=2)
        self.autobuy_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            enable_frame, 
            text="Enable Auto Buy", 
            variable=self.autobuy_enabled_var,
            command=self.toggle_auto_buy
        ).pack(side=tk.LEFT)
        
        # Auto buy trigger price
        trigger_frame = ttk.Frame(autobuy_frame)
        trigger_frame.pack(fill=tk.X, pady=2)
        ttk.Label(trigger_frame, text="Buy when price drops to ($):").pack(side=tk.LEFT)
        self.autobuy_price_var = tk.StringVar(value="0")
        self.autobuy_price_entry = ttk.Entry(trigger_frame, textvariable=self.autobuy_price_var, width=12)
        self.autobuy_price_entry.pack(side=tk.LEFT, padx=5)
        
        # Set current price button
        ttk.Button(
            trigger_frame,
            text="Set Current -1%",
            command=self.set_autobuy_current_minus
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.autobuy_status_var = tk.StringVar(value="⚪ Auto Buy: Disabled")
        ttk.Label(
            autobuy_frame,
            textvariable=self.autobuy_status_var,
            font=('Helvetica', 9, 'bold')
        ).pack(pady=5)
        
        # Auto Sell Section with help button
        autosell_container = ttk.Frame(self.trading_tab)
        autosell_container.pack(fill=tk.X, padx=10, pady=5)
        
        autosell_frame = ttk.LabelFrame(autosell_container, text="🤖 Auto Sell Configuration", padding="10")
        autosell_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help button inside frame - top right corner
        help_btn_autosell = ttk.Button(autosell_frame, text="?", width=2, command=self.show_help_auto_sell)
        help_btn_autosell.pack(side=tk.TOP, anchor=tk.NE, pady=(0, 5))
        
        # Enable Auto Sell checkbox
        sell_enable_frame = ttk.Frame(autosell_frame)
        sell_enable_frame.pack(fill=tk.X, pady=2)
        self.autosell_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            sell_enable_frame, 
            text="Enable Auto Sell", 
            variable=self.autosell_enabled_var,
            command=self.toggle_auto_sell
        ).pack(side=tk.LEFT)
        
        # Auto sell trigger price
        sell_trigger_frame = ttk.Frame(autosell_frame)
        sell_trigger_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sell_trigger_frame, text="Sell when price reaches ($):").pack(side=tk.LEFT)
        self.autosell_price_var = tk.StringVar(value="0")
        self.autosell_price_entry = ttk.Entry(sell_trigger_frame, textvariable=self.autosell_price_var, width=12)
        self.autosell_price_entry.pack(side=tk.LEFT, padx=5)
        
        # Set target price button
        ttk.Button(
            sell_trigger_frame,
            text="Use Target Price",
            command=self.set_autosell_target
        ).pack(side=tk.LEFT, padx=2)
        
        # Update current target button (for auto mode)
        ttk.Button(
            sell_trigger_frame,
            text="🔄 Update",
            command=self.update_autosell_current_target
        ).pack(side=tk.LEFT, padx=2)
        
        # Status label
        self.autosell_status_var = tk.StringVar(value="⚪ Auto Sell: Disabled")
        ttk.Label(
            autosell_frame,
            textvariable=self.autosell_status_var,
            font=('Helvetica', 9, 'bold')
        ).pack(pady=5)
        
        # Entry price info label (shows average entry from Coinbase)
        self.entry_info_var = tk.StringVar(value="")
        ttk.Label(
            autosell_frame,
            textvariable=self.entry_info_var,
            font=('Helvetica', 8),
            foreground='#E8E8E8'
        ).pack(pady=2)
        
        # Coinbase Avg Entry Sync Section
        coinbase_sync_frame = ttk.Frame(autosell_frame)
        coinbase_sync_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            coinbase_sync_frame,
            text="🔗 Sync Avg Entry from Coinbase:",
            font=('Helvetica', 9, 'bold'),
            foreground='#0083E8'
        ).pack(anchor=tk.W)
        
        entry_sync_frame = ttk.Frame(coinbase_sync_frame)
        entry_sync_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(entry_sync_frame, text="Coinbase Avg Entry ($):").pack(side=tk.LEFT)
        self.coinbase_avg_entry_var = tk.StringVar(value="")
        self.coinbase_avg_entry_entry = ttk.Entry(entry_sync_frame, textvariable=self.coinbase_avg_entry_var, width=15)
        self.coinbase_avg_entry_entry.pack(side=tk.LEFT, padx=5)
        
        # Save status label
        self.entry_save_status_var = tk.StringVar(value="")
        self.entry_save_status = ttk.Label(
            entry_sync_frame,
            textvariable=self.entry_save_status_var,
            font=('Helvetica', 9, 'bold')
        )
        self.entry_save_status.pack(side=tk.LEFT, padx=5)
        
        # Save and Calculate buttons
        ttk.Button(
            entry_sync_frame,
            text=" Save Entry",
            command=self.save_entry_price,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            entry_sync_frame,
            text=" Calculate Target",
            command=self.set_coinbase_avg_entry,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(
            coinbase_sync_frame,
            text="💡 Copy the 'Avg Entry' value from your Coinbase app and paste it here",
            font=('Helvetica', 7),
            foreground='gray'
        ).pack(anchor=tk.W, pady=2)
        
        # Separator
        ttk.Separator(autosell_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Load Last Session Section
        load_session_frame = ttk.Frame(autosell_frame)
        load_session_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            load_session_frame,
            text="💾 Database Session:",
            font=('Helvetica', 9, 'bold'),
            foreground='#2E7D32'
        ).pack(anchor=tk.W)
        
        load_btn_frame = ttk.Frame(load_session_frame)
        load_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            load_btn_frame,
            text="📂 Load Last Saved Session",
            command=self.load_last_session,
            width=25
        ).pack(side=tk.LEFT, padx=2)
        
        # Session info display
        self.session_info_var = tk.StringVar(value="No session loaded")
        ttk.Label(
            load_session_frame,
            textvariable=self.session_info_var,
            font=('Helvetica', 7),
            foreground='gray'
        ).pack(anchor=tk.W, pady=2)
        
        # Position Information with help button
        position_container = ttk.Frame(self.trading_tab)
        position_container.pack(fill=tk.X, padx=10, pady=5)
        
        position_frame = ttk.LabelFrame(position_container, text="Current Position & Profit Calculator (Existing BTC)", padding="10")
        position_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help button inside frame - top right corner
        help_btn_position = ttk.Button(position_frame, text="?", width=2, command=self.show_help_position)
        help_btn_position.pack(side=tk.TOP, anchor=tk.NE, pady=(0, 5))
        
        # Entry Price and Status
        self.entry_var = tk.StringVar(value="No Position")
        ttk.Label(
            position_frame,
            textvariable=self.entry_var,
            font=('Helvetica', 11, 'bold')
        ).pack(pady=(0,5))
        
        # Create a frame for the table
        table_frame = ttk.Frame(position_frame)
        table_frame.pack(fill=tk.X, padx=5)
        
        # Table headers
        headers = ['Description', 'Amount']
        for col, header in enumerate(headers):
            label = ttk.Label(table_frame, text=header, font=('Helvetica', 10, 'bold'))
            label.grid(row=0, column=col, padx=5, pady=2, sticky='w')
        
        # Table rows
        descriptions = [
            'Initial Investment:',  # What you spent on this BTC position
            'Buy Fee (0.6%):',
            'Actual BTC Purchase:',  # Net amount converted to BTC
            '--- Current Position ---',
            'Current BTC Value:',  # Current worth of your BTC
            'Current P/L (if sold now):',
            '--- At Target Price ---',
            'Value at Target:',
            'Sell Fee (0.6%):',
            'Final Profit (at target):'
        ]
        
        self.amount_labels = {}
        for row, desc in enumerate(descriptions, 1):
            ttk.Label(table_frame, text=desc, font=('Helvetica', 9)).grid(row=row, column=0, padx=5, pady=1, sticky='w')
            amount_label = ttk.Label(table_frame, text='$0.00', font=('Helvetica', 9))
            amount_label.grid(row=row, column=1, padx=5, pady=1, sticky='e')
            self.amount_labels[desc] = amount_label
        
        # Separator
        ttk.Separator(position_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Target Price (GREEN - Important!)
        target_frame = ttk.Frame(position_frame)
        target_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(target_frame, text="🎯 TARGET PRICE:", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT)
        self.target_price_var = tk.StringVar(value="$0.00")
        self.target_price_label = ttk.Label(
            target_frame,
            textvariable=self.target_price_var,
            font=('Helvetica', 12, 'bold'),
            foreground='green'
        )
        self.target_price_label.pack(side=tk.LEFT, padx=5)
        
        # Stop Loss Price (RED - Important!)
        stop_frame = ttk.Frame(position_frame)
        stop_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(stop_frame, text="🛑 STOP LOSS:", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT)
        self.stop_price_var = tk.StringVar(value="$0.00")
        self.stop_price_label = ttk.Label(
            stop_frame,
            textvariable=self.stop_price_var,
            font=('Helvetica', 12, 'bold'),
            foreground='red'
        )
        self.stop_price_label.pack(side=tk.LEFT, padx=5)
        
        # Calculation Info
        self.calc_info_var = tk.StringVar(value="")
        ttk.Label(
            position_frame,
            textvariable=self.calc_info_var,
            font=('Helvetica', 8),
            foreground='gray'
        ).pack()
        
        # Account Information with help button
        account_container = ttk.Frame(self.trading_tab)
        account_container.pack(fill=tk.X, padx=10, pady=5)
        
        account_title = "Account (Real Balance from Coinbase)" if self.using_real_balance else "Account (Mock Balance)"
        account_frame = ttk.LabelFrame(account_container, text=account_title, padding="10")
        account_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help button inside frame - top right corner
        help_btn_balance = ttk.Button(account_frame, text="?", width=2, command=self.show_help_balance)
        help_btn_balance.pack(side=tk.TOP, anchor=tk.NE, pady=(0, 5))
        
        self.balance_var = tk.StringVar(
            value=f"USD: ${self.balance_usd:.2f}\nBTC: {self.balance_btc:.8f}"
        )
        ttk.Label(
            account_frame,
            textvariable=self.balance_var,
            font=('Helvetica', 11)
        ).pack()
        
        # Refresh balance button
        refresh_btn_frame = ttk.Frame(account_frame)
        refresh_btn_frame.pack(pady=5)
        
        ttk.Button(
            refresh_btn_frame,
            text="🔄 Refresh Balance from Coinbase",
            command=self.refresh_balance
        ).pack()
        
        # Balance status indicator
        balance_status = "✅ Connected to Coinbase" if self.using_real_balance else "⚠️ Using Mock Balance (Set TRADING_MODE=LIVE for real balance)"
        self.balance_status_var = tk.StringVar(value=balance_status)
        ttk.Label(
            account_frame,
            textvariable=self.balance_status_var,
            font=('Helvetica', 8),
            foreground='green' if self.using_real_balance else 'orange'
        ).pack()
        
        # Average Entry Price (for existing positions)
        if self.balance_btc > 0 and self.last_buy_price == 0:
            ttk.Separator(account_frame, orient='horizontal').pack(fill=tk.X, pady=5)
            
            entry_frame = ttk.Frame(account_frame)
            entry_frame.pack(pady=5)
            
            ttk.Label(entry_frame, text="Average Entry Price ($):").pack(side=tk.LEFT)
            self.avg_entry_var = tk.StringVar(value="0")
            avg_entry_input = ttk.Entry(entry_frame, textvariable=self.avg_entry_var, width=12)
            avg_entry_input.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                entry_frame,
                text="Set Entry",
                command=self.set_manual_entry_price
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                account_frame,
                text="💡 Enter your average cost to calculate accurate profit targets",
                font=('Helvetica', 7),
                foreground='#E8E8E8'
            ).pack()
        
        # Statistics with help button
        stats_container = ttk.Frame(self.trading_tab)
        stats_container.pack(fill=tk.X, padx=10, pady=5)
        
        stats_frame = ttk.LabelFrame(stats_container, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Help button inside frame - top right corner
        help_btn_stats = ttk.Button(stats_frame, text="?", width=2, command=self.show_help_statistics)
        help_btn_stats.pack(side=tk.TOP, anchor=tk.NE, pady=(0, 5))
        
        self.stats_var = tk.StringVar(value="No trades yet")
        ttk.Label(
            stats_frame,
            textvariable=self.stats_var,
            font=('Helvetica', 11)
        ).pack()
        
        # Control buttons
        button_frame = ttk.Frame(self.trading_tab)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Monitoring",
            command=self.toggle_trading
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.buy_button = ttk.Button(
            button_frame,
            text="Execute Buy",
            command=self.manual_buy,
            state='disabled'
        )
        self.buy_button.pack(side=tk.LEFT, padx=5)
        
        # Export HTML Report button
        ttk.Button(
            button_frame,
            text="📊 Export HTML Report",
            command=self.export_html_report
        ).pack(side=tk.LEFT, padx=5)
        
    def create_buying_testing_tab(self):
        """Create the manual buying/selling testing interface"""
        # Title and description
        header_frame = ttk.Frame(self.testing_tab)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            header_frame,
            text="🧪 Manual Buying & Selling Test Center",
            font=('Helvetica', 14, 'bold')
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Test buy and sell operations manually with custom parameters",
            font=('Helvetica', 9),
            foreground='gray'
        ).pack()
        
        # Current Price Display
        price_frame = ttk.LabelFrame(self.testing_tab, text="Current Market Price", padding="10")
        price_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.test_price_var = tk.StringVar(value="$0.00")
        ttk.Label(
            price_frame,
            textvariable=self.test_price_var,
            font=('Helvetica', 20, 'bold'),
            foreground='#E8E8E8'
        ).pack()
        
        # Manual Buy Section
        buy_frame = ttk.LabelFrame(self.testing_tab, text="💰 Manual Buy Test", padding="15")
        buy_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Buy amount input
        buy_amount_frame = ttk.Frame(buy_frame)
        buy_amount_frame.pack(fill=tk.X, pady=5)
        ttk.Label(buy_amount_frame, text="Amount to Buy (USD):", width=20).pack(side=tk.LEFT)
        self.test_buy_amount_var = tk.StringVar(value="100.00")
        ttk.Entry(buy_amount_frame, textvariable=self.test_buy_amount_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # Buy price input (optional - use market price if 0)
        buy_price_frame = ttk.Frame(buy_frame)
        buy_price_frame.pack(fill=tk.X, pady=5)
        ttk.Label(buy_price_frame, text="Buy Price (0=Market):", width=20).pack(side=tk.LEFT)
        self.test_buy_price_var = tk.StringVar(value="0")
        ttk.Entry(buy_price_frame, textvariable=self.test_buy_price_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buy_price_frame,
            text="Use Market Price",
            command=self.set_test_market_price_buy
        ).pack(side=tk.LEFT, padx=5)
        
        # Buy mode selection
        buy_mode_frame = ttk.Frame(buy_frame)
        buy_mode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(buy_mode_frame, text="Execution Mode:", width=20).pack(side=tk.LEFT)
        self.test_buy_mode_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(buy_mode_frame, text="DRY RUN", variable=self.test_buy_mode_var, value=True).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(buy_mode_frame, text="LIVE", variable=self.test_buy_mode_var, value=False).pack(side=tk.LEFT, padx=5)
        
        # Execute Buy button
        ttk.Button(
            buy_frame,
            text="🛒 Execute Test Buy",
            command=self.execute_test_buy,
            style='Accent.TButton'
        ).pack(pady=10)
        
        # Buy result display
        self.test_buy_result_var = tk.StringVar(value="No buy test executed yet")
        ttk.Label(
            buy_frame,
            textvariable=self.test_buy_result_var,
            font=('Helvetica', 9),
            foreground='#E8E8E8',
            wraplength=550,
            justify='left'
        ).pack(pady=5)
        
        ttk.Separator(self.testing_tab, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)
        
        # Manual Sell Section
        sell_frame = ttk.LabelFrame(self.testing_tab, text="💵 Manual Sell Test", padding="15")
        sell_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Sell amount input (BTC)
        sell_amount_frame = ttk.Frame(sell_frame)
        sell_amount_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sell_amount_frame, text="Amount to Sell (BTC):", width=20).pack(side=tk.LEFT)
        self.test_sell_amount_var = tk.StringVar(value="0.001")
        ttk.Entry(sell_amount_frame, textvariable=self.test_sell_amount_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            sell_amount_frame,
            text="Use All BTC",
            command=self.set_test_all_btc
        ).pack(side=tk.LEFT, padx=5)
        
        # Sell price input (optional - use market price if 0)
        sell_price_frame = ttk.Frame(sell_frame)
        sell_price_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sell_price_frame, text="Sell Price (0=Market):", width=20).pack(side=tk.LEFT)
        self.test_sell_price_var = tk.StringVar(value="0")
        ttk.Entry(sell_price_frame, textvariable=self.test_sell_price_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            sell_price_frame,
            text="Use Market Price",
            command=self.set_test_market_price_sell
        ).pack(side=tk.LEFT, padx=5)
        
        # Sell mode selection
        sell_mode_frame = ttk.Frame(sell_frame)
        sell_mode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sell_mode_frame, text="Execution Mode:", width=20).pack(side=tk.LEFT)
        self.test_sell_mode_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(sell_mode_frame, text="DRY RUN", variable=self.test_sell_mode_var, value=True).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sell_mode_frame, text="LIVE", variable=self.test_sell_mode_var, value=False).pack(side=tk.LEFT, padx=5)
        
        # Execute Sell button
        ttk.Button(
            sell_frame,
            text="💰 Execute Test Sell",
            command=self.execute_test_sell,
            style='Accent.TButton'
        ).pack(pady=10)
        
        # Sell result display
        self.test_sell_result_var = tk.StringVar(value="No sell test executed yet")
        ttk.Label(
            sell_frame,
            textvariable=self.test_sell_result_var,
            font=('Helvetica', 9),
            foreground='#E8E8E8',
            wraplength=550,
            justify='left'
        ).pack(pady=5)
        
        # Current Test Balance Display
        balance_frame = ttk.LabelFrame(self.testing_tab, text="Current Balance", padding="10")
        balance_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.test_balance_display_var = tk.StringVar(
            value=f"USD: ${self.balance_usd:.2f}  |  BTC: {self.balance_btc:.8f}"
        )
        ttk.Label(
            balance_frame,
            textvariable=self.test_balance_display_var,
            font=('Helvetica', 11, 'bold')
        ).pack()
        
        # Warning notice
        warning_frame = ttk.Frame(self.testing_tab)
        warning_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            warning_frame,
            text="⚠️ WARNING: LIVE mode will execute real orders on Coinbase. Always test with DRY RUN first!",
            font=('Helvetica', 9, 'bold'),
            foreground='red',
            wraplength=550,
            justify='center'
        ).pack()
    
    def set_test_market_price_buy(self):
        """Set buy price to current market price"""
        if self.current_price > 0:
            self.test_buy_price_var.set(f"{self.current_price:.2f}")
        else:
            print("⚠️ Waiting for price data...")
    
    def set_test_market_price_sell(self):
        """Set sell price to current market price"""
        if self.current_price > 0:
            self.test_sell_price_var.set(f"{self.current_price:.2f}")
        else:
            print("⚠️ Waiting for price data...")
    
    def set_test_all_btc(self):
        """Set sell amount to all available BTC"""
        self.test_sell_amount_var.set(f"{self.balance_btc:.8f}")
    
    def execute_test_buy(self):
        """Execute a test buy order"""
        try:
            # Get parameters
            buy_amount = float(self.test_buy_amount_var.get())
            buy_price_str = self.test_buy_price_var.get().replace(',', '').replace('$', '')
            buy_price = float(buy_price_str) if buy_price_str and buy_price_str != '0' else self.current_price
            is_dry_run = self.test_buy_mode_var.get()
            
            # Validate
            if buy_amount <= 0:
                self.test_buy_result_var.set("❌ Error: Buy amount must be positive")
                return
            
            if buy_price <= 0:
                self.test_buy_result_var.set("❌ Error: Invalid price. Start monitoring to get market price.")
                return
            
            # Validate minimum amount ($5)
            if buy_amount < self.min_position_size:
                self.test_buy_result_var.set(f"❌ Error: Minimum buy amount is ${self.min_position_size:.2f}. You tried ${buy_amount:.2f}")
                print(f"\n❌ Buy amount too small! Minimum is ${self.min_position_size:.2f}, you tried ${buy_amount:.2f}")
                return
            
            # In DRY RUN mode: Skip balance validation (use simulated balance)
            # In LIVE mode: Validate only if not using payment method
            if is_dry_run:
                # DRY RUN: No balance check, simulate unlimited funds
                print(f"\n💡 DRY RUN MODE: Using simulated balance (no real funds needed)")
            else:
                # LIVE mode: Will use Coinbase payment method (card) if insufficient balance
                print(f"\n🔴 LIVE MODE: Will attempt purchase with Coinbase payment method if needed")
                if buy_amount > self.balance_usd:
                    print(f"   ℹ️ Insufficient wallet balance (${self.balance_usd:.2f})")
                    print(f"   💳 Will use attached payment method for ${buy_amount:.2f}")
            
            # Calculate
            buy_fee = buy_amount * self.buy_fee_rate
            net_investment = buy_amount - buy_fee
            btc_amount = net_investment / buy_price
            
            mode_str = "DRY RUN" if is_dry_run else "LIVE"
            
            # FASE 3: Validate price before LIVE execution
            if not is_dry_run:
                print(f"\n🔍 Validating price before test buy order...")
                is_valid, validated_price, error_msg = self.validate_price_before_execution(buy_price, "TEST BUY")
                
                if not is_valid:
                    self.test_buy_result_var.set(f"{error_msg}\n⚠️ Order cancelled")
                    print(error_msg)
                    print(f"⚠️ TEST BUY ORDER CANCELLED - Price validation failed")
                    return
                
                # Use validated price
                buy_price = validated_price
                btc_amount = net_investment / buy_price
            
            # Execute real order if LIVE mode
            if not is_dry_run:
                from trading_helpers import TradingHelpers
                helpers = TradingHelpers()
                
                print(f"\n🔴 EXECUTING REAL TEST BUY ORDER...")
                print(f"   Amount: ${buy_amount:.2f}")
                print(f"   Price: ${buy_price:,.2f}")
                print(f"   💳 Using Coinbase payment method (card/bank)")
                
                result = helpers.buy_btc_market(usd_amount=buy_amount)
                
                if not result.get('success'):
                    error_msg = result.get('error', 'Unknown error')
                    self.test_buy_result_var.set(f"❌ REAL BUY FAILED: {error_msg}")
                    print(f"❌ REAL TEST BUY FAILED: {error_msg}")
                    return
                
                print(f"✅ REAL TEST BUY EXECUTED: Order ID {result.get('order_id')}")
                
                # In LIVE mode, refresh balance from Coinbase after purchase
                print(f"🔄 Refreshing balance from Coinbase...")
                self.refresh_balance()
            else:
                # DRY RUN: Update simulated balances
                self.balance_usd -= buy_amount
                self.balance_btc += btc_amount
            
            # Update displays
            self.test_balance_display_var.set(f"USD: ${self.balance_usd:.2f}  |  BTC: {self.balance_btc:.8f}")
            self.balance_var.set(f"USD: ${self.balance_usd:.2f}\nBTC: {self.balance_btc:.8f}")
            
            # Show result
            payment_info = "" if is_dry_run else "\n💳 Paid with Coinbase payment method"
            result_text = (
                f"✅ {mode_str} BUY EXECUTED{payment_info}\n"
                f"Buy Price: ${buy_price:,.2f}\n"
                f"USD Spent: ${buy_amount:.2f}\n"
                f"Buy Fee (0.6%): ${buy_fee:.2f}\n"
                f"BTC Received: {btc_amount:.8f} BTC\n"
                f"Net Investment: ${net_investment:.2f}"
            )
            self.test_buy_result_var.set(result_text)
            
            print(f"\n{'='*60}")
            print(f"✅ TEST BUY EXECUTED [{mode_str}]")
            print(f"{'='*60}")
            print(f"Buy Price: ${buy_price:,.2f}")
            print(f"USD Spent: ${buy_amount:.2f}")
            print(f"Buy Fee (0.6%): ${buy_fee:.2f}")
            print(f"BTC Received: {btc_amount:.8f} BTC")
            print(f"Net Investment: ${net_investment:.2f}")
            print(f"{'='*60}")
            
        except ValueError as e:
            self.test_buy_result_var.set(f"❌ Error: Invalid input - {e}")
        except Exception as e:
            self.test_buy_result_var.set(f"❌ Error: {str(e)}")
            print(f"❌ Test buy error: {e}")
    
    def execute_test_sell(self):
        """Execute a test sell order"""
        try:
            # Get parameters
            sell_amount_btc = float(self.test_sell_amount_var.get())
            sell_price_str = self.test_sell_price_var.get().replace(',', '').replace('$', '')
            sell_price = float(sell_price_str) if sell_price_str and sell_price_str != '0' else self.current_price
            is_dry_run = self.test_sell_mode_var.get()
            
            # Validate
            if sell_amount_btc <= 0:
                self.test_sell_result_var.set("❌ Error: Sell amount must be positive")
                return
            
            if sell_price <= 0:
                self.test_sell_result_var.set("❌ Error: Invalid price. Start monitoring to get market price.")
                return
            
            # In DRY RUN mode: Skip BTC balance validation (use simulated balance)
            # In LIVE mode: Validate BTC balance
            if is_dry_run:
                # DRY RUN: No balance check, simulate having BTC
                print(f"\n💡 DRY RUN MODE: Using simulated BTC balance (no real BTC needed)")
            else:
                # LIVE mode: Must have actual BTC to sell
                if sell_amount_btc > self.balance_btc:
                    self.test_sell_result_var.set(f"❌ Error: Insufficient BTC. Need {sell_amount_btc:.8f}, have {self.balance_btc:.8f}")
                    return
            
            # Calculate
            gross_proceeds = sell_amount_btc * sell_price
            sell_fee = gross_proceeds * self.sell_fee_rate
            net_proceeds = gross_proceeds - sell_fee
            
            mode_str = "DRY RUN" if is_dry_run else "LIVE"
            
            # FASE 3: Validate price before LIVE execution
            if not is_dry_run:
                print(f"\n🔍 Validating price before test sell order...")
                is_valid, validated_price, error_msg = self.validate_price_before_execution(sell_price, "TEST SELL")
                
                if not is_valid:
                    self.test_sell_result_var.set(f"{error_msg}\n⚠️ Order cancelled")
                    print(error_msg)
                    print(f"⚠️ TEST SELL ORDER CANCELLED - Price validation failed")
                    return
                
                # Use validated price
                sell_price = validated_price
                # Recalculate with validated price
                gross_proceeds = sell_amount_btc * sell_price
                sell_fee = gross_proceeds * self.sell_fee_rate
                net_proceeds = gross_proceeds - sell_fee
            
            # Execute real order if LIVE mode
            if not is_dry_run:
                from trading_helpers import TradingHelpers
                helpers = TradingHelpers()
                
                print(f"\n🔴 EXECUTING REAL TEST SELL ORDER...")
                print(f"   Amount: {sell_amount_btc:.8f} BTC")
                print(f"   Price: ${sell_price:,.2f}")
                
                result = helpers.sell_btc_market(btc_amount=sell_amount_btc)
                
                if not result.get('success'):
                    error_msg = result.get('error', 'Unknown error')
                    self.test_sell_result_var.set(f"❌ REAL SELL FAILED: {error_msg}")
                    print(f"❌ REAL TEST SELL FAILED: {error_msg}")
                    return
                
                print(f"✅ REAL TEST SELL EXECUTED: Order ID {result.get('order_id')}")
                
                # In LIVE mode, refresh balance from Coinbase after sale
                print(f"🔄 Refreshing balance from Coinbase...")
                self.refresh_balance()
            else:
                # DRY RUN: Update simulated balances
                self.balance_btc -= sell_amount_btc
                self.balance_usd += net_proceeds
            
            # Update displays
            self.test_balance_display_var.set(f"USD: ${self.balance_usd:.2f}  |  BTC: {self.balance_btc:.8f}")
            self.balance_var.set(f"USD: ${self.balance_usd:.2f}\nBTC: {self.balance_btc:.8f}")
            
            # Show result
            result_text = (
                f"✅ {mode_str} SELL EXECUTED\n"
                f"Sell Price: ${sell_price:,.2f}\n"
                f"BTC Sold: {sell_amount_btc:.8f} BTC\n"
                f"Gross Proceeds: ${gross_proceeds:.2f}\n"
                f"Sell Fee (0.6%): ${sell_fee:.2f}\n"
                f"Net Proceeds: ${net_proceeds:.2f}"
            )
            self.test_sell_result_var.set(result_text)
            
            print(f"\n{'='*60}")
            print(f"✅ TEST SELL EXECUTED [{mode_str}]")
            print(f"{'='*60}")
            print(f"Sell Price: ${sell_price:,.2f}")
            print(f"BTC Sold: {sell_amount_btc:.8f} BTC")
            print(f"Gross Proceeds: ${gross_proceeds:.2f}")
            print(f"Sell Fee (0.6%): ${sell_fee:.2f}")
            print(f"Net Proceeds: ${net_proceeds:.2f}")
            print(f"{'='*60}")
            
        except ValueError as e:
            self.test_sell_result_var.set(f"❌ Error: Invalid input - {e}")
        except Exception as e:
            self.test_sell_result_var.set(f"❌ Error: {str(e)}")
            print(f"❌ Test sell error: {e}")
    
    def create_configuration_tab(self):
        """Create the configuration interface"""
        # Store real API credentials
        self.real_api_key = Config.COINBASE_API_KEY
        self.real_api_secret = Config.COINBASE_API_SECRET
        self.api_key_visible = False
        self.api_secret_visible = False
        
        # API Configuration Section
        api_frame = ttk.LabelFrame(self.config_tab, text="🔐 API Configuration", padding="15")
        api_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # API Key
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="API Key:", width=20).pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=self.mask_api_key(Config.COINBASE_API_KEY))
        self.api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, width=50)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        self.api_key_btn = ttk.Button(key_frame, text="👁️", width=3, command=self.toggle_api_key_visibility)
        self.api_key_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(key_frame, text="✏️", width=3, command=self.edit_api_key).pack(side=tk.LEFT)
        
        # API Secret
        secret_frame = ttk.Frame(api_frame)
        secret_frame.pack(fill=tk.X, pady=5)
        ttk.Label(secret_frame, text="API Secret:", width=20).pack(side=tk.LEFT)
        self.api_secret_var = tk.StringVar(value=self.mask_api_key(Config.COINBASE_API_SECRET))
        self.api_secret_entry = ttk.Entry(secret_frame, textvariable=self.api_secret_var, width=50)
        self.api_secret_entry.pack(side=tk.LEFT, padx=5)
        self.api_secret_btn = ttk.Button(secret_frame, text="👁️", width=3, command=self.toggle_api_secret_visibility)
        self.api_secret_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(secret_frame, text="✏️", width=3, command=self.edit_api_secret).pack(side=tk.LEFT)
        
        # Helper text
        ttk.Label(
            api_frame,
            text="💡 Tip: Click ✏️ to edit, paste your credentials, then click 'Save Configuration'",
            font=('Helvetica', 8),
            foreground='#E8E8E8'
        ).pack(pady=5)
        
        # Trading Mode
        mode_frame = ttk.Frame(api_frame)
        mode_frame.pack(fill=tk.X, pady=10)
        ttk.Label(mode_frame, text="Trading Mode:", width=20).pack(side=tk.LEFT)
        self.config_mode_var = tk.StringVar(value=Config.TRADING_MODE)
        ttk.Radiobutton(mode_frame, text="SIMULATION", variable=self.config_mode_var, value="SIMULATION").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="LIVE", variable=self.config_mode_var, value="LIVE").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            api_frame,
            text="⚠️ LIVE mode requires valid API credentials and will execute real trades",
            font=('Helvetica', 8),
            foreground='red'
        ).pack(pady=5)
        
        # Trading Parameters Section
        params_frame = ttk.LabelFrame(self.config_tab, text="📊 Trading Parameters", padding="15")
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fee Rates
        buy_fee_frame = ttk.Frame(params_frame)
        buy_fee_frame.pack(fill=tk.X, pady=3)
        ttk.Label(buy_fee_frame, text="Buy Fee Rate (%):", width=20).pack(side=tk.LEFT)
        # Format fee with 1 decimal place (e.g., 0.6 instead of 0.6000...)
        self.config_buy_fee_var = tk.StringVar(value=f"{self.buy_fee_rate * 100:.1f}")
        ttk.Entry(buy_fee_frame, textvariable=self.config_buy_fee_var, width=10).pack(side=tk.LEFT, padx=5)
        
        sell_fee_frame = ttk.Frame(params_frame)
        sell_fee_frame.pack(fill=tk.X, pady=3)
        ttk.Label(sell_fee_frame, text="Sell Fee Rate (%):", width=20).pack(side=tk.LEFT)
        # Format fee with 1 decimal place
        self.config_sell_fee_var = tk.StringVar(value=f"{self.sell_fee_rate * 100:.1f}")
        ttk.Entry(sell_fee_frame, textvariable=self.config_sell_fee_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Buy Amount with Coinbase balance validation
        buy_frame = ttk.Frame(params_frame)
        buy_frame.pack(fill=tk.X, pady=5)  # Increased padding
        
        # Label with fixed width and right-aligned text
        label_frame = ttk.Frame(buy_frame)
        label_frame.pack(side=tk.LEFT)
        ttk.Label(
            label_frame,
            text="Default Buy Amount:",
            width=18,
            anchor='e'  # Right-align text
        ).pack(side=tk.LEFT)
        
        # USD in bold
        ttk.Label(
            label_frame,
            text="(USD)",
            font=('Helvetica', 9, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Entry field
        self.config_position_var = tk.StringVar(value="5.00")
        ttk.Entry(buy_frame, textvariable=self.config_position_var, width=10).pack(side=tk.LEFT)
        
        # Available balance with better spacing
        balance_text = f"Available: ${self.balance_usd:.2f}" if self.using_real_balance else "(Min: $5.00)"
        self.config_balance_label = ttk.Label(
            buy_frame,
            text=balance_text,
            foreground='green' if self.using_real_balance else 'gray'
        )
        self.config_balance_label.pack(side=tk.LEFT, padx=10)
        
        # Help text
        ttk.Label(
            buy_frame,
            text="(amount to invest in crypto)",
            foreground='gray',
            font=('Helvetica', 8)
        ).pack(side=tk.LEFT)
        
        # Profit Rate
        profit_frame = ttk.Frame(params_frame)
        profit_frame.pack(fill=tk.X, pady=3)
        ttk.Label(profit_frame, text="Profit Target (%):", width=20).pack(side=tk.LEFT)
        # Format profit rate as percentage with 1 decimal place
        self.config_profit_var = tk.StringVar(value=f"{self.profit_rate * 100:.1f}")
        ttk.Entry(profit_frame, textvariable=self.config_profit_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(profit_frame, text="(Recommended: ≥2.5%)", foreground='gray').pack(side=tk.LEFT, padx=5)
        
        # Save button for Trading Parameters
        save_params_btn = ttk.Button(
            params_frame,
            text="💾 Save Trading Parameters",
            command=self.save_trading_parameters
        )
        save_params_btn.pack(pady=10)
        
        # Status label for Trading Parameters save
        self.params_save_status_var = tk.StringVar(value="")
        self.params_save_status_label = ttk.Label(
            params_frame,
            textvariable=self.params_save_status_var,
            font=('Helvetica', 9, 'bold')
        )
        self.params_save_status_label.pack(pady=5)
        
        # Connection Status Section
        status_frame = ttk.LabelFrame(self.config_tab, text="📡 Connection Status", padding="15")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # API Status
        api_status_text = "✅ Connected" if self.api.is_jwt_format else "❌ Not Connected"
        self.api_status_var = tk.StringVar(value=f"Coinbase API: {api_status_text}")
        ttk.Label(status_frame, textvariable=self.api_status_var, font=('Helvetica', 10)).pack(anchor='w', pady=2)
        
        # Balance Status
        balance_status_text = "✅ Using Real Balance" if self.using_real_balance else "⚠️ Using Mock Balance"
        self.config_balance_status_var = tk.StringVar(value=f"Balance: {balance_status_text}")
        ttk.Label(status_frame, textvariable=self.config_balance_status_var, font=('Helvetica', 10)).pack(anchor='w', pady=2)
        
        # Mode Status
        mode_status_text = f"Mode: {Config.TRADING_MODE}"
        self.mode_status_var = tk.StringVar(value=mode_status_text)
        ttk.Label(status_frame, textvariable=self.mode_status_var, font=('Helvetica', 10)).pack(anchor='w', pady=2)
        
        # Test Result Status (NEW)
        self.test_result_var = tk.StringVar(value="")
        self.test_result_label = ttk.Label(
            status_frame,
            textvariable=self.test_result_var,
            font=('Helvetica', 11, 'bold')
        )
        self.test_result_label.pack(anchor='w', pady=5)
        
        # Endpoints Status Section (NEW)
        ttk.Separator(status_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        ttk.Label(status_frame, text="Endpoints Status:", font=('Helvetica', 10, 'bold')).pack(anchor='w', pady=2)
        
        # Individual endpoint status labels
        self.endpoint_btc_price_var = tk.StringVar(value="📊 BTC Price: ⚪ Not tested")
        ttk.Label(status_frame, textvariable=self.endpoint_btc_price_var, font=('Helvetica', 9)).pack(anchor='w', padx=20, pady=1)
        
        self.endpoint_wallet_var = tk.StringVar(value="💰 Wallet Balance: ⚪ Not tested")
        ttk.Label(status_frame, textvariable=self.endpoint_wallet_var, font=('Helvetica', 9)).pack(anchor='w', padx=20, pady=1)
        
        self.endpoint_orders_var = tk.StringVar(value="📝 Orders (Buy/Sell): ⚪ Not tested")
        ttk.Label(status_frame, textvariable=self.endpoint_orders_var, font=('Helvetica', 9)).pack(anchor='w', padx=20, pady=1)
        
        self.endpoint_products_var = tk.StringVar(value="📈 Products: ⚪ Not tested")
        ttk.Label(status_frame, textvariable=self.endpoint_products_var, font=('Helvetica', 9)).pack(anchor='w', padx=20, pady=1)
        
        # Action Buttons
        button_frame = ttk.Frame(self.config_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=15)
        
        ttk.Button(
            button_frame,
            text="💾 Save Configuration to .env",
            command=self.save_configuration
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Reload Configuration",
            command=self.reload_configuration
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🧪 Test API Connection",
            command=self.test_api_connection
        ).pack(side=tk.LEFT, padx=5)
        
        # Info Section
        info_frame = ttk.Frame(self.config_tab)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = (
            "ℹ️ Configuration Tips:\n\n"
            "• API credentials are stored in the .env file\n"
            "• SIMULATION mode is safe for testing\n"
            "• LIVE mode requires valid API keys with trading permissions\n"
            "• Fee rates are typically 0.6% (0.006) for Coinbase\n"
            "• Always test with SIMULATION mode first\n"
        )
        ttk.Label(
            info_frame,
            text=info_text,
            font=('Helvetica', 9),
            foreground='#E8E8E8',
            justify='left'
        ).pack(anchor='w')
    
    def edit_api_key(self):
        """Clear API Key field for editing"""
        self.api_key_var.set("")
        self.api_key_entry.focus()
        self.api_key_visible = True
        self.api_key_btn.configure(text="🙈")
        print("✏️ Edit mode: Paste your COINBASE_API_KEY here")
    
    def edit_api_secret(self):
        """Clear API Secret field for editing"""
        self.api_secret_var.set("")
        self.api_secret_entry.focus()
        self.api_secret_visible = True
        self.api_secret_btn.configure(text="🙈")
        print("✏️ Edit mode: Paste your COINBASE_API_SECRET here")
        print("   For private keys, paste the entire key including BEGIN/END markers")
    
    def mask_api_key(self, key):
        """Mask API key for display"""
        if not key or len(key) < 8:
            return "Not Set"
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    
    def toggle_api_key_visibility(self):
        """Toggle API Key visibility"""
        self.api_key_visible = not self.api_key_visible
        if self.api_key_visible:
            self.api_key_var.set(self.real_api_key if self.real_api_key else "Not Set")
            self.api_key_btn.configure(text="🙈")
        else:
            self.api_key_var.set(self.mask_api_key(self.real_api_key))
            self.api_key_btn.configure(text="👁️")
    
    def toggle_api_secret_visibility(self):
        """Toggle API Secret visibility"""
        self.api_secret_visible = not self.api_secret_visible
        if self.api_secret_visible:
            self.api_secret_var.set(self.real_api_secret if self.real_api_secret else "Not Set")
            self.api_secret_btn.configure(text="🙈")
        else:
            self.api_secret_var.set(self.mask_api_key(self.real_api_secret))
            self.api_secret_btn.configure(text="👁️")
    
    def save_trading_parameters(self):
        """Save Trading Parameters with Coinbase balance validation"""
        try:
            # Get values
            buy_fee = float(self.config_buy_fee_var.get())
            sell_fee = float(self.config_sell_fee_var.get())
            position_size = float(self.config_position_var.get())
            profit_target = float(self.config_profit_var.get())
            
            # Validate ranges
            if buy_fee < 0 or sell_fee < 0:
                raise ValueError("Fees cannot be negative")
            if profit_target <= 0:
                raise ValueError("Profit target must be positive")
            if position_size < self.min_position_size:
                raise ValueError(f"Position size must be at least ${self.min_position_size:.2f}")
            
            # CRITICAL: Validate against Coinbase balance
            if self.using_real_balance:
                if position_size > self.balance_usd:
                    self.params_save_status_var.set(
                        f"❌ ERROR: Fondos Insuficientes | Disponible: ${self.balance_usd:.2f} | Intentando: ${position_size:.2f}"
                    )
                    self.params_save_status_label.configure(foreground='red')
                    
                    print(f"\n❌ ERROR: FONDOS INSUFICIENTES")
                    print(f"   Intentando configurar: ${position_size:.2f} USD")
                    print(f"   Balance disponible en Coinbase: ${self.balance_usd:.2f} USD")
                    print(f"   Faltante: ${position_size - self.balance_usd:.2f} USD")
                    print(f"\n💡 SOLUCIÓN: Usa ${self.balance_usd:.2f} o menos")
                    return
            
            # Apply values
            self.buy_fee_rate = buy_fee / 100
            self.sell_fee_rate = sell_fee / 100
            self.position_size = position_size
            self.profit_rate = profit_target / 100
            
            # Update Trading tab
            self.profit_var.set(f"{profit_target:.1f}")
            
            # Show success message
            self.params_save_status_var.set(
                f"✅ Guardado Exitoso | Position: ${position_size:.2f} | Profit: {profit_target:.1f}%"
            )
            self.params_save_status_label.configure(foreground='green')
            
            print(f"\n✅ Trading Parameters Saved Successfully")
            print(f"   Buy Fee: {buy_fee:.1f}%")
            print(f"   Sell Fee: {sell_fee:.1f}%")
            print(f"   Position Size: ${position_size:.2f}")
            print(f"   Profit Target: {profit_target:.1f}%")
            if self.using_real_balance:
                print(f"   Balance Disponible: ${self.balance_usd:.2f}")
            
            # Clear message after 5 seconds
            self.root.after(5000, lambda: self.params_save_status_var.set(""))
            
            # Update display
            self.check_position()
            
        except ValueError as e:
            self.params_save_status_var.set(f"❌ ERROR: {str(e)}")
            self.params_save_status_label.configure(foreground='red')
            print(f"\n❌ Error validando parámetros: {e}")
            self.root.after(5000, lambda: self.params_save_status_var.set(""))
    
    def save_configuration(self):
        """Save configuration to .env file"""
        try:
            import os
            import sys
            from pathlib import Path
            
            # Find correct .env location (for both script and executable)
            if getattr(sys, 'frozen', False):
                # Running as executable - save in user's AppData
                app_data = os.path.join(os.getenv('APPDATA'), 'Cripto-Bot')
                # Create directory if it doesn't exist
                os.makedirs(app_data, exist_ok=True)
                env_path = Path(os.path.join(app_data, '.env'))
                print(f"📁 Executable mode: Saving to {env_path}")
            else:
                # Running as script
                env_path = Path('.env')
            
            # Read current .env or .env.example
            env_content = {}
            
            # Try to read existing .env first
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key.strip()] = value.strip()
            else:
                # If .env doesn't exist, read from .env.example
                example_path = env_path.parent / '.env.example'
                if example_path.exists():
                    with open(example_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                env_content[key.strip()] = value.strip()
                    print("📝 Creating new .env from template")
            
            # Get values from UI
            api_key = self.api_key_var.get().strip()
            api_secret = self.api_secret_var.get().strip()
            
            # Track what was edited
            api_key_was_edited = self.api_key_visible or (api_key and not api_key.startswith('*'))
            api_secret_was_edited = self.api_secret_visible or (api_secret and not api_secret.startswith('*'))
            
            # Update or remove API Key
            if api_key_was_edited:
                if api_key and api_key != "Not Set" and not api_key.startswith('*'):
                    # Valid key provided - update it
                    env_content['COINBASE_API_KEY'] = api_key
                    self.real_api_key = api_key
                    print(f"✅ API Key updated: {api_key[:20]}...")
                else:
                    # Empty field - remove from .env
                    if 'COINBASE_API_KEY' in env_content:
                        del env_content['COINBASE_API_KEY']
                    self.real_api_key = ""
                    print(f"🗑️ API Key removed from .env")
            
            # Update or remove API Secret
            if api_secret_was_edited:
                if api_secret and api_secret != "Not Set" and not api_secret.startswith('*'):
                    # Valid secret provided - update it
                    env_content['COINBASE_API_SECRET'] = api_secret
                    self.real_api_secret = api_secret
                    print(f"✅ API Secret updated")
                else:
                    # Empty field - remove from .env
                    if 'COINBASE_API_SECRET' in env_content:
                        del env_content['COINBASE_API_SECRET']
                    if 'COINBASE_PRIVATE_KEY_FILE' in env_content:
                        del env_content['COINBASE_PRIVATE_KEY_FILE']
                    self.real_api_secret = ""
                    print(f"🗑️ API Secret removed from .env")
            
            # Update trading mode
            env_content['TRADING_MODE'] = self.config_mode_var.get()
            env_content['SIMULATION_MODE'] = 'False' if self.config_mode_var.get() == 'LIVE' else 'True'
            
            # Write back to .env
            with open(env_path, 'w') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
            
            # Update runtime config
            try:
                self.buy_fee_rate = float(self.config_buy_fee_var.get()) / 100
                self.sell_fee_rate = float(self.config_sell_fee_var.get()) / 100
                self.profit_rate = float(self.config_profit_var.get()) / 100
                
                # SYNC: Update Trading tab value to match Configuration tab
                self.profit_var.set(f"{self.profit_rate * 100:.1f}")
                
                # Validate position size (minimum $5)
                new_position_size = float(self.config_position_var.get())
                if new_position_size < self.min_position_size:
                    print(f"\n⚠️ Position size too small! Minimum is ${self.min_position_size:.2f}")
                    print(f"   Setting to minimum: ${self.min_position_size:.2f}")
                    self.position_size = self.min_position_size
                    self.config_position_var.set(str(self.min_position_size))
                else:
                    self.position_size = new_position_size
                    
            except ValueError as e:
                print(f"\n⚠️ Invalid configuration value: {e}")
                pass
            
            print("\n✅ Configuration saved to .env file")
            print(f"   Location: {env_path}")
            print(f"   Profit Target: {self.profit_rate*100:.2f}%")
            print(f"   Position Size: ${self.position_size:.2f}")
            print(f"   Trading Mode: {self.config_mode_var.get()}")
            print("\n🔄 Reloading configuration...")
            
            # Reset visibility flags after save
            self.api_key_visible = False
            self.api_secret_visible = False
            self.api_key_btn.configure(text="👁️")
            self.api_secret_btn.configure(text="👁️")
            
            # Auto-reload configuration
            self.reload_configuration()
            
            # Build status message
            status_msg = "✅ Configuration saved successfully!\n\n"
            status_msg += f"Location: {env_path}\n"
            status_msg += f"Trading Mode: {self.config_mode_var.get()}\n\n"
            
            # Show what was saved/removed
            if api_key_was_edited:
                if self.real_api_key:
                    status_msg += f"✅ API Key: Updated\n"
                else:
                    status_msg += f"🗑️ API Key: Removed\n"
            
            if api_secret_was_edited:
                if self.real_api_secret:
                    status_msg += f"✅ API Secret: Updated\n"
                else:
                    status_msg += f"🗑️ API Secret: Removed\n"
            
            status_msg += "\nThe API connection has been reloaded.\n"
            status_msg += "Click 'Test API Connection' to verify."
            
            # Show success message
            messagebox.showinfo(
                "Configuration Saved",
                status_msg
            )
            
        except Exception as e:
            error_msg = f"❌ Error saving configuration: {e}"
            print(f"\n{error_msg}")
            messagebox.showerror(
                "Error al Guardar",
                f"❌ No se pudo guardar la configuración.\n\n"
                f"Error: {str(e)}\n\n"
                f"Verifica que:\n"
                f"• Las credenciales sean válidas\n"
                f"• Tengas permisos de escritura\n"
                f"• El formato sea correcto"
            )
    
    def reload_configuration(self):
        """Reload configuration from .env"""
        try:
            from dotenv import load_dotenv
            import os
            
            load_dotenv(override=True)
            
            # Update Config class
            Config.COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
            Config.COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET', '')
            Config.TRADING_MODE = os.getenv('TRADING_MODE', 'SIMULATION')
            
            # Update display
            self.api_key_var.set(self.mask_api_key(Config.COINBASE_API_KEY))
            self.api_secret_var.set(self.mask_api_key(Config.COINBASE_API_SECRET))
            self.config_mode_var.set(Config.TRADING_MODE)
            self.mode_status_var.set(f"Mode: {Config.TRADING_MODE}")
            
            # Reinitialize API
            self.api = CoinbaseCompleteAPI()
            
            # Update status
            api_status_text = "✅ Connected" if self.api.is_jwt_format else "❌ Not Connected"
            self.api_status_var.set(f"Coinbase API: {api_status_text}")
            
            print("\n✅ Configuration reloaded successfully")
            
        except Exception as e:
            print(f"\n❌ Error reloading configuration: {e}")
    
    def test_api_connection(self):
        """Test API connection and show visual result for each endpoint"""
        try:
            print("\n🔄 Testing API endpoints...")
            
            # Clear previous results
            self.test_result_var.set("🔄 Testing endpoints...")
            self.test_result_label.configure(foreground='#E8E8E8')
            self.endpoint_btc_price_var.set("📊 BTC Price: 🔄 Testing...")
            self.endpoint_wallet_var.set("💰 Wallet Balance: 🔄 Testing...")
            self.endpoint_orders_var.set("📝 Orders (Buy/Sell): 🔄 Testing...")
            self.endpoint_products_var.set("📈 Products: 🔄 Testing...")
            self.root.update()
            
            if not self.api.is_jwt_format:
                print("❌ API not initialized (invalid credentials format)")
                self.test_result_var.set("🔴 OFFLINE - Invalid credentials format")
                self.test_result_label.configure(foreground='red')
                self.api_status_var.set("Coinbase API: ❌ Not Connected")
                
                # Update all endpoints to offline
                self.endpoint_btc_price_var.set("📊 BTC Price: 🔴 OFFLINE")
                self.endpoint_wallet_var.set("💰 Wallet Balance: 🔴 OFFLINE")
                self.endpoint_orders_var.set("📝 Orders (Buy/Sell): 🔴 OFFLINE")
                self.endpoint_products_var.set("📈 Products: 🔴 OFFLINE")
                return False
            
            endpoints_status = {}
            all_online = True
            
            # Test 1: BTC Price Endpoint (Public API)
            try:
                import requests
                response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot', timeout=5)
                if response.status_code == 200:
                    price = float(response.json()['data']['amount'])
                    self.endpoint_btc_price_var.set(f"📊 BTC Price: 🟢 ONLINE (${price:,.2f})")
                    endpoints_status['btc_price'] = True
                    print(f"✅ BTC Price Endpoint: ONLINE (${price:,.2f})")
                else:
                    self.endpoint_btc_price_var.set("📊 BTC Price: 🔴 OFFLINE")
                    endpoints_status['btc_price'] = False
                    all_online = False
                    print("❌ BTC Price Endpoint: OFFLINE")
            except Exception as e:
                self.endpoint_btc_price_var.set("📊 BTC Price: 🔴 OFFLINE")
                endpoints_status['btc_price'] = False
                all_online = False
                print(f"❌ BTC Price Endpoint: OFFLINE - {e}")
            
            # Test 2: Wallet Balance Endpoint
            try:
                accounts = self.api.list_accounts()
                if accounts and 'accounts' in accounts:
                    num_accounts = len(accounts['accounts'])
                    self.endpoint_wallet_var.set(f"💰 Wallet Balance: 🟢 ONLINE ({num_accounts} accounts)")
                    endpoints_status['wallet'] = True
                    print(f"✅ Wallet Balance Endpoint: ONLINE ({num_accounts} accounts)")
                else:
                    self.endpoint_wallet_var.set("💰 Wallet Balance: 🟡 PARTIAL")
                    endpoints_status['wallet'] = False
                    all_online = False
                    print("⚠️ Wallet Balance Endpoint: PARTIAL")
            except Exception as e:
                self.endpoint_wallet_var.set("💰 Wallet Balance: 🔴 OFFLINE")
                endpoints_status['wallet'] = False
                all_online = False
                print(f"❌ Wallet Balance Endpoint: OFFLINE - {e}")
            
            # Test 3: Orders Endpoint (Buy/Sell)
            try:
                orders = self.api.list_orders()
                if orders is not None:
                    self.endpoint_orders_var.set("📝 Orders (Buy/Sell): 🟢 ONLINE")
                    endpoints_status['orders'] = True
                    print("✅ Orders Endpoint: ONLINE")
                else:
                    self.endpoint_orders_var.set("📝 Orders (Buy/Sell): 🔴 OFFLINE")
                    endpoints_status['orders'] = False
                    all_online = False
                    print("❌ Orders Endpoint: OFFLINE")
            except Exception as e:
                self.endpoint_orders_var.set("📝 Orders (Buy/Sell): 🔴 OFFLINE")
                endpoints_status['orders'] = False
                all_online = False
                print(f"❌ Orders Endpoint: OFFLINE - {e}")
            
            # Test 4: Products Endpoint
            try:
                products = self.api.list_products()
                if products and 'products' in products:
                    num_products = len(products['products'])
                    self.endpoint_products_var.set(f"📈 Products: 🟢 ONLINE ({num_products} products)")
                    endpoints_status['products'] = True
                    print(f"✅ Products Endpoint: ONLINE ({num_products} products)")
                else:
                    self.endpoint_products_var.set("📈 Products: 🔴 OFFLINE")
                    endpoints_status['products'] = False
                    all_online = False
                    print("❌ Products Endpoint: OFFLINE")
            except Exception as e:
                self.endpoint_products_var.set("📈 Products: 🔴 OFFLINE")
                endpoints_status['products'] = False
                all_online = False
                print(f"❌ Products Endpoint: OFFLINE - {e}")
            
            # Final status
            online_count = sum(endpoints_status.values())
            total_count = len(endpoints_status)
            
            if all_online:
                self.test_result_var.set(f"🟢 ALL ENDPOINTS ONLINE ({total_count}/{total_count})")
                self.test_result_label.configure(foreground='green')
                self.api_status_var.set("Coinbase API: ✅ All Endpoints Working")
                print(f"\n✅ All {total_count} endpoints are ONLINE")
                return True
            elif online_count > 0:
                self.test_result_var.set(f"🟡 PARTIAL ({online_count}/{total_count} endpoints online)")
                self.test_result_label.configure(foreground='orange')
                self.api_status_var.set(f"Coinbase API: ⚠️ {online_count}/{total_count} Endpoints Working")
                print(f"\n⚠️ {online_count}/{total_count} endpoints are online")
                return False
            else:
                self.test_result_var.set(f"🔴 ALL ENDPOINTS OFFLINE (0/{total_count})")
                self.test_result_label.configure(foreground='red')
                self.api_status_var.set("Coinbase API: ❌ All Endpoints Failed")
                print(f"\n❌ All {total_count} endpoints are OFFLINE")
                return False
                
        except Exception as e:
            print(f"❌ API Connection Test Failed: {e}")
            self.test_result_var.set(f"🔴 TEST FAILED")
            self.test_result_label.configure(foreground='red')
            self.api_status_var.set("Coinbase API: ❌ Test Failed")
            return False
        
    def toggle_auto_buy(self):
        """Enable/disable auto buy - AUTO-CALCULATES PRICE"""
        self.auto_buy_enabled = self.autobuy_enabled_var.get()
        
        if self.auto_buy_enabled:
            try:
                # AUTO-CALCULATE: Set to current price - 1% (buy on dip)
                if self.current_price > 0:
                    # Strategy: Buy 1% below current price for safety
                    auto_price = self.current_price * 0.99  # -1%
                    self.autobuy_price_var.set(f"{auto_price:.2f}")
                    self.auto_buy_price = auto_price
                    
                    print(f"\n🤖 Auto Buy ENABLED:")
                    print(f"   Current Price: ${self.current_price:,.2f}")
                    print(f"   Auto Buy Price: ${auto_price:,.2f} (-1% safety margin)")
                    print(f"   💡 Strategy: Buy when price dips 1% below current")
                else:
                    # Fallback: use manual input
                    self.auto_buy_price = float(self.autobuy_price_var.get())
                    if self.auto_buy_price <= 0:
                        raise ValueError("Price must be positive")
                    print(f"\n🤖 Auto Buy ENABLED at ${self.auto_buy_price:,.2f} (manual price)")
                
                self.autobuy_status_var.set(f"🟢 Auto Buy: ACTIVE at ${self.auto_buy_price:,.2f}")
                self.autobuy_price_entry.configure(state='disabled')
                
            except ValueError as e:
                self.autobuy_enabled_var.set(False)
                self.auto_buy_enabled = False
                self.autobuy_status_var.set("⚪ Auto Buy: Disabled")
                print(f"\n❌ Invalid auto buy price: {e}")
        else:
            self.autobuy_status_var.set("⚪ Auto Buy: Disabled")
            self.autobuy_price_entry.configure(state='normal')
            self.auto_buy_executed = False
            print("\n⚪ Auto Buy DISABLED")
    
    def set_autobuy_current_minus(self):
        """Set auto buy price to current price - 1%"""
        if self.current_price > 0:
            trigger_price = self.current_price * 0.99  # -1%
            self.autobuy_price_var.set(f"{trigger_price:.2f}")
            print(f"\n✓ Auto Buy price set to ${trigger_price:,.2f} (Current -1%)")
        else:
            print("\n❌ Waiting for price data...")
    
    def toggle_auto_sell(self):
        """Enable/disable auto sell - AUTO-CALCULATES TARGET PRICE WITH PERFECT HARMONY"""
        self.auto_sell_enabled = self.autosell_enabled_var.get()
        
        if self.auto_sell_enabled:
            try:
                # PRIORITY 1: If we have an open position, use actual buy price
                if self.last_buy_price > 0 and self.balance_btc > 0:
                    # Strategy: Calculate price needed for 2.5% net profit after fees
                    # Target formula: (Position × 1.025) / (1 - sell_fee) / btc_qty
                    desired_net = self.position_size * (1 + self.profit_rate)
                    required_gross = desired_net / (1 - self.sell_fee_rate)
                    target_price = required_gross / self.balance_btc
                    
                    self.autosell_price_var.set(f"{target_price:.2f}")
                    self.auto_sell_price = target_price
                    
                    # Calculate actual percentages
                    price_increase_pct = ((target_price - self.last_buy_price) / self.last_buy_price) * 100
                    
                    print(f"\n🤖 Auto Sell ENABLED:")
                    print(f"   Entry Price: ${self.last_buy_price:,.2f}")
                    print(f"   Target Price: ${target_price:,.2f} (+{price_increase_pct:.2f}%)")
                    print(f"   Expected Net Profit: ${self.position_size * self.profit_rate:.2f} ({self.profit_rate*100}%)")
                    print(f"   💡 Strategy: Sell at calculated target for {self.profit_rate*100}% profit")
                
                # PRIORITY 2: If Auto Buy is active, calculate from Auto Buy price (HARMONY!)
                elif self.auto_buy_enabled and self.auto_buy_price > 0:
                    # Perfect harmony: Use Auto Buy price as entry for calculations
                    entry_price = self.auto_buy_price
                    
                    # Calculate BTC that will be received at auto buy price
                    net_investment = self.position_size * (1 - self.buy_fee_rate)
                    btc_to_receive = net_investment / entry_price
                    
                    # Calculate target for 2.5% profit
                    desired_net = self.position_size * (1 + self.profit_rate)
                    required_gross = desired_net / (1 - self.sell_fee_rate)
                    target_price = required_gross / btc_to_receive
                    
                    self.autosell_price_var.set(f"{target_price:.2f}")
                    self.auto_sell_price = target_price
                    
                    # Calculate percentages
                    price_increase_pct = ((target_price - entry_price) / entry_price) * 100
                    
                    print(f"\n🤖 Auto Sell ENABLED (HARMONIZED with Auto Buy):")
                    print(f"   Auto Buy Price: ${entry_price:,.2f}")
                    print(f"   Auto Sell Target: ${target_price:,.2f} (+{price_increase_pct:.2f}%)")
                    print(f"   Expected Net Profit: ${self.position_size * self.profit_rate:.2f} ({self.profit_rate*100}%)")
                    print(f"   ✅ PERFECT HARMONY: Buy @ ${entry_price:,.2f} → Sell @ ${target_price:,.2f}")
                    print(f"   💡 Guaranteed {self.profit_rate*100}% profit when both execute")
                
                # PRIORITY 3: No position, no auto buy, use current price as reference
                elif self.current_price > 0:
                    estimated_target = self.current_price * (1 + self.profit_rate + self.buy_fee_rate + self.sell_fee_rate)
                    self.autosell_price_var.set(f"{estimated_target:.2f}")
                    self.auto_sell_price = estimated_target
                    
                    print(f"\n🤖 Auto Sell ENABLED:")
                    print(f"   Current Price: ${self.current_price:,.2f}")
                    print(f"   Estimated Target: ${estimated_target:,.2f}")
                    print(f"   ⚠️ Will recalculate exact target after buy")
                else:
                    # Fallback: use manual input
                    price_str = self.autosell_price_var.get().replace(',', '').replace('$', '')
                    self.auto_sell_price = float(price_str)
                    if self.auto_sell_price <= 0:
                        raise ValueError("Price must be positive")
                    print(f"\n🤖 Auto Sell ENABLED at ${self.auto_sell_price:,.2f} (manual price)")
                
                self.autosell_status_var.set(f"🟢 Auto Sell: ACTIVE at ${self.auto_sell_price:,.2f}")
                self.autosell_price_entry.configure(state='disabled')
                
            except ValueError as e:
                self.autosell_enabled_var.set(False)
                self.auto_sell_enabled = False
                self.autosell_status_var.set("⚪ Auto Sell: Disabled")
                print(f"\n❌ Invalid auto sell price: {e}")
        else:
            self.autosell_status_var.set("⚪ Auto Sell: Disabled")
            self.autosell_price_entry.configure(state='normal')
            print("\n⚪ Auto Sell DISABLED")
    
    def set_autosell_target(self):
        """Set auto sell price to calculated target price"""
        if hasattr(self, 'target_price_var'):
            target_str = self.target_price_var.get().replace('$', '').replace(',', '')
            try:
                target_price = float(target_str)
                self.autosell_price_var.set(f"{target_price:.2f}")
                print(f"\n✓ Auto Sell price set to ${target_price:,.2f} (Target Price)")
            except:
                print("\n❌ No target price available")
        else:
            print("\n❌ No target price calculated yet")
    
    def update_autosell_current_target(self):
        """Update auto sell price with current calculated target (recalculates on click)"""
        if self.current_price > 0:
            # Calculate target using CORRECT formula (same as manual mode)
            if self.last_buy_price > 0 and self.balance_btc > 0:
                # Calculate from cost basis
                cost_basis = self.last_buy_price * self.balance_btc
                desired_net = cost_basis * (1 + self.profit_rate)
                required_gross = desired_net / (1 - self.sell_fee_rate)
                target_price = required_gross / self.balance_btc
                
                self.autosell_price_var.set(f"{target_price:.2f}")
                
                # If auto sell is enabled, update the trigger price
                if self.auto_sell_enabled:
                    self.auto_sell_price = target_price
                    self.autosell_status_var.set(f"🟢 Auto Sell: ACTIVE at ${target_price:,.2f}")
                
                print(f"\n🔄 Auto Sell price UPDATED:")
                print(f"   Entry: ${self.last_buy_price:,.2f}")
                print(f"   Target: ${target_price:,.2f} (+{self.profit_rate*100:.1f}%)")
                print(f"   Cost: ${cost_basis:.2f} → Net: ${desired_net:.2f}")
                print(f"   Sell Fee: ${required_gross*self.sell_fee_rate:.2f}")
            else:
                # Use regular target price
                self.set_autosell_target()
        else:
            print("\n❌ Waiting for price data...")
    
    def apply_settings(self):
        """Apply new trading settings"""
        try:
            # Get new values (Position Size is now auto-calculated from balance)
            new_profit = float(self.profit_var.get())
            new_stop = float(self.stop_var.get())
            new_rebuy_drop = float(self.rebuy_drop_var.get())
            
            # Validate values
            if new_profit <= 0 or new_stop <= 0 or new_rebuy_drop <= 0:
                raise ValueError("All values must be positive")
            
            # Apply new values
            # position_size is auto-calculated from balance, not from user input
            self.profit_rate = new_profit / 100  # Convert to decimal
            self.stop_loss = new_stop
            self.rebuy_drop = new_rebuy_drop
            self.auto_mode = self.auto_var.get()
            self.dry_run = self.dryrun_var.get()
            
            # SYNC: Update Configuration tab value to match Trading tab
            self.config_profit_var.set(f"{new_profit:.1f}")
            
            # Note: Entry price is NOT updated from settings
            # It should only change when user manually changes it or uses "Use Current"
            
            mode_str = "AUTO" if self.auto_mode else "MANUAL"
            run_str = "DRY RUN" if self.dry_run else "LIVE"
            
            print(f"\n⚙️  Settings Updated:")
            print(f"Position Size: ${self.position_size:.2f} (auto from balance)")
            print(f"Net Profit Target: {self.profit_rate*100:.1f}%")
            print(f"Stop Loss: {self.stop_loss:.1f}%")
            print(f"Rebuy Drop: {self.rebuy_drop:.1f}% (for auto-loop)")
            print(f"Mode: {mode_str} | {run_str}")
            
            # Update display
            self.check_position()
            
        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
            
    def update_price(self):
        """Update BTC price and check trading conditions (REST API fallback)"""
        last_error_time = 0
        error_count = 0
        consecutive_errors = 0
        
        while self.is_running:
            try:
                # If WebSocket is active and working, reduce REST frequency
                if self.websocket_feed and self.websocket_feed.is_connected:
                    time.sleep(5)  # Only check every 5 seconds as fallback
                    continue
                
                # Measure REST API latency
                start_time = time.time()
                
                # Get price from Coinbase API
                response = requests.get(
                    'https://api.coinbase.com/v2/prices/BTC-USD/spot',
                    timeout=10
                )
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'amount' in data['data']:
                        self.current_price = float(data['data']['amount'])
                        self.rest_latency_ms = latency_ms
                        
                        # Only update UI if WebSocket is not active
                        if not (self.websocket_feed and self.websocket_feed.is_connected):
                            self.price_var.set(f"${self.current_price:,.2f}")
                            
                            # Update test tab price display
                            if hasattr(self, 'test_price_var'):
                                self.test_price_var.set(f"${self.current_price:,.2f}")
                            
                            # Update timestamp
                            current_time = datetime.now()
                            self.last_update_var.set(
                                f"Updated: {current_time.strftime('%H:%M:%S.%f')[:-3]}"
                            )
                            
                            # Update latency display
                            self.latency_var.set(f"📱 Latency: {latency_ms}ms | Source: REST API")
                            
                            # Update connection status indicator
                            if hasattr(self, 'price_status_var'):
                                self.price_status_var.set("✅ REST API Conectado")
                        
                        # Connection successful
                        error_count = 0
                        consecutive_errors = 0
                        self.price_connection_ok = True
                        self.last_price_error = None
                        
                        # Check triggers only if WebSocket is not handling it
                        if not (self.websocket_feed and self.websocket_feed.is_connected):
                            self.check_auto_triggers()
                    else:
                        raise ValueError("Invalid response format")
                else:
                    raise requests.RequestException(f"Status: {response.status_code}")
                        
            except (requests.RequestException, ValueError) as e:
                current_time = time.time()
                error_count += 1
                consecutive_errors += 1
                
                # Update connection status
                self.price_connection_ok = False
                self.last_price_error = str(e)
                
                # After 3 consecutive errors, show "Sin Conexión" in GUI
                if consecutive_errors >= 3:
                    self.price_var.set("❌ Sin Conexión")
                    self.last_update_var.set("❌ No se puede conectar a Coinbase")
                    if hasattr(self, 'price_status_var'):
                        self.price_status_var.set("❌ Sin Conexión a Coinbase")
                
                if current_time - last_error_time >= 5:
                    print(f"\n❌ Price error: {str(e)}")
                    if error_count > 5:
                        print("   ⚠️  Verifique su conexión a internet")
                    last_error_time = current_time
            
            finally:
                time.sleep(0.1)  # Update every 100ms (10 times per second)
            
    def check_position(self):
        """Check current position and update profit table"""
        try:
            if self.current_price <= 0:
                return
            
            if self.balance_btc > 0:
                # Active position - use CORRECT formula
                btc_amount = self.balance_btc
                position_value = btc_amount * self.current_price
                
                # KEY: Check if using real balance from Coinbase
                if self.using_real_balance:
                    # REAL COINBASE BALANCE - Always use actual BTC value
                    if self.last_buy_price > 0:
                        # Manual entry price was set
                        entry_price = self.last_buy_price
                        cost_basis = btc_amount * entry_price
                    else:
                        # No entry price yet - use current value
                        entry_price = self.current_price
                        cost_basis = position_value
                    
                    # Display real balance values
                    # Calculate estimated buy fee from cost basis
                    buy_fee = cost_basis * self.buy_fee_rate
                    net_investment = cost_basis - buy_fee
                    
                    self.amount_labels['Initial Investment:'].configure(text=f'${cost_basis:,.2f}')
                    self.amount_labels['Buy Fee (0.6%):'].configure(text=f'${buy_fee:,.2f}')
                    self.amount_labels['Actual BTC Purchase:'].configure(text=f'${net_investment:,.2f}')
                else:
                    # NORMAL TRADING SCENARIO (bought through app)
                    if self.last_buy_price > 0:
                        entry_price = self.last_buy_price
                        cost_basis = self.position_size
                        buy_fee = cost_basis * self.buy_fee_rate
                        net_investment = cost_basis - buy_fee
                        
                        # Display trading values
                        self.amount_labels['Initial Investment:'].configure(text=f'${cost_basis:,.2f}')
                        self.amount_labels['Buy Fee (0.6%):'].configure(text=f'${buy_fee:,.2f}')
                        self.amount_labels['Actual BTC Purchase:'].configure(text=f'${net_investment:,.2f}')
                    else:
                        # No entry price
                        entry_price = self.current_price
                        cost_basis = position_value
                        
                        # Calculate estimated buy fee from cost basis
                        buy_fee = cost_basis * self.buy_fee_rate
                        net_investment = cost_basis - buy_fee
                        
                        self.amount_labels['Initial Investment:'].configure(text=f'${cost_basis:,.2f}')
                        self.amount_labels['Buy Fee (0.6%):'].configure(text=f'${buy_fee:,.2f}')
                        self.amount_labels['Actual BTC Purchase:'].configure(text=f'${net_investment:,.2f}')
                
                # Calculate TARGET PRICE using CORRECT formula that guarantees profit
                # Formula: Entry × (1 + (profit_target + total_fees))
                # Example: For 2.5% profit + 1.2% fees = Entry × 1.037
                total_fees_pct = (self.buy_fee_rate + self.sell_fee_rate) * 100  # 1.2%
                gross_profit_needed_pct = (self.profit_rate * 100) + total_fees_pct  # 2.5% + 1.2% = 3.7%
                target_price = entry_price * (1 + gross_profit_needed_pct / 100)
                
                # Calculate STOP LOSS using CORRECT formula that compensates for fees
                # Formula: Entry × (1 - (stop_loss - total_fees))
                # Example: For 1% stop - 1.2% fees = Entry × 0.998
                net_stop_loss_pct = self.stop_loss - total_fees_pct  # 1% - 1.2% = -0.2%
                
                if self.last_buy_price > 0 and self.current_price > entry_price * 1.05:
                    # Profitable position - protect gains from current price
                    stop_price = self.current_price * (1 - self.stop_loss / 100)
                else:
                    # New or losing position - compensate for fees
                    stop_price = entry_price * (1 + net_stop_loss_pct / 100)
                
                # Calculate P/L
                unrealized_pl = position_value - cost_basis
                
                # Avoid division by zero if last_buy_price is 0
                if self.last_buy_price > 0:
                    profit_pct = ((self.current_price - self.last_buy_price) / self.last_buy_price * 100)
                else:
                    # If no entry price recorded, use current position value vs cost basis
                    profit_pct = ((position_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
                
                # Calculate Final Profit using target_price (already calculated above)
                # Gross sell value = BTC amount × target price
                gross_sell_value = btc_amount * target_price
                
                # Sell fee = gross value × sell fee rate
                sell_fee = gross_sell_value * self.sell_fee_rate
                
                # Net proceeds after sell fee
                net_proceeds = gross_sell_value - sell_fee
                
                # CRITICAL: Total cost includes BOTH initial investment AND buy fee
                total_cost = cost_basis + buy_fee
                
                # Final profit = net proceeds - total cost (including buy fee)
                potential_profit = net_proceeds - total_cost
                
                # Value at target (for display) - should be GROSS sell value
                value_at_target = gross_sell_value
                
                # Update display
                self.amount_labels['--- Current Position ---'].configure(text='------------------------')
                self.amount_labels['Current BTC Value:'].configure(text=f'${position_value:,.2f}')
                self.amount_labels['Current P/L (if sold now):'].configure(
                    text=f'${unrealized_pl:+,.2f}',
                    foreground='green' if unrealized_pl > 0 else 'red'
                )
                
                self.amount_labels['--- At Target Price ---'].configure(text='------------------------')
                self.amount_labels['Value at Target:'].configure(text=f'${value_at_target:,.2f}')
                self.amount_labels['Sell Fee (0.6%):'].configure(text=f'${sell_fee:,.2f}')
                self.amount_labels['Final Profit (at target):'].configure(
                    text=f'${potential_profit:+,.2f}',
                    foreground='green' if potential_profit > 0 else 'red'
                )
                
                self.entry_var.set(f"Entry: ${self.last_buy_price:,.2f} | Current: ${self.current_price:,.2f} ({profit_pct:+.2f}%)")
                
                # Update target and stop loss display
                self.target_price_var.set(f"${target_price:,.2f}")
                self.stop_price_var.set(f"${stop_price:,.2f}")
                
                # Show calculation formula
                profit_increase_pct = ((target_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
                stop_decrease_pct = ((stop_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
                
                # Calculate actual factors dynamically
                target_factor = target_price / entry_price if entry_price > 0 else 1
                stop_factor = stop_price / entry_price if entry_price > 0 else 1
                
                self.calc_info_var.set(
                    f"Target = ${entry_price:,.2f} × {target_factor:.3f} = ${target_price:,.2f} (+{profit_increase_pct:.2f}%) | Stop = ${entry_price:,.2f} × {stop_factor:.3f} = ${stop_price:,.2f} ({stop_decrease_pct:+.2f}%)"
                )
                
                # Check sell conditions
                if self.last_buy_price > 0:
                    target_pct_increase = ((target_price - self.last_buy_price) / self.last_buy_price) * 100
                else:
                    target_pct_increase = 0
                
                if self.auto_mode and self.last_buy_price > 0 and profit_pct >= target_pct_increase:
                    print(f"\n🎯 Target reached! Price: ${self.current_price:,.2f} >= ${target_price:,.2f}")
                    self.execute_sell("Take Profit")
                elif self.auto_mode and profit_pct <= -self.stop_loss:
                    print(f"\n🛑 Stop Loss triggered! Price dropped {profit_pct:.2f}%")
                    self.execute_sell("Stop Loss")
                
                # Disable buy button when position is open
                if hasattr(self, 'buy_button'):
                    self.buy_button.configure(state='disabled')
            else:
                # No position - show potential trade based on configured entry price
                # Use position_size for potential trade calculations
                initial_investment = self.position_size
                buy_fee = initial_investment * self.buy_fee_rate
                net_investment = initial_investment - buy_fee
                
                # Update display with potential trade values
                self.amount_labels['Initial Investment:'].configure(text=f'${initial_investment:,.2f}')
                self.amount_labels['Buy Fee (0.6%):'].configure(text=f'${buy_fee:,.2f}')
                self.amount_labels['Actual BTC Purchase:'].configure(text=f'${net_investment:,.2f}')
                
                # Use current price for calculations (no manual entry field)
                configured_entry = self.current_price
                
                if configured_entry <= 0:
                    configured_entry = self.current_price
                
                # Use configured entry price for calculations with CORRECT formula
                btc_amount = net_investment / configured_entry
                current_value = btc_amount * self.current_price
                
                # Apply CORRECT formula for target price
                desired_net_proceeds = initial_investment * (1 + self.profit_rate)
                required_gross_proceeds = desired_net_proceeds / (1 - self.sell_fee_rate)
                target_price = required_gross_proceeds / btc_amount
                
                gross_sell_value = btc_amount * target_price
                sell_fee = gross_sell_value * self.sell_fee_rate
                net_sell_value = gross_sell_value - sell_fee
                potential_profit = net_sell_value - initial_investment
                
                self.amount_labels['--- Current Position ---'].configure(text='------------------------')
                self.amount_labels['Current BTC Value:'].configure(text=f'${current_value:,.2f}')
                self.amount_labels['Current P/L (if sold now):'].configure(text='No Position')
                
                self.amount_labels['--- At Target Price ---'].configure(text='------------------------')
                self.amount_labels['Value at Target:'].configure(text=f'${gross_sell_value:,.2f}')
                self.amount_labels['Sell Fee (0.6%):'].configure(text=f'${sell_fee:,.2f}')
                self.amount_labels['Final Profit (at target):'].configure(
                    text=f'${potential_profit:+,.2f}',
                    foreground='green' if potential_profit > 0 else 'red'
                )
                
                self.entry_var.set(f"No Position - Entry will be: ${configured_entry:,.2f}")
                
                # Update target and stop loss for potential trade
                stop_price = configured_entry * (1 - self.stop_loss / 100)
                self.target_price_var.set(f"${target_price:,.2f}")
                self.stop_price_var.set(f"${stop_price:,.2f}")
                
                # Enable buy button when no position
                if hasattr(self, 'buy_button'):
                    self.buy_button.configure(state='normal')
                
                # Show CORRECT calculation breakdown
                self.calc_info_var.set(
                    f"Target = [${initial_investment:.2f} × 1.{self.profit_rate*100:.0f}] / (1 - 0.{self.sell_fee_rate*1000:.0f}) / {btc_amount:.8f} BTC = ${target_price:,.2f}"
                )
                
        except Exception as e:
            print(f"❌ Calculation error: {str(e)}")
            
    def manual_buy(self):
        """Manually execute buy order"""
        if self.balance_btc > 0:
            print("\n❌ Already have an open position! Close it first.")
            # Show UI notification
            if hasattr(self, 'balance_status_var'):
                self.balance_status_var.set("❌ Ya tienes una posición abierta")
            return
        
        if self.balance_usd < self.position_size:
            print(f"\n❌ FONDOS INSUFICIENTES")
            print(f"   Necesitas: ${self.position_size:.2f} USD")
            print(f"   Disponible: ${self.balance_usd:.2f} USD")
            print(f"   Faltante: ${self.position_size - self.balance_usd:.2f} USD")
            print(f"\n💡 Solución: Cambia 'Default Position Size' en Configuration a máximo ${self.balance_usd:.2f}")
            
            # Show UI notification
            if hasattr(self, 'balance_status_var'):
                self.balance_status_var.set(
                    f"❌ Fondos Insuficientes | Disponible: ${self.balance_usd:.2f} | Necesitas: ${self.position_size:.2f}"
                )
            return
            
        self.execute_buy()
    
    def export_html_report(self):
        """Export trading report to HTML"""
        try:
            from datetime import datetime
            import os
            import webbrowser
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"btc_trading_report_{timestamp}.html"
            
            # Export to HTML
            print(f"\n📊 Generating HTML report...")
            success = self.db.export_to_html(filename)
            
            if success:
                # Get absolute path
                abs_path = os.path.abspath(filename)
                print(f"✅ Report saved: {abs_path}")
                
                # Ask user if they want to open the report
                try:
                    import tkinter.messagebox as messagebox
                    result = messagebox.askyesno(
                        "Report Generated",
                        f"HTML report generated successfully!\n\n"
                        f"File: {filename}\n\n"
                        f"Would you like to open it now?"
                    )
                    
                    if result:
                        webbrowser.open(f'file://{abs_path}')
                        print(f"🌐 Opening report in browser...")
                except Exception as e:
                    print(f"⚠️ Could not prompt to open file: {e}")
            else:
                print(f"❌ Failed to generate report")
                
        except Exception as e:
            print(f"❌ Error exporting report: {e}")
            import traceback
            traceback.print_exc()
    
    def execute_buy(self):
        """Execute buy order"""
        try:
            # Use current market price as entry
            entry_price = self.current_price
            
            if entry_price <= 0:
                print("\n❌ Invalid entry price - no price data available")
                return
            
            # Validate minimum position size
            if self.position_size < self.min_position_size:
                print(f"\n❌ Position size too small! Minimum is ${self.min_position_size:.2f}")
                print(f"   Current: ${self.position_size:.2f}")
                print(f"   Please adjust in Configuration tab")
                return
            
            # Calculate buy using CORRECT formula
            buy_fee = self.position_size * self.buy_fee_rate
            net_investment = self.position_size - buy_fee
            btc_amount = net_investment / entry_price
            
            # Validate balance (CRITICAL - prevent overdraft)
            if self.position_size > self.balance_usd:
                print(f"\n❌ FONDOS INSUFICIENTES EN COINBASE")
                print(f"   Intentando comprar: ${self.position_size:.2f} USD")
                print(f"   Balance disponible: ${self.balance_usd:.2f} USD")
                print(f"   Faltante: ${self.position_size - self.balance_usd:.2f} USD")
                print(f"\n💡 SOLUCIÓN:")
                print(f"   1. Ve a Configuration tab")
                print(f"   2. Cambia 'Default Position Size ($)' a ${self.balance_usd:.2f} o menos")
                print(f"   3. O deposita más fondos en Coinbase")
                
                # Show UI notification
                if hasattr(self, 'balance_status_var'):
                    self.balance_status_var.set(
                        f"❌ FONDOS INSUFICIENTES | Disponible: ${self.balance_usd:.2f} | Intentando: ${self.position_size:.2f}"
                    )
                return
            
            # FASE 3: Validate price before execution
            print(f"\n🔍 Validating price before buy order...")
            is_valid, validated_price, error_msg = self.validate_price_before_execution(entry_price, "BUY")
            
            if not is_valid:
                print(error_msg)
                print(f"⚠️ BUY ORDER CANCELLED - Price validation failed")
                return
            
            # Use validated price for execution
            entry_price = validated_price
            # Recalculate with validated price
            btc_amount = net_investment / entry_price
            
            # Execute REAL buy order if in LIVE mode
            if not self.dry_run:
                from trading_helpers import TradingHelpers
                helpers = TradingHelpers()
                
                print(f"\n🔴 EXECUTING REAL BUY ORDER...")
                result = helpers.buy_btc_market(usd_amount=self.position_size)
                
                if not result.get('success'):
                    print(f"\n❌ REAL BUY ORDER FAILED: {result.get('error')}")
                    return
                
                print(f"✅ REAL BUY ORDER EXECUTED: Order ID {result.get('order_id')}")
            
            # Update balances
            self.balance_usd -= self.position_size
            self.balance_btc = btc_amount
            self.last_buy_price = entry_price
            
            # Calculate target price using CORRECT formula
            desired_net = self.position_size * (1 + self.profit_rate)
            required_gross = desired_net / (1 - self.sell_fee_rate)
            target_price = required_gross / btc_amount
            stop_price = entry_price * (1 - self.stop_loss / 100)
            
            # Verification
            expected_net_profit = self.position_size * self.profit_rate
            
            # Save to database
            mode_str = "DRY RUN" if self.dry_run else "LIVE"
            self.db.save_trade(
                trade_type="BUY",
                price=entry_price,
                amount_usd=self.position_size,
                amount_btc=btc_amount,
                fee=buy_fee,
                profit=0,
                mode=mode_str,
                notes=f"Auto buy" if self.auto_buy_enabled else "Manual buy"
            )
            
            # Save session (open position)
            self.db.save_session(
                last_buy_price=entry_price,
                position_size=self.position_size,
                btc_amount=btc_amount,
                target_price=target_price,
                stop_loss=stop_price
            )
            
            mode_indicator = " [DRY RUN]" if self.dry_run else " [LIVE]"
            print(f"\n✓ BUY EXECUTED{mode_indicator}:")
            print(f"   Entry Price: ${entry_price:,.2f}")
            print(f"   Position: ${self.position_size:.2f}")
            print(f"   Buy Fee ({self.buy_fee_rate*100}%): ${buy_fee:.2f}")
            print(f"   Net Investment: ${net_investment:.2f}")
            print(f"   BTC Qty: {btc_amount:.8f}")
            print(f"\n   🎯 TARGET PRICE: ${target_price:,.2f}")
            print(f"      Formula: [${self.position_size:.2f} × (1 + {self.profit_rate*100}%)] / (1 - {self.sell_fee_rate*100}%) / {btc_amount:.8f}")
            print(f"      Expected Net Profit: ${expected_net_profit:.2f}")
            print(f"\n   🛑 STOP LOSS: ${stop_price:,.2f} (-{self.stop_loss}%)")
            
            self.balance_var.set(f"USD: ${self.balance_usd:.2f}\nBTC: {self.balance_btc:.8f}")
            self.check_position()
            
            # Disable buy button and entry price field during active position
            self.buy_button.configure(state='disabled')
            if hasattr(self, 'entry_price_entry'):
                self.entry_price_entry.configure(state='disabled')
            
            # AUTO-LOOP: Calculate sell target and activate Auto Sell
            if self.auto_mode or self.auto_sell_enabled:
                # Calculate sell target price from current entry
                profit_target_pct = self.profit_rate * 100
                buy_fee_pct = self.buy_fee_rate * 100
                sell_fee_pct = self.sell_fee_rate * 100
                
                # Target = Entry × (1 + Profit% + Buy Fee% + Sell Fee%)
                auto_sell_target = entry_price * (1 + (profit_target_pct + buy_fee_pct + sell_fee_pct) / 100)
                
                # Activate Auto Sell at the target price
                self.auto_sell_price = auto_sell_target
                self.autosell_price_var.set(f"{auto_sell_target:.2f}")
                self.auto_sell_enabled = True
                self.autosell_enabled_var.set(True)
                self.autosell_status_var.set(f"🟢 Auto Sell: ACTIVE at ${auto_sell_target:,.2f}")
                self.autosell_price_entry.configure(state='disabled')
                
                print(f"\n🔄 AUTO-LOOP ACTIVATED:")
                print(f"   Bought at: ${entry_price:,.2f}")
                print(f"   Target price: ${auto_sell_target:,.2f} (+{profit_target_pct + buy_fee_pct + sell_fee_pct:.1f}%)")
                print(f"   🤖 Auto Sell ENABLED - Waiting for target")
            
        except Exception as e:
            print(f"❌ Buy error: {str(e)}")
            
    def execute_sell(self, reason: str):
        """Execute sell order"""
        try:
            # CRITICAL: Validate BTC balance before attempting to sell
            if self.balance_btc <= 0:
                print(f"\n❌ NO TIENES BTC PARA VENDER")
                print(f"   Balance BTC: {self.balance_btc:.8f} BTC")
                print(f"   Balance USD: ${self.balance_usd:.2f}")
                print(f"\n💡 SOLUCIÓN: Primero debes comprar BTC antes de poder vender")
                
                # Show UI notification
                if hasattr(self, 'balance_status_var'):
                    self.balance_status_var.set(
                        f"❌ No tienes BTC para vender | Balance: {self.balance_btc:.8f} BTC"
                    )
                return
            
            # Additional validation: Check if balance matches Coinbase (if using real balance)
            if self.using_real_balance:
                # Refresh balance from Coinbase to ensure accuracy
                try:
                    print(f"\n🔄 Verificando balance en Coinbase...")
                    accounts = self.api.list_accounts()
                    coinbase_btc = 0.0
                    
                    for account in accounts.get('accounts', []):
                        if account.get('currency') == 'BTC':
                            coinbase_btc = float(account.get('available_balance', {}).get('value', 0))
                            break
                    
                    if coinbase_btc < self.balance_btc:
                        print(f"\n❌ BALANCE BTC INSUFICIENTE EN COINBASE")
                        print(f"   Intentando vender: {self.balance_btc:.8f} BTC")
                        print(f"   Disponible en Coinbase: {coinbase_btc:.8f} BTC")
                        print(f"   Faltante: {self.balance_btc - coinbase_btc:.8f} BTC")
                        print(f"\n💡 NOTA: El balance local no coincide con Coinbase")
                        print(f"   Ajustando venta a balance real de Coinbase: {coinbase_btc:.8f} BTC")
                        
                        # Update local balance to match Coinbase
                        self.balance_btc = coinbase_btc
                        
                        if coinbase_btc <= 0:
                            print(f"\n❌ NO PUEDES VENDER: Balance real en Coinbase es 0 BTC")
                            if hasattr(self, 'balance_status_var'):
                                self.balance_status_var.set(
                                    f"❌ Balance en Coinbase: 0 BTC | No puedes vender"
                                )
                            return
                    else:
                        print(f"✅ Balance verificado: {coinbase_btc:.8f} BTC disponible en Coinbase")
                        
                except Exception as e:
                    print(f"⚠️ No se pudo verificar balance en Coinbase: {e}")
                    print(f"   Continuando con balance local: {self.balance_btc:.8f} BTC")
            
            # FASE 3: Validate price before execution
            print(f"\n🔍 Validating price before sell order...")
            is_valid, validated_price, error_msg = self.validate_price_before_execution(self.current_price, "SELL")
            
            if not is_valid:
                print(error_msg)
                print(f"⚠️ SELL ORDER CANCELLED - Price validation failed")
                return
            
            # Use validated price
            sell_price = validated_price
            
            # Calculate sell
            btc_qty = self.balance_btc  # Store before clearing
            gross_proceeds = btc_qty * sell_price
            sell_fee = gross_proceeds * self.sell_fee_rate
            net_proceeds = gross_proceeds - sell_fee
            
            # Calculate profit
            cost_basis = self.position_size
            net_profit = net_proceeds - cost_basis
            profit_pct = (net_profit / cost_basis) * 100
            
            # Execute REAL sell order if in LIVE mode
            if not self.dry_run:
                from trading_helpers import TradingHelpers
                helpers = TradingHelpers()
                
                print(f"\n🔴 EXECUTING REAL SELL ORDER...")
                result = helpers.sell_btc_market(btc_amount=btc_qty)
                
                if not result.get('success'):
                    print(f"\n❌ REAL SELL ORDER FAILED: {result.get('error')}")
                    return
                
                print(f"✅ REAL SELL ORDER EXECUTED: Order ID {result.get('order_id')}")
            
            self.trades_count += 1
            if net_profit > 0:
                self.winning_trades += 1
            self.total_profit += net_profit
            
            self.balance_usd += net_proceeds
            self.balance_btc = 0
            self.last_buy_price = 0
            
            # Save to database
            mode_str = "DRY RUN" if self.dry_run else "LIVE"
            self.db.save_trade(
                trade_type="SELL",
                price=sell_price,
                amount_usd=net_proceeds,
                amount_btc=btc_qty,
                fee=sell_fee,
                profit=net_profit,
                mode=mode_str,
                notes=f"{reason}"
            )
            
            # Close session (position closed)
            self.db.close_session()
            
            mode_indicator = " [DRY RUN]" if self.dry_run else " [LIVE]"
            print(f"\n✓ SELL EXECUTED ({reason}){mode_indicator}:")
            print(f"   Sale Price: ${sell_price:,.2f}")
            print(f"   BTC Qty: {btc_qty:.8f}")
            print(f"   Gross Value: ${gross_proceeds:.2f}")
            print(f"   Sell Fee ({self.sell_fee_rate*100}%): ${sell_fee:.2f}")
            print(f"   Net Proceeds: ${net_proceeds:.2f}")
            print(f"   Cost Basis: ${cost_basis:.2f}")
            print(f"   Net Profit/Loss: ${net_profit:+.2f} ({profit_pct:+.2f}%)")
            
            self.balance_var.set(f"USD: ${self.balance_usd:.2f}\nBTC: {self.balance_btc:.8f}")
            self.update_statistics()
            self.check_position()
            
            # Re-enable buy button and entry price field after selling
            if self.is_running:
                self.buy_button.configure(state='normal')
            if hasattr(self, 'entry_price_entry'):
                self.entry_price_entry.configure(state='normal')
            
            # Reset auto buy flag so it can trigger again
            self.auto_buy_executed = False
            
            # AUTO-LOOP: Calculate rebuy price and activate Auto Buy
            if self.auto_mode or self.auto_buy_enabled:
                # Calculate rebuy price: Sell price - X% (to profit on the cycle)
                # Use configurable rebuy drop %
                rebuy_drop_pct = self.rebuy_drop
                rebuy_price = sell_price * (1 - rebuy_drop_pct / 100)
                
                # Activate Auto Buy at the rebuy price
                self.auto_buy_price = rebuy_price
                self.autobuy_price_var.set(f"{rebuy_price:.2f}")
                self.auto_buy_enabled = True
                self.autobuy_enabled_var.set(True)
                self.autobuy_status_var.set(f"🟢 Auto Buy: ACTIVE at ${rebuy_price:,.2f}")
                self.autobuy_price_entry.configure(state='disabled')
                
                print(f"\n🔄 AUTO-LOOP ACTIVATED:")
                print(f"   Sold at: ${self.current_price:,.2f}")
                print(f"   Rebuy price: ${rebuy_price:,.2f} (-{rebuy_drop_pct}%)")
                print(f"   🤖 Auto Buy ENABLED - Waiting for price to drop")
            elif self.auto_buy_enabled:
                print(f"\n🤖 Auto Buy re-armed: Will buy again when price drops to ${self.auto_buy_price:,.2f}")
            
        except Exception as e:
            print(f"❌ Sell error: {str(e)}")
            
    def update_statistics(self):
        """Update trading statistics"""
        win_rate = (self.winning_trades / self.trades_count * 100) if self.trades_count > 0 else 0
        roi = ((self.balance_usd - 1000) / 1000 * 100)
        
        self.stats_var.set(
            f"Trades: {self.trades_count} | Win: {win_rate:.1f}% | "
            f"Profit: ${self.total_profit:.2f} | ROI: {roi:+.2f}%"
        )
        
        # Save to database
        self.db.save_statistics(
            total_trades=self.trades_count,
            winning_trades=self.winning_trades,
            total_profit=self.total_profit,
            win_rate=win_rate,
            roi=roi
        )
        
    def on_websocket_price(self, price, latency_ms):
        """Callback for WebSocket price updates"""
        try:
            self.current_price = price
            self.websocket_latency_ms = latency_ms
            self.last_price_update_time = time.time()  # Track price freshness
            self.price_var.set(f"${self.current_price:,.2f}")
            
            # Update test tab price display
            if hasattr(self, 'test_price_var'):
                self.test_price_var.set(f"${self.current_price:,.2f}")
            
            # Update timestamp
            current_time = datetime.now()
            self.last_update_var.set(
                f"Updated: {current_time.strftime('%H:%M:%S.%f')[:-3]}"
            )
            
            # Update latency display
            self.latency_var.set(f"📡 Latency: {latency_ms}ms | Source: WebSocket ⚡")
            
            # Update connection status
            self.price_connection_ok = True
            self.price_status_var.set("✅ WebSocket Conectado")
            
            # Check auto buy/sell triggers
            self.check_auto_triggers()
            
        except Exception as e:
            print(f"❌ Error processing WebSocket price: {e}")
    
    def on_websocket_error(self, error):
        """Callback for WebSocket errors"""
        print(f"⚠️ WebSocket error: {error}")
        # Will fallback to REST automatically
    
    def is_price_stale(self):
        """Check if current price data is too old"""
        if self.last_price_update_time == 0:
            return True
        age = time.time() - self.last_price_update_time
        return age > self.max_price_age_seconds
    
    def get_fresh_price(self):
        """Get a fresh price reading, return (price, success, error_message)"""
        try:
            # Check if WebSocket price is fresh
            if self.websocket_feed and self.websocket_feed.is_connected:
                if not self.websocket_feed.is_price_stale(max_age_seconds=self.max_price_age_seconds):
                    price = self.websocket_feed.get_price()
                    if price > 0:
                        self.last_price_update_time = time.time()
                        return (price, True, None)
            
            # Fallback to REST API
            print("   📱 Getting fresh price from REST API...")
            start_time = time.time()
            response = requests.get(
                'https://api.coinbase.com/v2/prices/BTC-USD/spot',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'amount' in data['data']:
                    price = float(data['data']['amount'])
                    latency_ms = int((time.time() - start_time) * 1000)
                    self.last_price_update_time = time.time()
                    print(f"   ✅ Fresh price: ${price:,.2f} (latency: {latency_ms}ms)")
                    return (price, True, None)
            
            return (0, False, "Failed to get price from API")
            
        except Exception as e:
            return (0, False, f"Error getting fresh price: {str(e)}")
    
    def validate_price_before_execution(self, expected_price, operation_name="order"):
        """
        Validate price before executing an order
        Returns: (is_valid, actual_price, error_message)
        """
        # Get fresh price
        fresh_price, success, error = self.get_fresh_price()
        
        if not success:
            return (False, 0, f"❌ Cannot get fresh price: {error}")
        
        # Calculate price deviation
        price_diff = abs(fresh_price - expected_price)
        price_deviation_pct = (price_diff / expected_price) * 100
        
        # Check if deviation is acceptable
        if price_deviation_pct > self.max_price_deviation_pct:
            return (
                False,
                fresh_price,
                f"❌ Price moved too much! Expected: ${expected_price:,.2f}, "
                f"Actual: ${fresh_price:,.2f} (Δ{price_deviation_pct:+.2f}%)"
            )
        
        # Price is valid
        print(f"   ✅ Price validation passed: ${fresh_price:,.2f} "
              f"(deviation: {price_deviation_pct:.3f}%)")
        return (True, fresh_price, None)
    
    def check_auto_triggers(self):
        """Check auto buy and auto sell triggers"""
        # Check auto buy trigger
        if (self.auto_buy_enabled and 
            not self.auto_buy_executed and 
            self.balance_btc == 0 and
            self.current_price <= self.auto_buy_price):
            
            print(f"\n🤖 AUTO BUY TRIGGERED!")
            print(f"   Current Price: ${self.current_price:,.2f}")
            print(f"   Trigger Price: ${self.auto_buy_price:,.2f}")
            
            # Execute auto buy
            self.auto_buy_executed = True
            self.execute_buy()
            
            # Disable auto buy after execution
            self.autobuy_enabled_var.set(False)
            self.auto_buy_enabled = False
            self.autobuy_status_var.set("⚪ Auto Buy: Disabled (Executed)")
            self.autobuy_price_entry.configure(state='normal')
        
        # Check auto sell trigger
        if (self.auto_sell_enabled and 
            self.balance_btc > 0 and
            self.current_price >= self.auto_sell_price):
            
            print(f"\n🤖 AUTO SELL TRIGGERED!")
            print(f"   Current Price: ${self.current_price:,.2f}")
            print(f"   Trigger Price: ${self.auto_sell_price:,.2f}")
            
            # Execute auto sell
            self.execute_sell("Auto Sell")
            
            # Disable auto sell after execution
            self.autosell_enabled_var.set(False)
            self.auto_sell_enabled = False
            self.autosell_status_var.set("⚪ Auto Sell: Disabled (Executed)")
            self.autosell_price_entry.configure(state='normal')
        
        # Update display
        self.check_position()
    
    def toggle_trading(self):
        """Toggle monitoring on/off"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.start_button.configure(text="Stop Monitoring")
            
            # Start WebSocket for real-time prices
            if self.use_websocket:
                print("\n🚀 Starting WebSocket connection...")
                self.websocket_feed = CoinbaseWebSocketFeed("BTC-USD")
                self.websocket_feed.connect(
                    price_callback=self.on_websocket_price,
                    error_callback=self.on_websocket_error
                )
            
            # Start REST API fallback thread
            self.update_thread = threading.Thread(target=self.update_price)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            # Enable buy button only if we don't have a position
            if self.balance_btc == 0:
                self.buy_button.configure(state='normal')
            
            print("\n📊 Live Monitoring Started")
            print("   🚀 WebSocket: Real-time price updates (<50ms latency)")
            print("   🔄 REST API: Fallback if WebSocket fails")
            print("   💰 Click 'Execute Buy' when ready to open a position")
        else:
            self.start_button.configure(text="Start Monitoring")
            self.buy_button.configure(state='disabled')
            
            # Stop WebSocket
            if self.websocket_feed:
                self.websocket_feed.disconnect()
                self.websocket_feed = None
            
            print("\n⏸️  Monitoring stopped")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BTCTrader()
    app.run()
