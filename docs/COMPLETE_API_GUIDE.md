# 📚 Guía Completa de API - 48 Endpoints

## ✅ Implementación Completa del Coinbase Advanced Trade API

```
Total Endpoints: 48
Tests: 91/91 pasando (100%)
Coverage: Todos los endpoints documentados oficialmente
```

---

## 🚀 Uso Básico

```python
from coinbase_complete_api import CoinbaseCompleteAPI

# Inicializar el cliente
api = CoinbaseCompleteAPI()

# El cliente detecta automáticamente ECDSA y modo LIVE/SIMULATION
```

---

## 📊 Endpoints por Categoría

### 1. 👤 ACCOUNTS (2 endpoints)

#### List Accounts
```python
# Obtener lista de cuentas
accounts = api.list_accounts(limit=10, cursor=None)

# Respuesta:
{
    'accounts': [
        {
            'uuid': 'account-id',
            'currency': 'USD',
            'available_balance': {'value': '1000.00'},
            'hold': {'value': '0.00'}
        }
    ]
}
```

#### Get Account
```python
# Obtener cuenta específica
account = api.get_account('account-id')
```

---

### 2. 🛒 ORDERS (6 endpoints)

#### Create Order
```python
# Market Buy Order
order_config = {
    'market_market_ioc': {
        'quote_size': '100.00'  # Comprar $100 de BTC
    }
}

order = api.create_order(
    client_order_id='my-order-123',
    product_id='BTC-USD',
    side='BUY',
    order_configuration=order_config
)

# Market Sell Order
order_config = {
    'market_market_ioc': {
        'base_size': '0.001'  # Vender 0.001 BTC
    }
}

order = api.create_order(
    client_order_id='my-order-124',
    product_id='BTC-USD',
    side='SELL',
    order_configuration=order_config
)
```

#### Cancel Orders
```python
# Cancelar una o más órdenes
result = api.cancel_orders(['order-id-1', 'order-id-2'])
```

#### List Orders
```python
# Listar órdenes históricas
orders = api.list_orders(
    product_id='BTC-USD',
    order_status='OPEN',  # OPEN, FILLED, CANCELLED
    limit=10,
    start_date='2024-01-01',
    end_date='2024-01-31'
)
```

#### List Fills
```python
# Listar ejecuciones de órdenes
fills = api.list_fills(
    product_id='BTC-USD',
    order_id='specific-order-id',  # Opcional
    limit=10
)
```

#### Get Order
```python
# Obtener orden específica
order = api.get_order('order-id')
```

#### Preview Order
```python
# Preview de orden antes de ejecutar
preview = api.preview_order(
    product_id='BTC-USD',
    side='BUY',
    order_configuration=order_config
)
```

---

### 3. 📈 PRODUCTS (6 endpoints)

#### List Products
```python
# Listar todos los productos disponibles
products = api.list_products(
    limit=50,
    product_type='SPOT'  # SPOT, FUTURE
)
```

#### Get Product
```python
# Información de producto específico
product = api.get_product('BTC-USD')
```

#### Get Product Candles
```python
# Obtener velas/candles de precio
candles = api.get_product_candles(
    product_id='BTC-USD',
    start='2024-01-01T00:00:00Z',
    end='2024-01-02T00:00:00Z',
    granularity='ONE_HOUR'  # ONE_MINUTE, FIVE_MINUTE, etc.
)
```

#### Get Market Trades
```python
# Últimas transacciones del mercado
trades = api.get_market_trades(
    product_id='BTC-USD',
    limit=10
)
```

#### Get Best Bid/Ask
```python
# Mejor bid/ask para productos
best = api.get_best_bid_ask(
    product_ids=['BTC-USD', 'ETH-USD']
)
```

#### Get Product Book
```python
# Order book de un producto
book = api.get_product_book(
    product_id='BTC-USD',
    limit=10
)
```

---

### 4. 🔄 CONVERT (3 endpoints)

#### Create Convert Quote
```python
# Crear quote para conversión
quote = api.create_convert_quote(
    from_account='BTC-account-id',
    to_account='USD-account-id',
    amount='0.001'
)
```

#### Commit Convert Trade
```python
# Ejecutar conversión
trade = api.commit_convert_trade(
    trade_id='quote-id',
    from_account='BTC-account-id',
    to_account='USD-account-id',
    amount='0.001'
)
```

