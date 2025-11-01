"""
Coinbase Advanced Trade API Integration
Using official v3 brokerage endpoints
"""
import requests
import hmac
import hashlib
import time
import json
from config import Config


class CoinbaseAdvancedTradeAPI:
    """Coinbase Advanced Trade API client"""
    
    BASE_URL = "https://api.coinbase.com"
    
    def __init__(self):
        """Initialize API client"""
        self.api_key = Config.COINBASE_API_KEY
        self.api_secret = Config.COINBASE_API_SECRET
        self.is_live = Config.is_live_mode()
    
    def _generate_signature(self, timestamp, method, path, body=''):
        """Generate HMAC-SHA256 signature for API request"""
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
            raise Exception("Cannot make API requests in SIMULATION mode. Set TRADING_MODE=LIVE")
        
        timestamp = str(int(time.time()))
        path = f"/api/v3/brokerage{endpoint}"
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
    
    def get_accounts(self):
        """
        GET /api/v3/brokerage/accounts
        Get list of all accounts with balances
        Required permission: View
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
        """
        Get account balances in simplified format
        Returns: {'USD': 1000.0, 'BTC': 0.00284, ...}
        """
        accounts_data = self.get_accounts()
        balances = {}
        
        for account in accounts_data.get('accounts', []):
            currency = account.get('currency')
            balance = float(account.get('available_balance', {}).get('value', 0))
            balances[currency] = balance
        
        return balances
    
    def get_specific_account(self, account_uuid):
        """
        GET /api/v3/brokerage/accounts/{account_uuid}
        Get detailed information for a specific account
        Required permission: View
        """
        if not self.is_live:
            return {'account': {'currency': 'USD', 'available_balance': {'value': '1000.0'}}}
        
        try:
            response = self._make_request('GET', f'/accounts/{account_uuid}')
            return response
        except Exception as e:
            print(f"❌ Error getting account {account_uuid}: {e}")
            return None
    
    def create_order(self, product_id, side, order_config):
        """
        POST /api/v3/brokerage/orders
        Create a new buy or sell order
        Required permission: Trade
        
        Args:
            product_id: Trading pair (e.g., 'BTC-USD')
            side: 'BUY' or 'SELL'
            order_config: Order configuration dict
        
        Returns:
            Order details or None if failed
        """
        if not self.is_live:
            print(f"[SIMULATION] Would {side} {product_id}")
            return {
                'order_id': 'sim_' + str(int(time.time())),
                'status': 'FILLED',
                'side': side,
                'product_id': product_id,
                'simulated': True
            }
        
        try:
            order_data = {
                'client_order_id': f'{side.lower()}_{int(time.time())}',
                'product_id': product_id,
                'side': side,
                'order_configuration': order_config
            }
            
            response = self._make_request('POST', '/orders', order_data)
            
            print(f"✅ [LIVE] Order created:")
            print(f"   Order ID: {response.get('order_id')}")
            print(f"   Side: {side}")
            print(f"   Product: {product_id}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error creating order: {e}")
            return None
    
    def place_market_buy_order(self, pair, amount_usd):
        """
        Place a market buy order
        
        Args:
            pair: Trading pair (e.g., 'BTC-USD')
            amount_usd: Amount in USD to spend
        
        Returns:
            Order details or None if failed
        """
        order_config = {
            'market_market_ioc': {
                'quote_size': str(amount_usd)
            }
        }
        
        return self.create_order(pair, 'BUY', order_config)
    
    def place_market_sell_order(self, pair, amount_btc):
        """
        Place a market sell order
        
        Args:
            pair: Trading pair (e.g., 'BTC-USD')
            amount_btc: Amount in BTC to sell
        
        Returns:
            Order details or None if failed
        """
        order_config = {
            'market_market_ioc': {
                'base_size': str(amount_btc)
            }
        }
        
        return self.create_order(pair, 'SELL', order_config)
    
    def get_order_fills(self, order_id=None, product_id=None):
        """
        GET /api/v3/brokerage/orders/historical/fills
        Get historical order fills (executed orders)
        Required permission: View
        """
        if not self.is_live:
            return {'fills': []}
        
        try:
            endpoint = '/orders/historical/fills'
            params = []
            if order_id:
                params.append(f'order_id={order_id}')
            if product_id:
                params.append(f'product_id={product_id}')
            
            if params:
                endpoint += '?' + '&'.join(params)
            
            response = self._make_request('GET', endpoint)
            return response
            
        except Exception as e:
            print(f"❌ Error getting order fills: {e}")
            return {'fills': []}
    
    def get_order_history(self, product_id=None, limit=100):
        """
        GET /api/v3/brokerage/orders/historical
        Get paginated list of all orders
        Required permission: View
        """
        if not self.is_live:
            return {'orders': []}
        
        try:
            endpoint = f'/orders/historical?limit={limit}'
            if product_id:
                endpoint += f'&product_id={product_id}'
            
            response = self._make_request('GET', endpoint)
            return response
            
        except Exception as e:
            print(f"❌ Error getting order history: {e}")
            return {'orders': []}
    
    def cancel_orders(self, order_ids):
        """
        POST /api/v3/brokerage/orders/batch_cancel
        Cancel one or more open orders by client_order_id
        Required permission: Trade
        
        Args:
            order_ids: List of client_order_ids to cancel
        
        Returns:
            Cancellation results
        """
        if not self.is_live:
            print(f"[SIMULATION] Would cancel orders: {order_ids}")
            return {'results': [{'success': True, 'order_id': oid} for oid in order_ids]}
        
        try:
            cancel_data = {
                'order_ids': order_ids
            }
            
            response = self._make_request('POST', '/orders/batch_cancel', cancel_data)
            
            print(f"✅ Cancel request sent for {len(order_ids)} orders")
            return response
            
        except Exception as e:
            print(f"❌ Error cancelling orders: {e}")
            return None


# Test connection if run directly
if __name__ == '__main__':
    print("="*70)
    print("COINBASE ADVANCED TRADE API TEST")
    print("="*70)
    
    api = CoinbaseAdvancedTradeAPI()
    
    print(f"\nMode: {'[LIVE]' if api.is_live else '[SIMULATION]'}")
    
    # Test 1: Public endpoint (always works)
    print("\n" + "-"*70)
    print("TEST 1: Public Spot Price (No Auth)")
    print("-"*70)
    try:
        price = api.get_spot_price()
        print(f"✅ Current BTC Price: ${price:,.2f}")
    except Exception as e:
        print(f"❌ Failed to get spot price: {e}")
    
    # Test 2: Get accounts (requires auth in LIVE mode)
    print("\n" + "-"*70)
    print("TEST 2: Get Accounts (Requires: View permission)")
    print("-"*70)
    try:
        accounts_data = api.get_accounts()
        accounts = accounts_data.get('accounts', [])
        
        if accounts:
            print(f"✅ Found {len(accounts)} accounts:")
            for account in accounts[:5]:
                currency = account.get('currency')
                balance = account.get('available_balance', {}).get('value', 0)
                if float(balance) > 0:
                    print(f"   {currency}: {balance}")
        else:
            print("⚠️  No accounts found or not in LIVE mode")
            
    except Exception as e:
        print(f"❌ Failed to get accounts: {e}")
    
    # Test 3: Get balances (simplified)
    print("\n" + "-"*70)
    print("TEST 3: Get Account Balances (Simplified)")
    print("-"*70)
    try:
        balances = api.get_account_balance()
        
        if balances:
            print("✅ Balances:")
            for currency, balance in balances.items():
                if balance > 0:
                    print(f"   {currency}: {balance}")
        else:
            print("⚠️  No balances or not in LIVE mode")
            
    except Exception as e:
        print(f"❌ Failed to get balances: {e}")
    
    print("\n" + "="*70)
    print("Summary:")
    print(f"  API Key: {api.api_key[:20]}...")
    print(f"  Mode: {' LIVE' if api.is_live else 'SIMULATION'}")
    print(f"  Endpoints: /api/v3/brokerage/*")
    print("="*70)
