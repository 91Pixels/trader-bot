# Trading Endpoints - Implementación Completa

## 📊 Endpoints Implementados

### 1. **CREATE ORDER** - Comprar/Vender BTC
**Endpoint:** `POST /orders`  
**Documentación:** https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/create-order

#### Funciones Implementadas:

```python
from trading_helpers import TradingHelpers

helpers = TradingHelpers()

# COMPRAR BTC
result = helpers.buy_btc_market(usd_amount=10.0)
# Compra $10 de BTC al precio de mercado

# VENDER BTC
result = helpers.sell_btc_market(btc_amount=0.0001)
# Vende 0.0001 BTC al precio de mercado
```

#### Ejemplo de Salida (Compra):
```
✅ BUY ORDER EXECUTED
   Amount: $10.00
   Order ID: abc-123-def-456
```

---

### 2. **LIST FILLS** - Historial de Órdenes Ejecutadas
**Endpoint:** `GET /orders/historical/fills`  
**Documentación:** https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/list-fills

#### Función Implementada:

```python
# Calcular Average Entry Price desde fills
avg_data = helpers.calculate_average_entry_price(
    product_id='BTC-USD',
    limit=100
)

print(f"Average Price: ${avg_data['average_price']:,.2f}")
print(f"Total BTC Bought: {avg_data['total_btc_bought']:.8f}")
print(f"Total USD Spent: ${avg_data['total_usd_spent']:,.2f}")
```

#### Ejemplo de Salida:
```
🔄 Calculating average entry price for BTC-USD...
  BUY: 0.00010000 BTC @ $50,000.00 = $5.00
  BUY: 0.00020000 BTC @ $60,000.00 = $12.00
  BUY: 0.00015000 BTC @ $55,000.00 = $8.25

✅ Average Entry Price Calculated:
   Total BTC Bought: 0.00045000
   Total USD Spent:  $25.25
   Number of Buys:   3
   ⭐ AVERAGE PRICE: $56,111.11
```

---

### 3. **BREAK-EVEN PRICE** - Precio Mínimo para No Perder
**Función Helper:** Calculado localmente

#### Función Implementada:

```python
# Calcular break-even price
break_even_info = helpers.get_break_even_price(
    average_entry_price=70000.00
)

print(f"Break-Even Price: ${break_even_info['break_even_price']:,.2f}")
print(f"Fee Impact: ${break_even_info['fee_impact']:.2f}")
```

#### Ejemplo de Salida:
```
If you bought BTC at: $70,000.00
Break-Even Price:     $70,422.54
Fee Impact:           $422.54

🔴 Below $70,422.54 = LOSS
🟢 Above $70,422.54 = PROFIT
```

#### Fórmula:
```
Break-Even Price = Average Entry Price / (1 - Sell Fee Rate)
                 = $70,000 / (1 - 0.006)
                 = $70,000 / 0.994
                 = $70,422.54
```

---

### 4. **POSITION ANALYSIS** - Análisis Completo de Posición
**Función Helper:** Combina múltiples datos

#### Función Implementada:

```python
# Analizar posición actual
analysis = helpers.analyze_position(
    current_price=110000.00,
    average_entry_price=70000.00,
    btc_amount=0.00004323
)

print(f"Status: {analysis['status']}")
print(f"P/L: ${analysis['profit_loss']:+,.2f} ({analysis['profit_loss_pct']:+.2f}%)")
print(f"Recommendation: {analysis['recommendation']}")
```

#### Ejemplo de Salida:
```
Current BTC Balance:  0.00004323 BTC
Average Entry Price:  $70,000.00
Current Price:        $110,043.15
Break-Even Price:     $70,422.54

Cost Basis:           $3.03
Current Value:        $4.76
P/L:                  $+1.70 (+56.26%)

Status:               🟢 PROFIT ZONE
Recommendation:       Safe to sell - you'll make profit
```

---

## 🎯 Uso en la Aplicación

### En `btc_trader.py`:

```python
from trading_helpers import TradingHelpers

# Inicializar
helpers = TradingHelpers()

# 1. Obtener Average Entry Price automáticamente
avg_data = helpers.calculate_average_entry_price()
if avg_data['average_price'] > 0:
    self.last_buy_price = avg_data['average_price']
    print(f"✅ Average Entry Price loaded: ${avg_data['average_price']:,.2f}")

# 2. Ejecutar compra
def execute_buy(self):
    result = helpers.buy_btc_market(usd_amount=self.position_size)
    if result['success']:
        self.balance_btc += (self.position_size / self.current_price)
        self.balance_usd -= self.position_size

# 3. Ejecutar venta
def execute_sell(self):
    result = helpers.sell_btc_market(btc_amount=self.balance_btc)
    if result['success']:
        proceeds = self.balance_btc * self.current_price * 0.994  # After 0.6% fee
        self.balance_usd += proceeds
        self.balance_btc = 0

# 4. Verificar si es seguro vender
def is_safe_to_sell(self):
    if self.last_buy_price > 0:
        break_even_info = helpers.get_break_even_price(self.last_buy_price)
        return self.current_price > break_even_info['break_even_price']
    return False
```

---

## 📋 Resumen de Endpoints

| Endpoint | Método | Función | Propósito |
|----------|--------|---------|-----------|
| `/orders` | POST | `buy_btc_market()` | Comprar BTC con USD |
| `/orders` | POST | `sell_btc_market()` | Vender BTC por USD |
| `/orders/historical/fills` | GET | `calculate_average_entry_price()` | Obtener average entry price |
| Local | - | `get_break_even_price()` | Calcular precio mínimo |
| Local | - | `analyze_position()` | Análisis completo |

---

## ⚠️ Notas Importantes

1. **Average Entry Price desde Fills:**
   - Solo funciona si compraste BTC a través de Coinbase Advanced Trade API
   - Si compraste en otro lugar, usa el campo manual en la GUI

2. **Break-Even Price:**
   - Incluye el impacto del sell fee (0.6%)
   - Cualquier precio por encima = ganancia
   - Cualquier precio por debajo = pérdida

3. **Trading en LIVE Mode:**
   - Asegúrate de tener `TRADING_MODE=LIVE` en `.env`
   - Los órdenes son REALES y gastan dinero real
   - Siempre verifica el saldo antes de ejecutar

4. **Simulación:**
   - En modo `SIMULATION`, los órdenes no se ejecutan realmente
   - Útil para probar la lógica sin riesgo

---

## 🧪 Testing

```bash
# Test completo de endpoints
python scripts/test_trading_endpoints.py

# Resultado esperado:
✅ Average Entry Price calculation
✅ Break-Even Price calculation
✅ Position Analysis
✅ Buy/Sell endpoints info
```

---

## 📚 Referencias

- **Coinbase Advanced Trade API:** https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/rest-api
- **Create Order:** https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/create-order
- **List Fills:** https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/list-fills

---

## ✅ Estado de Implementación

```
ENDPOINTS CRÍTICOS:
  ✅ Buy BTC (market order)
  ✅ Sell BTC (market order)
  ✅ List Fills (historial)
  ✅ Calculate Average Entry Price
  ✅ Break-Even Price
  ✅ Position Analysis

HELPER FUNCTIONS:
  ✅ buy_btc_market()
  ✅ sell_btc_market()
  ✅ calculate_average_entry_price()
  ✅ get_break_even_price()
  ✅ analyze_position()

DOCUMENTACIÓN:
  ✅ Este archivo (TRADING_ENDPOINTS.md)
  ✅ Ejemplos de uso
  ✅ Script de testing
```

---

**¡Todos los endpoints están implementados y listos para usar!** 🎉