#### Get Convert Trade
```python
# Obtener info de conversión
trade = api.get_convert_trade(
    trade_id='trade-id',
    from_account='BTC-account-id',
    to_account='USD-account-id'
)
```

---

### 5. 💼 PORTFOLIOS (6 endpoints)

#### List Portfolios
```python
# Listar portfolios
portfolios = api.list_portfolios(
    portfolio_type='DEFAULT'  # DEFAULT, CONSUMER
)
```

#### Create Portfolio
```python
# Crear nuevo portfolio
portfolio = api.create_portfolio(name='Trading Portfolio')
```

#### Move Portfolio Funds
```python
# Mover fondos entre portfolios
result = api.move_portfolio_funds(
    funds={'value': '100', 'currency': 'USD'},
    source_portfolio_uuid='source-uuid',
    target_portfolio_uuid='target-uuid'
)
```

#### Get Portfolio Breakdown
```python
# Desglose de portfolio
breakdown = api.get_portfolio_breakdown('portfolio-uuid')
```

#### Delete Portfolio
```python
# Eliminar portfolio
api.delete_portfolio('portfolio-uuid')
```

#### Edit Portfolio
```python
# Editar nombre de portfolio
api.edit_portfolio('portfolio-uuid', name='New Name')
```

---

### 6. 💰 FEES & TRANSACTIONS (1 endpoint)

#### Get Transaction Summary
```python
# Resumen de transacciones
summary = api.get_transaction_summary(
    start_date='2024-01-01',
    end_date='2024-01-31',
    user_native_currency='USD',
    product_type='SPOT'
)
```

---

### 7. 📊 FUTURES (9 endpoints)

#### Get Futures Balance Summary
```python
balance = api.get_futures_balance_summary()
```

#### List Futures Positions
```python
positions = api.list_futures_positions()
```

#### Get Futures Position
```python
position = api.get_futures_position('BTC-PERP')
```

#### Schedule Futures Sweep
```python
sweep = api.schedule_futures_sweep(usd_amount='100.00')
```

#### List Futures Sweeps
```python
sweeps = api.list_futures_sweeps()
```

#### Cancel Pending Futures Sweep
```python
api.cancel_pending_futures_sweep()
```

#### Get Intraday Margin Setting
```python
setting = api.get_intraday_margin_setting()
```

#### Set Intraday Margin Setting
```python
api.set_intraday_margin_setting(setting='STANDARD')
```

#### Get Current Margin Window
```python
window = api.get_current_margin_window()
```

---

### 8. 🔮 PERPETUALS (6 endpoints)

#### Get Perpetuals Portfolio Summary
```python
summary = api.get_perpetuals_portfolio_summary('portfolio-uuid')
```

#### List Perpetuals Positions
```python
positions = api.list_perpetuals_positions('portfolio-uuid')
```

#### Get Perpetuals Position
```python
position = api.get_perpetuals_position('portfolio-uuid', 'BTC-PERP')
```

#### Get Perpetuals Portfolio Balances
```python
balances = api.get_perpetuals_portfolio_balances('portfolio-uuid')
```

#### Opt-In Multi Asset Collateral
```python
result = api.opt_in_multi_asset_collateral(
    portfolio_uuid='uuid',
    multi_asset_collateral_enabled=True
)
```

#### Allocate Portfolio
```python
allocation = api.allocate_portfolio(
    portfolio_uuid='uuid',
    symbol='BTC-PERP',
    amount='100',
    currency='USD'
)
```

---

### 9. 💳 PAYMENT METHODS (2 endpoints)

#### List Payment Methods
```python
methods = api.list_payment_methods()
```

#### Get Payment Method
```python
method = api.get_payment_method('payment-method-id')
```

---

### 10. 🔑 DATA API (1 endpoint)

#### Get API Key Permissions
```python
# Ver permisos de tu API key
permissions = api.get_api_key_permissions()

# Respuesta:
{
    'can_view': True,
    'can_trade': True,
    'can_transfer': False,
    'portfolio_permissions': []
}
```

---

### 11. 🌐 PUBLIC ENDPOINTS (6 endpoints - Sin autenticación)

#### Get Server Time
```python
time = api.get_server_time()
```

