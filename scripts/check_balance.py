"""
Check Coinbase Account Balance
"""
import os
os.environ['TRADING_MODE'] = 'LIVE'

from coinbase_advanced_trade_jwt import CoinbaseAdvancedTradeJWT

print("="*70)
print("💰 COINBASE ACCOUNT BALANCE")
print("="*70)
print()

api = CoinbaseAdvancedTradeJWT()

if not api.is_jwt_format:
    print("❌ Credentials not in correct format")
    exit(1)

print("🔄 Retrieving account information...")
print()

try:
    # Get current BTC price
    btc_price = api.get_spot_price('BTC-USD')
    
    # Get all accounts
    accounts_data = api.get_accounts()
    accounts = accounts_data.get('accounts', [])
    
    if not accounts:
        print("❌ No accounts found")
        exit(1)
    
    print("-"*70)
    print("ACCOUNT BALANCES")
    print("-"*70)
    print()
    
    # Track totals
    total_usd_value = 0
    btc_balance = 0
    usd_balance = 0
    
    # Show all accounts with balance
    for account in accounts:
        currency = account.get('currency')
        available = float(account.get('available_balance', {}).get('value', 0))
        hold = float(account.get('hold', {}).get('value', 0))
        total = available + hold
        
        if total > 0 or currency in ['BTC', 'USD', 'USDC']:
            if currency == 'BTC':
                btc_balance = available
                usd_value = available * btc_price
                total_usd_value += usd_value
                
                print(f"₿  Bitcoin (BTC)")
                print(f"   Available: {available:.8f} BTC")
                if hold > 0:
                    print(f"   On Hold: {hold:.8f} BTC")
                print(f"   Total: {total:.8f} BTC")
                print(f"   Value: ${usd_value:,.2f} USD")
                print(f"   Price: ${btc_price:,.2f} per BTC")
                print()
                
            elif currency == 'USD':
                usd_balance = available
                total_usd_value += available
                
                print(f"💵 US Dollar (USD)")
                print(f"   Available: ${available:,.2f}")
                if hold > 0:
                    print(f"   On Hold: ${hold:,.2f}")
                print(f"   Total: ${total:,.2f}")
                print()
                
            else:
                if total > 0:
                    print(f"💰 {currency}")
                    print(f"   Available: {available}")
                    if hold > 0:
                        print(f"   On Hold: {hold}")
                    print(f"   Total: {total}")
                    print()
    
    print("-"*70)
    print("PORTFOLIO SUMMARY")
    print("-"*70)
    print()
    print(f"₿  BTC Holdings: {btc_balance:.8f} BTC")
    print(f"💵 USD Balance: ${usd_balance:,.2f}")
    print()
    print(f"💰 Total Portfolio Value: ${total_usd_value:,.2f} USD")
    print()
    
    # Trading capacity
    print("-"*70)
    print("TRADING CAPACITY")
    print("-"*70)
    print()
    
    if usd_balance > 0:
        btc_can_buy = usd_balance / btc_price
        print(f"✅ With ${usd_balance:,.2f} USD you can buy:")
        print(f"   {btc_can_buy:.8f} BTC")
        print()
    else:
        print("⚠️  No USD available to buy BTC")
        print()
    
    if btc_balance > 0:
        usd_can_get = btc_balance * btc_price
        print(f"✅ With {btc_balance:.8f} BTC you can sell for:")
        print(f"   ${usd_can_get:,.2f} USD")
        print()
    else:
        print("⚠️  No BTC available to sell")
        print()
    
    print("="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
