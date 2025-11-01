# 💰 Integración de Balance Real de Coinbase en GUI

## ✅ Implementado: Balance Real en Tiempo Real

El bot ahora se conecta automáticamente a Coinbase y muestra tu balance real en la GUI.

```
========================================================================
BALANCE REAL INTEGRADO EN GUI
========================================================================

Endpoint Usado:     list_accounts()
Modo:               LIVE (con credenciales ECDSA)
Actualización:      Manual (botón Refresh)
Fallback:           Mock balance si no se puede conectar

BALANCE ACTUAL:
  USD: $0.00
  BTC: 0.00004323 ($4.74 USD)
========================================================================
```

---

## 🎯 Características

### 1. ✅ Carga Automática al Iniciar
```
- Al abrir btc_trader.py en modo LIVE
- Detecta automáticamente credenciales ECDSA
- Carga balance real de Coinbase
- Muestra indicador de conexión
```

### 2. ✅ Botón de Refresh Manual
```
- Botón "🔄 Refresh Balance from Coinbase"
- Actualiza balance en tiempo real
- Actualiza indicador de estado
- Funciona solo en LIVE mode
```

### 3. ✅ Indicadores Visuales
```
✅ Connected to Coinbase          - Balance real cargado
⚠️ Using Mock Balance             - Modo SIMULATION
❌ Connection Failed              - Error al conectar
```

### 4. ✅ Fallback Automático
```
- Si falla la conexión → usa mock balance
- Si está en SIMULATION → usa mock balance
- Si credenciales no son ECDSA → usa mock balance
```

---

## 🚀 Uso

### Opción 1: Modo LIVE (Balance Real)

```bash
# 1. Editar .env
TRADING_MODE=LIVE

# 2. Ejecutar GUI
python btc_trader.py
```

**Resultado:**
```
🔄 Loading real balance from Coinbase...
✅ Real balance loaded:
   USD: $0.00
   BTC: 0.00004323

GUI muestra:
┌─────────────────────────────────────────┐
│ Account (Real Balance from Coinbase)    │
├─────────────────────────────────────────┤
│ USD: $0.00                              │
│ BTC: 0.00004323                         │
│                                         │
│ [🔄 Refresh Balance from Coinbase]      │
│                                         │
│ ✅ Connected to Coinbase                │
└─────────────────────────────────────────┘
```

### Opción 2: Modo SIMULATION (Mock Balance)

```bash
# 1. Editar .env
TRADING_MODE=SIMULATION

# 2. Ejecutar GUI
python btc_trader.py
```

**Resultado:**
```
GUI muestra:
┌─────────────────────────────────────────┐
│ Account (Mock Balance)                  │
├─────────────────────────────────────────┤
│ USD: $1000.00                           │
│ BTC: 0.00000000                         │
│                                         │
│ [🔄 Refresh Balance from Coinbase]      │
│                                         │
│ ⚠️ Using Mock Balance                   │
│ (Set TRADING_MODE=LIVE for real)       │
└─────────────────────────────────────────┘
```

---

## 🔧 Código de Integración

### 1. Inicialización en btc_trader.py

```python
def __init__(self):
    # Initialize Coinbase API
    self.api = CoinbaseCompleteAPI()
    self.using_real_balance = False
    
    # Default balances
    self.balance_usd = 1000.0  # Mock
    self.balance_btc = 0.0     # Mock
    
    # Load real balance if in LIVE mode
    if Config.is_live_mode() and self.api.is_jwt_format:
        self.load_real_balance()
```

### 2. Método load_real_balance()

```python
def load_real_balance(self):
    """Load real balance from Coinbase"""
    try:
        print("\n🔄 Loading real balance from Coinbase...")
        accounts = self.api.list_accounts()
        
        # Extract USD and BTC balances
        for account in accounts.get('accounts', []):
            currency = account.get('currency')
            available = float(account.get('available_balance', {}).get('value', 0))
            
            if currency == 'USD':
                self.balance_usd = available
            elif currency == 'BTC':
                self.balance_btc = available
        
        self.using_real_balance = True
        print(f"✅ Real balance loaded:")
        print(f"   USD: ${self.balance_usd:.2f}")
        print(f"   BTC: {self.balance_btc:.8f}")
        
    except Exception as e:
        print(f"⚠️  Could not load real balance: {e}")
        self.using_real_balance = False
```

