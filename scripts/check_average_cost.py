"""
Check if Coinbase API provides Average Cost/Entry Price
"""
from coinbase_complete_api import CoinbaseCompleteAPI
import json


def check_account_data():
    """Check what data is available in accounts endpoint"""
    print("="*70)
    print("CHECKING COINBASE ACCOUNT DATA FOR AVERAGE COST")
    print("="*70)
    print()
    
    api = CoinbaseCompleteAPI()
    
    # Get accounts
    print("🔄 Fetching account data...")
    accounts_response = api.list_accounts()
    
    print("✅ Data received")
    print()
    
    # Check BTC account
    for account in accounts_response.get('accounts', []):
        if account.get('currency') == 'BTC':
            print("="*70)
            print("BTC ACCOUNT - FULL DATA:")
            print("="*70)
            print()
            print(json.dumps(account, indent=2))
            print()
            
            # Check for cost-related fields
            print("="*70)
            print("CHECKING FOR COST/ENTRY FIELDS:")
            print("="*70)
            print()
            
            possible_fields = [
                'average_cost',
                'avg_cost',
                'cost_basis',
                'entry_price',
                'average_entry',
                'avg_entry_price',
                'purchase_price',
                'basis'
            ]
            
            found_fields = []
            for field in possible_fields:
                if field in account:
                    found_fields.append(field)
                    print(f"✅ Found: {field} = {account[field]}")
            
            if not found_fields:
                print("❌ No average cost fields found in account data")
            
            print()
            
            # Check if we need to use fills to calculate
            print("="*70)
            print("ALTERNATIVE: Calculate from fills")
            print("="*70)
            print()
            print("If average cost not in accounts, we can:")
            print("1. Use list_fills() to get all BTC purchases")
            print("2. Calculate weighted average from fills")
            print()
    
    print("="*70)


def calculate_average_from_fills():
    """Calculate average cost from order fills"""
    print("="*70)
    print("CALCULATING AVERAGE COST FROM FILLS")
    print("="*70)
    print()
    
    api = CoinbaseCompleteAPI()
    
    print("🔄 Fetching order fills for BTC-USD...")
    try:
        fills = api.list_fills(product_id='BTC-USD', limit=100)
        
        print(f"✅ Retrieved {len(fills.get('fills', []))} fills")
        print()
        
        if not fills.get('fills'):
            print("❌ No fills found")
            return None
        
        # Calculate weighted average for BUY orders
        total_btc_bought = 0.0
        total_usd_spent = 0.0
        buy_count = 0
        
        print("📊 Analyzing fills...")
        print()
        
        for fill in fills.get('fills', []):
            side = fill.get('side')
            size = float(fill.get('size', 0))
            price = float(fill.get('price', 0))
            
            if side == 'BUY':
                cost = size * price
                total_btc_bought += size
                total_usd_spent += cost
                buy_count += 1
                
                print(f"  BUY: {size:.8f} BTC @ ${price:,.2f} = ${cost:,.2f}")
        
        print()
        
        if total_btc_bought > 0:
            average_cost = total_usd_spent / total_btc_bought
            
            print("="*70)
            print("CALCULATED AVERAGE COST:")
            print("="*70)
            print()
            print(f"Total BTC Bought:    {total_btc_bought:.8f} BTC")
            print(f"Total USD Spent:     ${total_usd_spent:,.2f}")
            print(f"Number of Buys:      {buy_count}")
            print()
            print(f"⭐ AVERAGE COST:     ${average_cost:,.2f} per BTC")
            print()
            
            # Get current balance
            accounts = api.list_accounts()
            current_btc = 0.0
            for account in accounts.get('accounts', []):
                if account.get('currency') == 'BTC':
                    current_btc = float(account.get('available_balance', {}).get('value', 0))
            
            if current_btc > 0:
                cost_basis = current_btc * average_cost
                print(f"Your current {current_btc:.8f} BTC")
                print(f"Cost basis: ${cost_basis:,.2f}")
            
            return average_cost
        else:
            print("❌ No BUY orders found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    # First check if average cost is in account data
    check_account_data()
    
    print()
    print("="*70)
    print()
    
    # Then try calculating from fills
    average_cost = calculate_average_from_fills()
    
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print()
    
    if average_cost:
        print(f"✅ Average Entry Price: ${average_cost:,.2f}")
        print()
        print("We can use this in btc_trader.py to set:")
        print("  self.last_buy_price = average_cost")
    else:
        print("⚠️  Could not determine average cost")
        print("   Using current market value as cost basis")
    
    print()
    print("="*70)
