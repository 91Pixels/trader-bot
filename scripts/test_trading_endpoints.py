"""
Test Trading Endpoints
Tests buy, sell, and average entry price calculation
"""
from trading_helpers import TradingHelpers
from config import Config

print("="*70)
print("TESTING TRADING ENDPOINTS")
print("="*70)
print()

# Check mode
if not Config.is_live_mode():
    print("⚠️  Set TRADING_MODE=LIVE to use real trading endpoints")
    print()

helpers = TradingHelpers()

# Test 1: Calculate Average Entry Price from Fills
print("="*70)
print("TEST 1: CALCULATE AVERAGE ENTRY PRICE FROM FILLS")
print("="*70)
print()

avg_data = helpers.calculate_average_entry_price(product_id='BTC-USD', limit=100)

if avg_data['average_price'] > 0:
    print(f"\n📊 Average Entry Price Data:")
    print(f"   Average Price:    ${avg_data['average_price']:,.2f}")
    print(f"   Total BTC Bought: {avg_data['total_btc_bought']:.8f}")
    print(f"   Total USD Spent:  ${avg_data['total_usd_spent']:,.2f}")
    print(f"   Number of Buys:   {avg_data['buy_count']}")
else:
    print("\n⚠️  No historical fills found")
    print("   This means you haven't bought BTC through Coinbase Advanced Trade API yet")
    print("   You can still manually enter your average entry price in the GUI")

# Test 2: Break-Even Analysis
print()
print("="*70)
print("TEST 2: BREAK-EVEN PRICE CALCULATION")
print("="*70)
print()

# Use real average if available, otherwise use example
if avg_data['average_price'] > 0:
    entry_price = avg_data['average_price']
else:
    entry_price = 70000  # Example

break_even_info = helpers.get_break_even_price(entry_price)

print(f"If you bought BTC at: ${entry_price:,.2f}")
print(f"Break-Even Price:     ${break_even_info['break_even_price']:,.2f}")
print(f"Fee Impact:           ${break_even_info['fee_impact']:.2f}")
print()
print(f"🔴 Below ${break_even_info['break_even_price']:,.2f} = LOSS")
print(f"🟢 Above ${break_even_info['break_even_price']:,.2f} = PROFIT")

# Test 3: Position Analysis
print()
print("="*70)
print("TEST 3: CURRENT POSITION ANALYSIS")
print("="*70)
print()

# Get current price
import requests
try:
    response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot', timeout=5)
    if response.status_code == 200:
        current_price = float(response.json()['data']['amount'])
    else:
        current_price = 109000  # Fallback
except:
    current_price = 109000  # Fallback

# Get current BTC balance
accounts = helpers.api.list_accounts()
btc_balance = 0.0
for account in accounts.get('accounts', []):
    if account.get('currency') == 'BTC':
        btc_balance = float(account.get('available_balance', {}).get('value', 0))

if btc_balance > 0:
    analysis = helpers.analyze_position(
        current_price=current_price,
        average_entry_price=entry_price,
        btc_amount=btc_balance
    )
    
    print(f"Current BTC Balance:  {analysis['btc_amount']:.8f} BTC")
    print(f"Average Entry Price:  ${analysis['average_entry']:,.2f}")
    print(f"Current Price:        ${analysis['current_price']:,.2f}")
    print(f"Break-Even Price:     ${analysis['break_even_price']:,.2f}")
    print()
    print(f"Cost Basis:           ${analysis['cost_basis']:.2f}")
    print(f"Current Value:        ${analysis['current_value']:.2f}")
    print(f"P/L:                  ${analysis['profit_loss']:+.2f} ({analysis['profit_loss_pct']:+.2f}%)")
    print()
    print(f"Status:               {analysis['status']}")
    print(f"Recommendation:       {analysis['recommendation']}")
else:
    print("⚠️  No BTC balance found")

# Test 4: Show Buy/Sell Endpoints
print()
print("="*70)
print("TEST 4: BUY/SELL ENDPOINTS (INFO ONLY)")
print("="*70)
print()

print("📌 Buy BTC Endpoint:")
print("   helpers.buy_btc_market(usd_amount=10.0)")
print("   → Creates market buy order for $10 worth of BTC")
print()
print("📌 Sell BTC Endpoint:")
print("   helpers.sell_btc_market(btc_amount=0.0001)")
print("   → Creates market sell order for 0.0001 BTC")
print()
print("⚠️  These are REAL trading functions - use carefully in LIVE mode!")

# Test 5: Summary
print()
print("="*70)
print("SUMMARY")
print("="*70)
print()
print("✅ Available Endpoints:")
print("   1. buy_btc_market() - Buy BTC with USD")
print("   2. sell_btc_market() - Sell BTC for USD")
print("   3. calculate_average_entry_price() - Get average from fills")
print("   4. get_break_even_price() - Calculate minimum price to not lose")
print("   5. analyze_position() - Complete position analysis")
print()
print("📊 Data Sources for Average Entry Price:")
print("   • Historical fills from Coinbase (if you traded via API)")
print("   • Manual entry in GUI (if you bought elsewhere)")
print()
print("="*70)