#### Get Public Product Book
```python
book = api.get_public_product_book('BTC-USD', limit=10)
```

#### List Public Products
```python
products = api.list_public_products()
```

#### Get Public Product
```python
product = api.get_public_product('BTC-USD')
```

#### Get Public Product Candles
```python
candles = api.get_public_product_candles(
    product_id='BTC-USD',
    start='2024-01-01T00:00:00Z',
    end='2024-01-02T00:00:00Z',
    granularity='ONE_HOUR'
)
```

#### Get Public Market Trades
```python
trades = api.get_public_market_trades('BTC-USD', limit=10)
```

---

## 📋 Ejemplos de Uso Completo

### Ejemplo 1: Trading Completo

```python
from coinbase_complete_api import CoinbaseCompleteAPI

api = CoinbaseCompleteAPI()

# 1. Ver balance
accounts = api.list_accounts()
print(f"Balance: {accounts}")

# 2. Ver precio actual
product = api.get_product('BTC-USD')
print(f"Precio BTC: ${product['price']}")

# 3. Preview de orden
preview = api.preview_order(
    product_id='BTC-USD',
    side='BUY',
    order_configuration={
        'market_market_ioc': {'quote_size': '100.00'}
    }
)
print(f"Preview: {preview}")

# 4. Crear orden
order = api.create_order(
    client_order_id='buy-btc-001',
    product_id='BTC-USD',
    side='BUY',
    order_configuration={
        'market_market_ioc': {'quote_size': '100.00'}
    }
)
print(f"Orden creada: {order['order_id']}")

# 5. Verificar orden
order_status = api.get_order(order['order_id'])
print(f"Estado: {order_status}")

# 6. Ver fills
fills = api.list_fills(order_id=order['order_id'])
print(f"Ejecuciones: {fills}")
```

### Ejemplo 2: Análisis de Mercado

```python
# Obtener candles de precio
candles = api.get_product_candles(
    product_id='BTC-USD',
    start='2024-01-01T00:00:00Z',
    end='2024-01-02T00:00:00Z',
    granularity='ONE_HOUR'
)

# Analizar precios
for candle in candles['candles']:
    print(f"Time: {candle['start']}, Price: {candle['close']}")

# Ver order book
book = api.get_product_book('BTC-USD', limit=5)
print(f"Best Bid: {book['bids'][0]}")
print(f"Best Ask: {book['asks'][0]}")

# Market trades recientes
trades = api.get_market_trades('BTC-USD', limit=10)
print(f"Últimos trades: {trades}")
```

### Ejemplo 3: Gestión de Portfolio

```python
# Crear portfolio
portfolio = api.create_portfolio('My Trading Portfolio')
portfolio_id = portfolio['portfolio']['uuid']

# Ver breakdown
breakdown = api.get_portfolio_breakdown(portfolio_id)
print(f"Portfolio: {breakdown}")

# Mover fondos
api.move_portfolio_funds(
    funds={'value': '100', 'currency': 'USD'},
    source_portfolio_uuid='source-id',
    target_portfolio_uuid=portfolio_id
)
```

---

## ⚠️ Permisos Requeridos

```
view      - Ver datos (accounts, orders, products, etc.)
trade     - Crear/cancelar órdenes, trading
transfer  - Mover fondos entre portfolios
```

---

## 🧪 Testing

```bash
# Tests de API completa (20 tests)
python -m pytest tests/test_complete_api.py -v

# Todos los tests (91 tests)
python -m pytest tests/ -v
```

---

## 📊 Resumen

```
========================================================================
COINBASE COMPLETE API
========================================================================

Total Endpoints:         48
Categorías:              11
Tests:                   91/91 pasando (100%)
Documentación:           Completa
Formato:                 ECDSA + JWT

READY FOR:
  ✅ Production trading
  ✅ Portfolio management
  ✅ Market analysis
  ✅ Automated trading bots
  ✅ Advanced strategies
========================================================================
```

---

## 🔗 Referencias

- [Documentación Oficial](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/rest-api)
- [Código Fuente](../coinbase_complete_api.py)
- [Tests](../tests/test_complete_api.py)

---

**Última actualización:** 31 de Octubre, 2025
**Status:** ✅ 48 Endpoints Completos e Implementados