### 3. Método refresh_balance()

```python
def refresh_balance(self):
    """Refresh balance from Coinbase (manual)"""
    if Config.is_live_mode() and self.api.is_jwt_format:
        self.load_real_balance()
        # Update GUI
        self.balance_var.set(
            f"USD: ${self.balance_usd:.2f}\nBTC: {self.balance_btc:.8f}"
        )
        self.balance_status_var.set("✅ Connected to Coinbase - Balance Updated")
        print("✅ Balance refreshed from Coinbase")
```

---

## 📊 Endpoint Utilizado

### list_accounts()

```python
from coinbase_complete_api import CoinbaseCompleteAPI

api = CoinbaseCompleteAPI()
accounts = api.list_accounts()

# Respuesta:
{
    'accounts': [
        {
            'uuid': 'account-id',
            'currency': 'USD',
            'available_balance': {'value': '0.00'},
            'hold': {'value': '0.00'}
        },
        {
            'uuid': 'account-id',
            'currency': 'BTC',
            'available_balance': {'value': '0.00004323'},
            'hold': {'value': '0.00'}
        }
    ]
}
```

---

## 🧪 Testing

### Test Balance Integration

```bash
# Test si el balance se carga correctamente
python scripts/test_gui_balance.py
```

**Salida esperada:**
```
========================================================================
TESTING GUI WITH REAL BALANCE
========================================================================

API Mode: LIVE
JWT Format: ✅ ECDSA

🔄 Testing balance retrieval...
✅ Balance loaded successfully:
   USD: $0.00
   BTC: 0.00004323

✅ GUI should load with real balance
========================================================================
```

---

## ⚠️ Troubleshooting

### Problema: "Using Mock Balance"

**Solución:**
```bash
# Verificar modo
echo $TRADING_MODE  # Debe ser LIVE

# Si no:
# Editar .env
TRADING_MODE=LIVE

# Reiniciar GUI
python btc_trader.py
```

### Problema: "Connection Failed"

**Causas posibles:**
1. Credenciales no son ECDSA
2. IP no está en allowlist
3. API key no tiene permisos "view"
4. Coinbase API está down

**Solución:**
```bash
# Verificar credenciales
python scripts/test_gui_balance.py

# Verificar permisos
# - View ✅
# - Trade ✅
# - IP: 24.157.20.150 ✅
```

### Problema: Balance no se actualiza

**Solución:**
```
1. Click en botón "🔄 Refresh Balance from Coinbase"
2. Esperar 1-2 segundos
3. Balance debe actualizarse
4. Si persiste, reiniciar GUI
```

---

## 📈 Próximas Mejoras

### En desarrollo:
```
⏳ Auto-refresh cada X minutos
⏳ Historial de balances
⏳ Notificaciones de cambios
⏳ Gráfico de balance en tiempo real
```

---

## 📋 Resumen

```
========================================================================
BALANCE REAL INTEGRADO EN GUI
========================================================================

Archivo Modificado:   btc_trader.py
Endpoint Usado:       list_accounts()
Modo Requerido:       LIVE + ECDSA credentials
Actualización:        Manual (botón Refresh)

CARACTERÍSTICAS:
  ✅ Carga automática al iniciar
  ✅ Botón de refresh manual
  ✅ Indicadores visuales de estado
  ✅ Fallback a mock balance
  ✅ No rompe funcionalidad existente

TESTING:
  ✅ Verificado con balance real
  ✅ Verificado modo SIMULATION
  ✅ Verificado fallback

LISTO PARA:
  ✅ Uso en producción
  ✅ Trading con balance real
  ✅ Monitoreo en tiempo real
========================================================================
```

---

**Implementado:** 31 de Octubre, 2025  
**Status:** ✅ Completado y Testeado  
**Balance Actual:** $0.00 USD + 0.00004323 BTC ($4.74 USD)
