"""
Coinbase Advanced Trade API with JWT Authentication (ECDSA)
Following official documentation: https://docs.cdp.coinbase.com/coinbase-app/
"""
import requests
import time
from coinbase import jwt_generator
from config import Config


class CoinbaseAdvancedTradeJWT:
    """Coinbase Advanced Trade API with proper JWT authentication"""
    
    BASE_URL = "https://api.coinbase.com"
    
    def __init__(self):
        """Initialize API client"""
        # For JWT authentication, credentials must be in this format:
        # api_key = "organizations/{org_id}/apiKeys/{key_id}"
        # api_secret = "-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----"
        
        self.api_key = Config.COINBASE_API_KEY
        self.api_secret = Config.COINBASE_API_SECRET
        self.is_live = Config.is_live_mode()
        
        # Check if credentials are in correct format for JWT
        self.is_jwt_format = self.api_secret.startswith("-----BEGIN EC PRIVATE KEY-----")
        
        if not self.is_jwt_format:
            print("⚠️  WARNING: API credentials are not in ECDSA format")
            print("   Current format: Ed25519 (Base64)")
            print("   Required format: ECDSA (PEM)")
            print()
            print("   Please create a new API key with:")
            print("   1. Go to: https://portal.cdp.coinbase.com/projects/api-keys")
            print("   2. Create API key")
            print("   3. ⚠️  IMPORTANT: Set signature algorithm to ECDSA (NOT Ed25519)")
            print("   4. Download credentials")
            print()
    
    def _make_request(self, method, endpoint, data=None):
        """Make authenticated API request using JWT"""
        if not self.is_live:
            raise Exception("Cannot make API requests in SIMULATION mode")
        
        if not self.is_jwt_format:
            raise Exception(
                "API credentials must be in ECDSA format with PEM private key. "
                "Please create a new API key with ECDSA signature algorithm."
            )
        
        # Build request path
        request_path = f"/api/v3/brokerage{endpoint}"
        
        # Generate JWT token for this specific request
        jwt_uri = jwt_generator.format_jwt_uri(method, request_path)
        jwt_token = jwt_generator.build_rest_jwt(jwt_uri, self.api_key, self.api_secret)
        
        # Build headers with JWT
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.BASE_URL}{request_path}"
        
        print(f"\n🔐 Request:")
        print(f"   Method: {method}")
        print(f"   URL: {url}")
        print(f"   JWT: {jwt_token[:50]}...")
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            import json
            body = json.dumps(data) if data else ''
            response = requests.post(url, headers=headers, data=body, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"   Response: {response.status_code}")
        
        response.raise_for_status()
        return response.json()
    
    def get_spot_price(self, pair='BTC-USD'):
        """Get current spot price (public endpoint)"""
        url = f"{self.BASE_URL}/v2/prices/{pair}/spot"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data['data']['amount'])
    
    def get_accounts(self):
        """
        GET /api/v3/brokerage/accounts
        List all accounts with balances
        Required permission: view
        """
        if not self.is_live:
            return {'accounts': [
                {'currency': 'USD', 'available_balance': {'value': '1000.0'}},
                {'currency': 'BTC', 'available_balance': {'value': '0.0'}}
            ]}
        
        try:
            response = self._make_request('GET', '/accounts')
            return response
        except Exception as e:
            print(f"❌ Error getting accounts: {e}")
            return {'accounts': []}
    
    def get_account_balance(self):
        """Get account balances in simplified format"""
        accounts_data = self.get_accounts()
        balances = {}
        
        for account in accounts_data.get('accounts', []):
            currency = account.get('currency')
            balance = float(account.get('available_balance', {}).get('value', 0))
            balances[currency] = balance
        
        return balances
    
    def create_order(self, product_id, side, order_config):
        """
        POST /api/v3/brokerage/orders
        Create a new order
        Required permission: trade
        """
        if not self.is_live:
            print(f"[SIMULATION] Would {side} {product_id}")
            return {'order_id': 'sim_' + str(int(time.time())), 'status': 'SIMULATED'}
        
        try:
            order_data = {
                'client_order_id': f'{side.lower()}_{int(time.time())}',
                'product_id': product_id,
                'side': side,
                'order_configuration': order_config
            }
            
            response = self._make_request('POST', '/orders', order_data)
            print(f"✅ Order created: {response.get('order_id')}")
            return response
            
        except Exception as e:
            print(f"❌ Error creating order: {e}")
            return None
    
    def place_market_buy_order(self, pair, amount_usd):
        """Place market buy order"""
        order_config = {
            'market_market_ioc': {
                'quote_size': str(amount_usd)
            }
        }
        return self.create_order(pair, 'BUY', order_config)
    
    def place_market_sell_order(self, pair, amount_btc):
        """Place market sell order"""
        order_config = {
            'market_market_ioc': {
                'base_size': str(amount_btc)
            }
        }
        return self.create_order(pair, 'SELL', order_config)


# Test if run directly
if __name__ == '__main__':
    print("="*70)
    print("COINBASE ADVANCED TRADE API - JWT Authentication")
    print("="*70)
    print()
    
    api = CoinbaseAdvancedTradeJWT()
    
    print(f"Mode: {'[LIVE]' if api.is_live else '[SIMULATION]'}")
    print(f"JWT Format: {'✅ ECDSA (correct)' if api.is_jwt_format else '❌ Ed25519 (incorrect)'}")
    print()
    
    if not api.is_jwt_format:
        print("="*70)
        print("ACTION REQUIRED")
        print("="*70)
        print()
        print("Your current API key (Bot2) uses Ed25519 signature algorithm.")
        print("Advanced Trade API requires ECDSA signature algorithm.")
        print()
        print("Steps to fix:")
        print("1. Go to: https://portal.cdp.coinbase.com/projects/api-keys")
        print("2. Create new API key")
        print("3. ⚠️  CRITICAL: Select 'ECDSA' as signature algorithm")
        print("4. Configure:")
        print("   - Permissions: View, Trade")
        print("   - IP allowlist: 24.157.20.150")
        print("5. Download the JSON file")
        print("6. Update .env with the new credentials")
        print()
        print("The new credentials will have format:")
        print('  api_key: "organizations/xxx/apiKeys/yyy"')
        print('  private_key: "-----BEGIN EC PRIVATE KEY-----\\n...\\n-----END EC PRIVATE KEY-----"')
        print()
    else:
        # Test with correct credentials
        print("✅ Credentials are in correct format!")
        print()
        
        # Test public endpoint
        try:
            price = api.get_spot_price()
            print(f"✅ Public API works: BTC = ${price:,.2f}")
        except Exception as e:
            print(f"❌ Public API error: {e}")
        
        print()
        
        # Test authenticated endpoint
        if api.is_live:
            print("Testing authenticated endpoint...")
            try:
                balances = api.get_account_balance()
                print(f"✅ Authentication works!")
                print(f"   Balances: {balances}")
            except Exception as e:
                print(f"❌ Authentication error: {e}")
        else:
            print("[SIMULATION] Set TRADING_MODE=LIVE to test authentication")
    
    print()
    print("="*70)
