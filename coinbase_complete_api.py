"""
Coinbase Advanced Trade API - Complete Implementation
All endpoints from: https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/rest-api
"""
import requests
import time
from coinbase import jwt_generator
from config import Config


class CoinbaseCompleteAPI:
    """Complete Coinbase Advanced Trade API client with all endpoints"""
    
    BASE_URL = "https://api.coinbase.com"
    
    def __init__(self):
        """Initialize API client"""
        self.api_key = Config.COINBASE_API_KEY
        self.api_secret = Config.COINBASE_API_SECRET
        self.is_live = Config.is_live_mode()
        
        # Check if credentials are in ECDSA format
        self.is_jwt_format = self.api_secret.startswith("-----BEGIN EC PRIVATE KEY-----")
        
        if not self.is_jwt_format:
            print("⚠️  WARNING: API credentials must be in ECDSA format for Advanced Trade API")
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make authenticated API request using JWT"""
        try:
            if not self.is_live:
                raise Exception("Cannot make API requests in SIMULATION mode")
            
            if not self.is_jwt_format:
                raise Exception("API credentials must be in ECDSA format with PEM private key")
            
            # Build request path
            request_path = f"/api/v3/brokerage{endpoint}"
            
            # Generate JWT token for this specific request
            try:
                jwt_uri = jwt_generator.format_jwt_uri(method, request_path)
                jwt_token = jwt_generator.build_rest_jwt(jwt_uri, self.api_key, self.api_secret)
                print(f"✅ JWT token generated for {method} {endpoint}")
            except Exception as e:
                print(f"❌ Error generating JWT token: {e}")
                print(f"   API Key: {self.api_key[:30] if self.api_key else 'None'}...")
                print(f"   API Secret starts: {self.api_secret[:30] if self.api_secret else 'None'}...")
                raise
            
            # Build headers with JWT
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.BASE_URL}{request_path}"
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                import json
                body = json.dumps(data) if data else ''
                response = requests.post(url, headers=headers, data=body, timeout=10)
            elif method == 'PUT':
                import json
                body = json.dumps(data) if data else ''
                response = requests.put(url, headers=headers, data=body, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error {method} {endpoint}: {e}")
            print(f"   Response: {e.response.text if hasattr(e.response, 'text') else 'No response text'}")
            raise
        except Exception as e:
            print(f"❌ Error in _make_request {method} {endpoint}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _make_public_request(self, method, endpoint, params=None):
        """Make public API request (no authentication)"""
        url = f"{self.BASE_URL}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, params=params, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    # ========================================================================
    # ACCOUNTS
    # ========================================================================
    
    def list_accounts(self, limit=None, cursor=None):
        """
        GET /accounts
        Get a list of authenticated accounts
        Permission: view
        """
        params = {}
        if limit:
            params['limit'] = limit
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request('GET', '/accounts', params=params)
    
    def get_account(self, account_id):
        """
        GET /accounts/{account_id}
        Get a single account by account ID
        Permission: view
        """
        return self._make_request('GET', f'/accounts/{account_id}')
    
    # ========================================================================
    # ORDERS
    # ========================================================================
    
    def create_order(self, client_order_id, product_id, side, order_configuration):
        """
        POST /orders
        Create an order
        Permission: trade
        
        Example order_configuration for market buy:
        {
            "market_market_ioc": {
                "quote_size": "10.00"
            }
        }
        """
        data = {
            'client_order_id': client_order_id,
            'product_id': product_id,
            'side': side,
            'order_configuration': order_configuration
        }
        
        return self._make_request('POST', '/orders', data=data)
    
    def cancel_orders(self, order_ids):
        """
        POST /orders/batch_cancel
        Cancel one or more orders
        Permission: trade
        """
        data = {'order_ids': order_ids}
        return self._make_request('POST', '/orders/batch_cancel', data=data)
    
    def list_orders(self, product_id=None, order_status=None, limit=None, start_date=None, end_date=None):
        """
        GET /orders/historical/batch
        Get a list of orders
        Permission: view
        """
        params = {}
        if product_id:
            params['product_id'] = product_id
        if order_status:
            params['order_status'] = order_status
        if limit:
            params['limit'] = limit
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        return self._make_request('GET', '/orders/historical/batch', params=params)
    
    def list_fills(self, order_id=None, product_id=None, start_date=None, end_date=None, limit=None):
        """
        GET /orders/historical/fills
        Get a list of fills
        Permission: view
        """
        params = {}
        if order_id:
            params['order_id'] = order_id
        if product_id:
            params['product_id'] = product_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if limit:
            params['limit'] = limit
        
        return self._make_request('GET', '/orders/historical/fills', params=params)
    
    def get_order(self, order_id):
        """
        GET /orders/historical/{order_id}
        Get a single order
        Permission: view
        """
        return self._make_request('GET', f'/orders/historical/{order_id}')
    
    def preview_order(self, product_id, side, order_configuration):
        """
        POST /orders/preview
        Preview an order
        Permission: view
        """
        data = {
            'product_id': product_id,
            'side': side,
            'order_configuration': order_configuration
        }
        
        return self._make_request('POST', '/orders/preview', data=data)
    
    # ========================================================================
    # PRODUCTS
    # ========================================================================
    
    def list_products(self, limit=None, offset=None, product_type=None):
        """
        GET /products
        Get a list of available currency pairs for trading
        Permission: view
        """
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if product_type:
            params['product_type'] = product_type
        
        return self._make_request('GET', '/products', params=params)
    
    def get_product(self, product_id):
        """
        GET /products/{product_id}
        Get information on a single product
        Permission: view
        """
        return self._make_request('GET', f'/products/{product_id}')
    
    def get_product_candles(self, product_id, start, end, granularity):
        """
        GET /products/{product_id}/candles
        Get rates for a single product by product ID
        Permission: view
        
        granularity: ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, THIRTY_MINUTE,
                     ONE_HOUR, TWO_HOUR, SIX_HOUR, ONE_DAY
        """
        params = {
            'start': start,
            'end': end,
            'granularity': granularity
        }
        
        return self._make_request('GET', f'/products/{product_id}/candles', params=params)
    
    def get_market_trades(self, product_id, limit=None):
        """
        GET /products/{product_id}/ticker
        Get snapshot information about the last trades (ticks)
        Permission: view
        """
        params = {}
        if limit:
            params['limit'] = limit
        
        return self._make_request('GET', f'/products/{product_id}/ticker', params=params)
    
    def get_best_bid_ask(self, product_ids=None):
        """
        GET /best_bid_ask
        Get the best bid/ask for all products
        Permission: view
        """
        params = {}
        if product_ids:
            params['product_ids'] = ','.join(product_ids) if isinstance(product_ids, list) else product_ids
        
        return self._make_request('GET', '/best_bid_ask', params=params)
    
    def get_product_book(self, product_id, limit=None):
        """
        GET /product_book
        Get a list of bids/asks for a single product
        Permission: view
        """
        params = {'product_id': product_id}
        if limit:
            params['limit'] = limit
        
        return self._make_request('GET', '/product_book', params=params)
    
    # ========================================================================
    # CONVERT
    # ========================================================================
    
    def create_convert_quote(self, from_account, to_account, amount):
        """
        POST /convert/quote
        Create a convert quote
        Permission: trade
        """
        data = {
            'from_account': from_account,
            'to_account': to_account,
            'amount': amount
        }
        
        return self._make_request('POST', '/convert/quote', data=data)
    
    def commit_convert_trade(self, trade_id, from_account, to_account, amount):
        """
        POST /convert/{trade_id}
        Commit a convert trade
        Permission: trade
        """
        data = {
            'from_account': from_account,
            'to_account': to_account,
            'amount': amount
        }
        
        return self._make_request('POST', f'/convert/{trade_id}', data=data)
    
    def get_convert_trade(self, trade_id, from_account, to_account):
        """
        GET /convert/{trade_id}
        Get a convert trade
        Permission: view
        """
        params = {
            'from_account': from_account,
            'to_account': to_account
        }
        
        return self._make_request('GET', f'/convert/{trade_id}', params=params)
    
    # ========================================================================
    # PORTFOLIOS
    # ========================================================================
    
    def list_portfolios(self, portfolio_type=None):
        """
        GET /portfolios
        Get a list of portfolios
        Permission: view
        """
        params = {}
        if portfolio_type:
            params['portfolio_type'] = portfolio_type
        
        return self._make_request('GET', '/portfolios', params=params)
    
    def create_portfolio(self, name):
        """
        POST /portfolios
        Create a portfolio
        Permission: view
        """
        data = {'name': name}
        return self._make_request('POST', '/portfolios', data=data)
    
    def move_portfolio_funds(self, funds, source_portfolio_uuid, target_portfolio_uuid):
        """
        POST /portfolios/move_funds
        Move funds between portfolios
        Permission: transfer
        """
        data = {
            'funds': funds,
            'source_portfolio_uuid': source_portfolio_uuid,
            'target_portfolio_uuid': target_portfolio_uuid
        }
        
        return self._make_request('POST', '/portfolios/move_funds', data=data)
    
    def get_portfolio_breakdown(self, portfolio_uuid):
        """
        GET /portfolios/{portfolio_uuid}
        Get the breakdown of a portfolio
        Permission: view
        """
        return self._make_request('GET', f'/portfolios/{portfolio_uuid}')
    
    def delete_portfolio(self, portfolio_uuid):
        """
        DELETE /portfolios/{portfolio_uuid}
        Delete a portfolio
        Permission: trade
        """
        return self._make_request('DELETE', f'/portfolios/{portfolio_uuid}')
    
    def edit_portfolio(self, portfolio_uuid, name):
        """
        PUT /portfolios/{portfolio_uuid}
        Edit a portfolio
        Permission: trade
        """
        data = {'name': name}
        return self._make_request('PUT', f'/portfolios/{portfolio_uuid}', data=data)
    
    # ========================================================================
    # FEES & TRANSACTIONS
    # ========================================================================
    
    def get_transaction_summary(self, start_date=None, end_date=None, user_native_currency=None, product_type=None):
        """
        GET /transaction_summary
        Get a summary of transactions
        Permission: view
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if user_native_currency:
            params['user_native_currency'] = user_native_currency
        if product_type:
            params['product_type'] = product_type
        
        return self._make_request('GET', '/transaction_summary', params=params)
    
    # ========================================================================
    # FUTURES
    # ========================================================================
    
    def get_futures_balance_summary(self):
        """
        GET /cfm/balance_summary
        Get futures balance summary
        Permission: view
        """
        return self._make_request('GET', '/cfm/balance_summary')
    
    def list_futures_positions(self):
        """
        GET /cfm/positions
        List futures positions
        Permission: view
        """
        return self._make_request('GET', '/cfm/positions')
    
    def get_futures_position(self, product_id):
        """
        GET /cfm/positions/{product_id}
        Get a futures position
        Permission: view
        """
        return self._make_request('GET', f'/cfm/positions/{product_id}')
    
    def schedule_futures_sweep(self, usd_amount):
        """
        POST /cfm/sweeps/schedule
        Schedule a futures sweep
        Permission: transfer
        """
        data = {'usd_amount': usd_amount}
        return self._make_request('POST', '/cfm/sweeps/schedule', data=data)
    
    def list_futures_sweeps(self):
        """
        GET /cfm/sweeps
        List futures sweeps
        Permission: view
        """
        return self._make_request('GET', '/cfm/sweeps')
    
    def cancel_pending_futures_sweep(self):
        """
        DELETE /cfm/sweeps
        Cancel pending futures sweep
        Permission: transfer
        """
        return self._make_request('DELETE', '/cfm/sweeps')
    
    def get_intraday_margin_setting(self):
        """
        GET /cfm/intraday/margin_setting
        Get intraday margin setting
        Permission: view
        """
        return self._make_request('GET', '/cfm/intraday/margin_setting')
    
    def set_intraday_margin_setting(self, setting):
        """
        POST /cfm/intraday/margin_setting
        Set intraday margin setting
        Permission: trade
        """
        data = {'setting': setting}
        return self._make_request('POST', '/cfm/intraday/margin_setting', data=data)
    
    def get_current_margin_window(self, margin_profile_type=None):
        """
        GET /cfm/intraday/current_margin_window
        Get current margin window
        Permission: view
        """
        params = {}
        if margin_profile_type:
            params['margin_profile_type'] = margin_profile_type
        
        return self._make_request('GET', '/cfm/intraday/current_margin_window', params=params)
    
    # ========================================================================
    # PERPETUALS
    # ========================================================================
    
    def get_perpetuals_portfolio_summary(self, portfolio_uuid):
        """
        GET /intx/portfolio/{portfolio_uuid}
        Get perpetuals portfolio summary
        Permission: view
        """
        return self._make_request('GET', f'/intx/portfolio/{portfolio_uuid}')
    
    def list_perpetuals_positions(self, portfolio_uuid):
        """
        GET /intx/positions/{portfolio_uuid}
        List perpetuals positions
        Permission: view
        """
        return self._make_request('GET', f'/intx/positions/{portfolio_uuid}')
    
    def get_perpetuals_position(self, portfolio_uuid, symbol):
        """
        GET /intx/positions/{portfolio_uuid}/{symbol}
        Get a perpetuals position
        Permission: view
        """
        return self._make_request('GET', f'/intx/positions/{portfolio_uuid}/{symbol}')
    
    def get_perpetuals_portfolio_balances(self, portfolio_uuid):
        """
        GET /intx/balances/{portfolio_uuid}
        Get perpetuals portfolio balances
        Permission: view
        """
        return self._make_request('GET', f'/intx/balances/{portfolio_uuid}')
    
    def opt_in_multi_asset_collateral(self, portfolio_uuid, multi_asset_collateral_enabled):
        """
        POST /intx/multi_asset_collateral
        Opt-in or opt-out of multi asset collateral
        Permission: trade
        """
        data = {
            'portfolio_uuid': portfolio_uuid,
            'multi_asset_collateral_enabled': multi_asset_collateral_enabled
        }
        
        return self._make_request('POST', '/intx/multi_asset_collateral', data=data)
    
    def allocate_portfolio(self, portfolio_uuid, symbol, amount, currency):
        """
        POST /intx/allocate
        Allocate portfolio
        Permission: transfer
        """
        data = {
            'portfolio_uuid': portfolio_uuid,
            'symbol': symbol,
            'amount': amount,
            'currency': currency
        }
        
        return self._make_request('POST', '/intx/allocate', data=data)
    
    # ========================================================================
    # PAYMENT METHODS
    # ========================================================================
    
    def list_payment_methods(self):
        """
        GET /payment_methods
        Get a list of payment methods
        Permission: view
        """
        return self._make_request('GET', '/payment_methods')
    
    def get_payment_method(self, payment_method_id):
        """
        GET /payment_methods/{payment_method_id}
        Get a single payment method
        Permission: view
        """
        return self._make_request('GET', f'/payment_methods/{payment_method_id}')
    
    # ========================================================================
    # DATA API
    # ========================================================================
    
    def get_api_key_permissions(self):
        """
        GET /key_permissions
        Get information about your API key's permissions
        Permission: view
        """
        return self._make_request('GET', '/key_permissions')
    
    # ========================================================================
    # PUBLIC ENDPOINTS (No authentication required)
    # ========================================================================
    
    def get_server_time(self):
        """
        GET /time
        Get the server time
        Public endpoint
        """
        return self._make_public_request('GET', '/api/v3/brokerage/time')
    
    def get_public_product_book(self, product_id, limit=None):
        """
        GET /market/product_book
        Get the public product book
        Public endpoint
        """
        params = {'product_id': product_id}
        if limit:
            params['limit'] = limit
        
        return self._make_public_request('GET', '/api/v3/brokerage/market/product_book', params=params)
    
    def list_public_products(self, limit=None, offset=None, product_type=None):
        """
        GET /market/products
        Get a list of public products
        Public endpoint
        """
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if product_type:
            params['product_type'] = product_type
        
        return self._make_public_request('GET', '/api/v3/brokerage/market/products', params=params)
    
    def get_public_product(self, product_id):
        """
        GET /market/products/{product_id}
        Get a single public product
        Public endpoint
        """
        return self._make_public_request('GET', f'/api/v3/brokerage/market/products/{product_id}')
    
    def get_public_product_candles(self, product_id, start, end, granularity):
        """
        GET /market/products/{product_id}/candles
        Get public product candles
        Public endpoint
        """
        params = {
            'start': start,
            'end': end,
            'granularity': granularity
        }
        
        return self._make_public_request('GET', f'/api/v3/brokerage/market/products/{product_id}/candles', params=params)
    
    def get_public_market_trades(self, product_id, limit=None):
        """
        GET /market/products/{product_id}/ticker
        Get public market trades
        Public endpoint
        """
        params = {}
        if limit:
            params['limit'] = limit
        
        return self._make_public_request('GET', f'/api/v3/brokerage/market/products/{product_id}/ticker', params=params)


# Test if run directly
if __name__ == '__main__':
    print("="*70)
    print("COINBASE COMPLETE API - All Endpoints")
    print("="*70)
    print()
    
    api = CoinbaseCompleteAPI()
    
    print(f"Mode: {'LIVE' if api.is_live else 'SIMULATION'}")
    print(f"JWT Format: {'✅ ECDSA' if api.is_jwt_format else '❌ Ed25519'}")
    print()
    
    if api.is_jwt_format:
        print("✅ API client ready with ALL endpoints:")
        print()
        print("📊 Accounts (2 endpoints)")
        print("🛒 Orders (6 endpoints)")
        print("📈 Products (6 endpoints)")
        print("🔄 Convert (3 endpoints)")
        print("💼 Portfolios (6 endpoints)")
        print("💰 Fees & Transactions (1 endpoint)")
        print("📊 Futures (9 endpoints)")
        print("🔮 Perpetuals (6 endpoints)")
        print("💳 Payment Methods (2 endpoints)")
        print("🔑 Data API (1 endpoint)")
        print("🌐 Public Endpoints (6 endpoints)")
        print()
        print(f"TOTAL: 48 endpoints implemented")
    
    print()
    print("="*70)
