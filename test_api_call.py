from coinbase_complete_api import CoinbaseCompleteAPI

print("="*60)
print("API CALL TEST")
print("="*60)

api = CoinbaseCompleteAPI()
print(f"Is JWT Format: {api.is_jwt_format}")
print(f"Is Live Mode: {api.is_live}")

# Test each endpoint
print("\n📊 Testing BTC Price (public)...")
try:
    import requests
    response = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot', timeout=5)
    if response.status_code == 200:
        price = float(response.json()['data']['amount'])
        print(f"✅ BTC Price: ${price:,.2f}")
    else:
        print(f"❌ BTC Price failed: {response.status_code}")
except Exception as e:
    print(f"❌ BTC Price error: {e}")

print("\n💰 Testing Wallet Balance...")
try:
    result = api.list_accounts(limit=10)
    print(f"✅ Wallet Balance: {result}")
except Exception as e:
    print(f"❌ Wallet Balance error: {e}")

print("\n📝 Testing Orders...")
try:
    result = api.list_orders(limit=10)
    print(f"✅ Orders: {result}")
except Exception as e:
    print(f"❌ Orders error: {e}")

print("\n📈 Testing Products...")
try:
    result = api.list_products(limit=10)
    print(f"✅ Products: {result}")
except Exception as e:
    print(f"❌ Products error: {e}")

print("="*60)
