import tkinter as tk
from tkinter import ttk
import requests
import threading
import time
from datetime import datetime
import os
from coinbase_complete_api import CoinbaseCompleteAPI
from config import Config

class BTCTrader:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("BTC Trading Strategy - Connected to Coinbase")
        self.root.geometry("600x850")
        
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
        
        # Strategy parameters
        self.profit_rate = 0.015   # 1.5% net profit target
        self.stop_loss = 1.0      # 1.0% stop loss
        self.position_size = 100.0 # $100 per trade
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
        
        # Create GUI elements
        self.create_gui()
        
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
        
    def create_gui(self):
        # Initialize entry_price_var (used internally, not displayed)
        self.entry_price_var = tk.StringVar(value="0")
        
        # Create Notebook (Tab Container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.trading_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.trading_tab, text='📊 Trading')
        self.notebook.add(self.config_tab, text='⚙️ Configuration')
        
        # Create Trading Tab Content
        self.create_trading_tab()
        
        # Create Configuration Tab Content
        self.create_configuration_tab()
        
    def create_trading_tab(self):
        """Create the main trading interface"""
        # Price Display
        price_frame = ttk.LabelFrame(self.trading_tab, text="Live BTC Price", padding="10")
        price_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
            foreground='blue'
        ).pack()
        
        # Trading Settings
        self.settings_frame = ttk.LabelFrame(self.trading_tab, text="Trading Settings", padding="10")
        self.settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Profit target setting
        profit_frame = ttk.Frame(self.settings_frame)
        profit_frame.pack(fill=tk.X, pady=2)
        ttk.Label(profit_frame, text="Profit Target (%):").pack(side=tk.LEFT)
        self.profit_var = tk.StringVar(value="1.5")
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
        
        # Auto Buy Section
        autobuy_frame = ttk.LabelFrame(self.trading_tab, text="🤖 Auto Buy Configuration", padding="10")
        autobuy_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
        
        # Auto Sell Section
        autosell_frame = ttk.LabelFrame(self.trading_tab, text="🤖 Auto Sell Configuration", padding="10")
        autosell_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
        
        # Position Information
        position_frame = ttk.LabelFrame(self.trading_tab, text="Current Position & Profit Calculator", padding="10")
        position_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
            'Initial Investment:',
            'Buy Fee (0.6%):',
            'Actual BTC Purchase:',
            '--- Current Position ---',
            'Current BTC Value:',
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
        
        # Account Information
        account_title = "Account (Real Balance from Coinbase)" if self.using_real_balance else "Account (Mock Balance)"
        account_frame = ttk.LabelFrame(self.trading_tab, text=account_title, padding="10")
        account_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
                foreground='blue'
            ).pack()
        
        # Statistics
        stats_frame = ttk.LabelFrame(self.trading_tab, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
        
    def create_configuration_tab(self):
        """Create the configuration interface"""
        # API Configuration Section
        api_frame = ttk.LabelFrame(self.config_tab, text="🔐 API Configuration", padding="15")
        api_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # API Key
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="API Key:", width=20).pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=self.mask_api_key(Config.COINBASE_API_KEY))
        api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, width=40, show="*")
        api_key_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(key_frame, text="👁️", width=3, command=lambda: self.toggle_visibility(api_key_entry)).pack(side=tk.LEFT)
        
        # API Secret
        secret_frame = ttk.Frame(api_frame)
        secret_frame.pack(fill=tk.X, pady=5)
        ttk.Label(secret_frame, text="API Secret:", width=20).pack(side=tk.LEFT)
        self.api_secret_var = tk.StringVar(value=self.mask_api_key(Config.COINBASE_API_SECRET))
        api_secret_entry = ttk.Entry(secret_frame, textvariable=self.api_secret_var, width=40, show="*")
        api_secret_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(secret_frame, text="👁️", width=3, command=lambda: self.toggle_visibility(api_secret_entry)).pack(side=tk.LEFT)
        
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
        self.config_buy_fee_var = tk.StringVar(value=str(self.buy_fee_rate * 100))
        ttk.Entry(buy_fee_frame, textvariable=self.config_buy_fee_var, width=10).pack(side=tk.LEFT, padx=5)
        
        sell_fee_frame = ttk.Frame(params_frame)
        sell_fee_frame.pack(fill=tk.X, pady=3)
        ttk.Label(sell_fee_frame, text="Sell Fee Rate (%):", width=20).pack(side=tk.LEFT)
        self.config_sell_fee_var = tk.StringVar(value=str(self.sell_fee_rate * 100))
        ttk.Entry(sell_fee_frame, textvariable=self.config_sell_fee_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Position Size
        position_frame = ttk.Frame(params_frame)
        position_frame.pack(fill=tk.X, pady=3)
        ttk.Label(position_frame, text="Default Position Size ($):", width=20).pack(side=tk.LEFT)
        self.config_position_var = tk.StringVar(value=str(self.position_size))
        ttk.Entry(position_frame, textvariable=self.config_position_var, width=10).pack(side=tk.LEFT, padx=5)
        
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
            foreground='blue',
            justify='left'
        ).pack(anchor='w')
    
    def mask_api_key(self, key):
        """Mask API key for display"""
        if not key or len(key) < 8:
            return "Not Set"
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    
    def toggle_visibility(self, entry_widget):
        """Toggle password visibility"""
        if entry_widget.cget('show') == '*':
            entry_widget.configure(show='')
        else:
            entry_widget.configure(show='*')
    
    def save_configuration(self):
        """Save configuration to .env file"""
        try:
            import os
            from pathlib import Path
            
            env_path = Path('.env')
            
            # Read current .env
            env_content = {}
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key.strip()] = value.strip()
            
            # Update values
            api_key = self.api_key_var.get()
            api_secret = self.api_secret_var.get()
            
            if not api_key.startswith('*'):
                env_content['COINBASE_API_KEY'] = api_key
            if not api_secret.startswith('*'):
                env_content['COINBASE_API_SECRET'] = api_secret
            
            env_content['TRADING_MODE'] = self.config_mode_var.get()
            
            # Write back
            with open(env_path, 'w') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
            
            # Update runtime config
            try:
                self.buy_fee_rate = float(self.config_buy_fee_var.get()) / 100
                self.sell_fee_rate = float(self.config_sell_fee_var.get()) / 100
                self.position_size = float(self.config_position_var.get())
            except ValueError:
                pass
            
            print("\n✅ Configuration saved to .env file")
            print("⚠️ Restart the application to apply API changes")
            
        except Exception as e:
            print(f"\n❌ Error saving configuration: {e}")
    
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
        """Test API connection"""
        try:
            print("\n🔄 Testing API connection...")
            
            if not self.api.is_jwt_format:
                print("❌ API not initialized (invalid credentials format)")
                return
            
            # Try to get accounts
            accounts = self.api.list_accounts()
            
            if accounts and 'accounts' in accounts:
                print(f"✅ API Connection Successful!")
                print(f"   Found {len(accounts['accounts'])} accounts")
                
                # Update status
                self.api_status_var.set("Coinbase API: ✅ Connected & Working")
            else:
                print("⚠️ API responded but no accounts found")
                
        except Exception as e:
            print(f"❌ API Connection Failed: {e}")
            self.api_status_var.set("Coinbase API: ❌ Connection Failed")
        
    def toggle_auto_buy(self):
        """Enable/disable auto buy"""
        self.auto_buy_enabled = self.autobuy_enabled_var.get()
        
        if self.auto_buy_enabled:
            try:
                self.auto_buy_price = float(self.autobuy_price_var.get())
                if self.auto_buy_price <= 0:
                    raise ValueError("Price must be positive")
                
                self.autobuy_status_var.set(f"🟢 Auto Buy: ACTIVE at ${self.auto_buy_price:,.2f}")
                self.autobuy_price_entry.configure(state='disabled')
                print(f"\n🤖 Auto Buy ENABLED: Will buy when price drops to ${self.auto_buy_price:,.2f}")
                
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
        """Enable/disable auto sell"""
        self.auto_sell_enabled = self.autosell_enabled_var.get()
        
        if self.auto_sell_enabled:
            try:
                price_str = self.autosell_price_var.get().replace(',', '').replace('$', '')
                self.auto_sell_price = float(price_str)
                if self.auto_sell_price <= 0:
                    raise ValueError("Price must be positive")
                
                self.autosell_status_var.set(f"🟢 Auto Sell: ACTIVE at ${self.auto_sell_price:,.2f}")
                self.autosell_price_entry.configure(state='disabled')
                print(f"\n🤖 Auto Sell ENABLED: Will sell when price reaches ${self.auto_sell_price:,.2f}")
                
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
            # Calculate current target price
            profit_target_pct = self.profit_rate * 100
            sell_fee_pct = self.sell_fee_rate * 100
            
            # Calculate from current price (for active positions)
            if self.last_buy_price > 0 and self.current_price > self.last_buy_price * 1.05:
                # Profitable position - use current price
                current_target = self.current_price * (1 + (profit_target_pct + sell_fee_pct) / 100)
                self.autosell_price_var.set(f"{current_target:.2f}")
                
                # If auto sell is enabled, update the trigger price
                if self.auto_sell_enabled:
                    self.auto_sell_price = current_target
                    self.autosell_status_var.set(f"🟢 Auto Sell: ACTIVE at ${current_target:,.2f}")
                
                print(f"\n🔄 Auto Sell price UPDATED to ${current_target:,.2f}")
                print(f"   Based on Current Price: ${self.current_price:,.2f}")
                print(f"   Profit Target: {profit_target_pct:.1f}% + Sell Fee: {sell_fee_pct:.1f}%")
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
        """Update BTC price and check trading conditions"""
        last_error_time = 0
        error_count = 0
        consecutive_errors = 0
        
        while self.is_running:
            try:
                # Get price from Coinbase API
                response = requests.get(
                    'https://api.coinbase.com/v2/prices/BTC-USD/spot',
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'amount' in data['data']:
                        self.current_price = float(data['data']['amount'])
                        self.price_var.set(f"${self.current_price:,.2f}")
                        
                        # Update timestamp
                        current_time = datetime.now()
                        self.last_update_var.set(
                            f"Updated: {current_time.strftime('%H:%M:%S.%f')[:-3]}"
                        )
                        
                        # Connection successful
                        error_count = 0
                        consecutive_errors = 0
                        self.price_connection_ok = True
                        self.last_price_error = None
                        
                        # Update connection status indicator
                        if hasattr(self, 'price_status_var'):
                            self.price_status_var.set("✅ Conectado a Coinbase")
                        
                        # Check auto buy trigger
                        if (self.auto_buy_enabled and 
                            not self.auto_buy_executed and 
                            self.balance_btc == 0 and
                            self.current_price <= self.auto_buy_price):
                            
                            print(f"\n🤖 AUTO BUY TRIGGERED!")
                            print(f"   Current Price: ${self.current_price:,.2f}")
                            print(f"   Trigger Price: ${self.auto_buy_price:,.2f}")
                            
                            # Execute auto buy (uses current price automatically)
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
                    self.amount_labels['Initial Investment:'].configure(text=f'${cost_basis:,.2f}')
                    self.amount_labels['Buy Fee (0.6%):'].configure(text='$0.00')
                    self.amount_labels['Actual BTC Purchase:'].configure(text=f'${cost_basis:,.2f}')
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
                        self.amount_labels['Initial Investment:'].configure(text=f'${cost_basis:,.2f}')
                        self.amount_labels['Buy Fee (0.6%):'].configure(text='$0.00')
                        self.amount_labels['Actual BTC Purchase:'].configure(text=f'${cost_basis:,.2f}')
                
                # Calculate TARGET PRICE
                profit_target_pct = self.profit_rate * 100  # Convert to percentage
                buy_fee_pct = self.buy_fee_rate * 100       # 0.6%
                sell_fee_pct = self.sell_fee_rate * 100     # 0.6%
                
                # LOGIC CORRECTION: 
                # - For OPEN & PROFITABLE position: Use current price as base
                # - For NEW position: Use entry price as base
                
                if self.last_buy_price > 0 and self.current_price > entry_price * 1.05:
                    # Position is OPEN and PROFITABLE (current > 5% above entry)
                    # Calculate target from CURRENT PRICE (buy fee already paid)
                    # TARGET = Current Price × (1 + Profit Target % + Sell Fee %)
                    target_price = self.current_price * (1 + (profit_target_pct + sell_fee_pct) / 100)
                else:
                    # Position is NEW or in LOSS
                    # Calculate target from ENTRY PRICE (include both fees)
                    # TARGET = Entry Price × (1 + Profit Target % + Buy Fee % + Sell Fee %)
                    target_price = entry_price * (1 + (profit_target_pct + buy_fee_pct + sell_fee_pct) / 100)
                
                # Calculate P/L
                unrealized_pl = position_value - cost_basis
                
                # Avoid division by zero if last_buy_price is 0
                if self.last_buy_price > 0:
                    profit_pct = ((self.current_price - self.last_buy_price) / self.last_buy_price * 100)
                else:
                    # If no entry price recorded, use current position value vs cost basis
                    profit_pct = ((position_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
                
                # Calculate Final Profit using correct formula:
                # LOGIC CORRECTION: For profitable positions, calculate from CURRENT value
                
                if self.last_buy_price > 0 and self.current_price > entry_price * 1.05:
                    # OPEN & PROFITABLE position
                    # Value at Target = Current Value × (1 + Profit Target % / 100)
                    value_at_target = position_value * (1 + profit_target_pct / 100)
                    
                    # Sell Fee = Value at Target × Sell Fee %
                    sell_fee = value_at_target * self.sell_fee_rate
                    
                    # Final Profit = Profit Target % of Current Value - Sell Fee
                    potential_profit = value_at_target - position_value - sell_fee
                else:
                    # NEW position
                    # Value at Target = Initial Investment × (1 + Profit Target % / 100)
                    value_at_target = cost_basis * (1 + profit_target_pct / 100)
                    
                    # Sell Fee = Value at Target × Sell Fee %
                    sell_fee = value_at_target * self.sell_fee_rate
                    
                    # Final Profit = Value at Target - Initial Investment - Sell Fee
                    potential_profit = value_at_target - cost_basis - sell_fee
                
                # Gross sell value (for display)
                gross_sell_value = btc_amount * target_price
                
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
                
                # Update target and stop loss
                # CRITICAL FIX: Stop loss must be based on CURRENT PRICE for open profitable positions
                
                if self.last_buy_price > 0 and self.current_price > entry_price * 1.05:
                    # OPEN & PROFITABLE position
                    # Stop Loss = Current Price × (1 - Stop Loss %)
                    # This protects your gains, not your entry
                    stop_price = self.current_price * (1 - self.stop_loss / 100)
                elif self.last_buy_price > 0:
                    # NEW or LOSS position
                    # Stop Loss = Entry Price × (1 - Stop Loss %)
                    stop_price = self.last_buy_price * (1 - self.stop_loss / 100)
                else:
                    # No entry price
                    stop_price = self.current_price * (1 - self.stop_loss / 100)
                
                self.target_price_var.set(f"${target_price:,.2f}")
                self.stop_price_var.set(f"${stop_price:,.2f}")
                
                # Show CORRECT calculation formula based on position type
                if self.last_buy_price > 0 and self.current_price > entry_price * 1.05:
                    # Profitable position - calculated from current price
                    self.calc_info_var.set(
                        f"Target = Current ${self.current_price:,.2f} × (1 + {profit_target_pct + sell_fee_pct:.1f}%) | Stop = Current × (1 - {self.stop_loss:.1f}%) = ${stop_price:,.2f}"
                    )
                else:
                    # New position - calculated from entry price
                    self.calc_info_var.set(
                        f"Target = Entry ${entry_price:.2f} × (1 + {profit_target_pct + buy_fee_pct + sell_fee_pct:.1f}%) | Stop = Entry × (1 - {self.stop_loss:.1f}%) = ${stop_price:,.2f}"
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
            return
        
        if self.balance_usd < self.position_size:
            print(f"\n❌ Insufficient funds! Need ${self.position_size:.2f}, have ${self.balance_usd:.2f}")
            return
            
        self.execute_buy()
    
    def execute_buy(self):
        """Execute buy order"""
        try:
            # Use current market price as entry
            entry_price = self.current_price
            
            if entry_price <= 0:
                print("\n❌ Invalid entry price - no price data available")
                return
            
            # Calculate buy using CORRECT formula
            buy_fee = self.position_size * self.buy_fee_rate
            net_investment = self.position_size - buy_fee
            btc_amount = net_investment / entry_price
            
            # Validate balance
            if self.position_size > self.balance_usd:
                print(f"\n❌ Insufficient funds! Need ${self.position_size:.2f}, have ${self.balance_usd:.2f}")
                return
            
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
            # Calculate sell
            btc_qty = self.balance_btc  # Store before clearing
            gross_proceeds = btc_qty * self.current_price
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
            
            mode_indicator = " [DRY RUN]" if self.dry_run else " [LIVE]"
            print(f"\n✓ SELL EXECUTED ({reason}){mode_indicator}:")
            print(f"   Sale Price: ${self.current_price:,.2f}")
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
            self.entry_price_entry.configure(state='normal')
            
            # Reset auto buy flag so it can trigger again
            self.auto_buy_executed = False
            
            # AUTO-LOOP: Calculate rebuy price and activate Auto Buy
            if self.auto_mode or self.auto_buy_enabled:
                # Calculate rebuy price: Sell price - X% (to profit on the cycle)
                # Use configurable rebuy drop %
                rebuy_drop_pct = self.rebuy_drop
                rebuy_price = self.current_price * (1 - rebuy_drop_pct / 100)
                
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
        
    def toggle_trading(self):
        """Toggle monitoring on/off"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.start_button.configure(text="Stop Monitoring")
            self.update_thread = threading.Thread(target=self.update_price)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            # Enable buy button only if we don't have a position
            if self.balance_btc == 0:
                self.buy_button.configure(state='normal')
            
            print("\n📊 Live Monitoring Started")
            print("   🔄 Price updates: 10 times per second (100ms intervals)")
            print("   💰 Click 'Execute Buy' when ready to open a position")
        else:
            self.start_button.configure(text="Start Monitoring")
            self.buy_button.configure(state='disabled')
            print("\n⏸️  Monitoring stopped")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = BTCTrader()
    app.run()
