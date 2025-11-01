"""
Test GUI Balance Integration
"""
import os

# Set LIVE mode to test real balance
os.environ['TRADING_MODE'] = 'LIVE'

print("="*70)
print("TESTING GUI WITH REAL BALANCE")
print("="*70)
print()

try:
    from coinbase_complete_api import CoinbaseCompleteAPI
    from config import Config
    
    # Test API connection
    api = CoinbaseCompleteAPI()
    print(f"API Mode: {'LIVE' if Config.is_live_mode() else 'SIMULATION'}")
    print(f"JWT Format: {'✅ ECDSA' if api.is_jwt_format else '❌ Ed25519'}")
    print()
    
    if Config.is_live_mode() and api.is_jwt_format:
        print("🔄 Testing balance retrieval...")
        accounts = api.list_accounts()
        
        balance_usd = 0.0
        balance_btc = 0.0
        
        for account in accounts.get('accounts', []):
            currency = account.get('currency')
            available = float(account.get('available_balance', {}).get('value', 0))
            
            if currency == 'USD':
                balance_usd = available
            elif currency == 'BTC':
                balance_btc = available
        
        print(f"✅ Balance loaded successfully:")
        print(f"   USD: ${balance_usd:.2f}")
        print(f"   BTC: {balance_btc:.8f}")
        print()
        print("✅ GUI should load with real balance")
        print()
        print("To launch GUI run:")
        print("   python btc_trader.py")
    else:
        print("⚠️  Not in LIVE mode or credentials not ECDSA")
        print("   GUI will use mock balance")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
