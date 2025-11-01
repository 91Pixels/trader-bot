"""
Coinbase Advanced Trade API Integration
Handles authentication and trading operations
"""
import requests
import hmac
import hashlib
import time
import json
from config import Config


class CoinbaseAPI:
    """Coinbase Advanced Trade API client"""
    
    BASE_URL = "https://api.coinbase.com"
    
    def __init__(self):
        """Initialize API client"""
        self.api_key = Config.COINBASE_API_KEY
        self.api_secret = Config.COINBASE_API_SECRET
        self.is_live = Config.is_live_mode()
    
    def _generate_signature(self, timestamp, method, path, body=''):
        """Generate HMAC signature for API request"""
        message = f"{timestamp}{method}{path}{body}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method, endpoint, data=None):
        """Make authenticated API request"""
        if not self.is_live:
            raise Exception("Cannot make API requests in SIMULATION mode")
        
        timestamp = str(int(time.time()))
        path = f"/api/v3{endpoint}"
        body = json.dumps(data) if data else ''
        
        signature = self._generate_signature(timestamp, method, path, body)
        
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.BASE_URL}{path}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=body, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    def get_spot_price(self, pair='BTC-USD'):
        """Get current spot price (public endpoint - no auth needed)"""
        url = f"{self.BASE_URL}/v2/prices/{pair}/spot"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data['data']['amount'])
    
    def get_account_balance(self):
        """Get account balances"""
        if not self.is_live:
            return {'USD': 1000.0, 'BTC': 0.0}
        
        try:
            response = self._make_request('GET', '/accounts')
            balances = {}
            
            for account in response.get('accounts', []):
                currency = account['currency']
                balance = float(account['available_balance']['value'])
                balances[currency] = balance
            
            return balances
        except Exception as e:
            print(f"❌ Error getting account balance: {e}")
            return {}
    
    def place_market_buy_order(self, pair, amount_usd):
        """
        Place a market buy order
        
        Args:
            pair: Trading pair (e.g., 'BTC-USD')
            amount_usd: Amount in USD to spend
        
        Returns:
            Order details or None if failed
        """
        if not self.is_live:
            print(f"[SIMULATION] Would buy ${amount_usd} of {pair}")
            return {
                'order_id': 'sim_' + str(int(time.time())),
                'status': 'filled',
                'type': 'market_buy',
                'amount_usd': amount_usd,
                'simulated': True
            }
        
        try:
            order_config = {
                'market_market_ioc': {
                    'quote_size': str(amount_usd)
                }
            }
            
            order_data = {
                'client_order_id': f'buy_{int(time.time())}',
                'product_id': pair,
                'side': 'BUY',
                'order_configuration': order_config
            }
            
            response = self._make_request('POST', '/orders', order_data)
            
            print(f"✅ [LIVE] Market buy order placed:")
            print(f"   Order ID: {response.get('order_id')}")
            print(f"   Amount: ${amount_usd}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error placing buy order: {e}")
            return None
    
    def place_market_sell_order(self, pair, amount_btc):
        """
        Place a market sell order
        
        Args:
            pair: Trading pair (e.g., 'BTC-USD')
            amount_btc: Amount in BTC to sell
        
        Returns:
            Order details or None if failed
        """
        if not self.is_live:
            print(f"[SIMULATION] Would sell {amount_btc} {pair.split('-')[0]}")
            return {
                'order_id': 'sim_' + str(int(time.time())),
                'status': 'filled',
                'type': 'market_sell',
                'amount_btc': amount_btc,
                'simulated': True
            }
        
        try:
            order_config = {
                'market_market_ioc': {
                    'base_size': str(amount_btc)
                }
            }
            
            order_data = {
                'client_order_id': f'sell_{int(time.time())}',
                'product_id': pair,
                'side': 'SELL',
                'order_configuration': order_config
            }
            
            response = self._make_request('POST', '/orders', order_data)
            
            print(f"✅ [LIVE] Market sell order placed:")
            print(f"   Order ID: {response.get('order_id')}")
            print(f"   Amount: {amount_btc} BTC")
            
            return response
            
        except Exception as e:
            print(f"❌ Error placing sell order: {e}")
            return None
    
    def get_order_status(self, order_id):
        """Get status of an order"""
        if not self.is_live:
            return {'status': 'filled', 'simulated': True}
        
        try:
            response = self._make_request('GET', f'/orders/historical/{order_id}')
            return response
        except Exception as e:
            print(f"❌ Error getting order status: {e}")
            return None
    
    def cancel_order(self, order_id):
        """Cancel an open order"""
        if not self.is_live:
            print(f"[SIMULATION] Would cancel order {order_id}")
            return True
        
        try:
            response = self._make_request('POST', f'/orders/batch_cancel', {
                'order_ids': [order_id]
            })
            print(f"✅ Order {order_id} cancelled")
            return True
        except Exception as e:
            print(f"❌ Error cancelling order: {e}")
            return False


# Test connection if run directly
if __name__ == '__main__':
    print("="*70)
    print("COINBASE API CONNECTION TEST")
    print("="*70)
    
    api = CoinbaseAPI()
    
    print(f"\nMode: {' [LIVE]' if api.is_live else '[SIMULATION]'}")
    
    # Test public endpoint (always works)
    try:
        price = api.get_spot_price()
        print(f"\n✅ Spot Price: ${price:,.2f}")
    except Exception as e:
        print(f"\n❌ Failed to get spot price: {e}")
    
    # Test authenticated endpoints (only in live mode)
    if api.is_live and api.api_key and api.api_secret:
        try:
            balances = api.get_account_balance()
            print(f"\n✅ Account Balances:")
            for currency, balance in balances.items():
                print(f"   {currency}: {balance}")
        except Exception as e:
            print(f"\n❌ Failed to get account balance: {e}")
    else:
        print("\n⚠️  Authenticated endpoints not tested (simulation mode or missing credentials)")
    
    print("\n" + "="*70)
