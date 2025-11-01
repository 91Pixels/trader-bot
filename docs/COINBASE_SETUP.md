# 🔐 Configuración de Coinbase API para Trading Real

## ⚠️ IMPORTANTE - LEE ANTES DE CONTINUAR

Este bot puede realizar **transacciones reales** con dinero real. Por seguridad:

1. **Comienza en modo SIMULATION** para probar
2. **Usa pequeñas cantidades** cuando pases a LIVE
3. **Nunca compartas tus API keys** con nadie
4. **Guarda backups** de tu configuración

---

## 📋 Paso 1: Obtener API Keys de Coinbase

### 1.1 Crear Cuenta en Coinbase
1. Ve a [https://www.coinbase.com](https://www.coinbase.com)
2. Crea una cuenta o inicia sesión
3. Completa la verificación de identidad (requerido para trading)
4. Agrega fondos a tu cuenta

### 1.2 Generar API Keys
1. Ve a [https://www.coinbase.com/settings/api](https://www.coinbase.com/settings/api)
2. Click en "New API Key"
3. **Permisos necesarios:**
   - ✅ `wallet:accounts:read` - Ver balances
   - ✅ `wallet:buys:create` - Realizar compras
   - ✅ `wallet:sells:create` - Realizar ventas
   - ✅ `wallet:trades:read` - Ver historial
4. **NO dar permisos de:**
   - ❌ `wallet:accounts:delete`
   - ❌ `wallet:withdrawals:create`
   - ❌ `wallet:transfers:create`
5. Guarda la **API Key** y **API Secret** de forma segura
   - ⚠️ El API Secret solo se muestra UNA VEZ

---

## 🔧 Paso 2: Configurar el Bot

### 2.1 Copiar archivo de configuración

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 2.2 Editar .env con tus credenciales

Abre el archivo `.env` y configura:

```env
# ====================================
# CREDENCIALES (REQUERIDAS para LIVE)
# ====================================
COINBASE_API_KEY=tu_api_key_aqui
COINBASE_API_SECRET=tu_api_secret_aqui

# ====================================
# MODO DE TRADING
# ====================================
TRADING_MODE=SIMULATION
# Cambiar a LIVE solo cuando estés listo

# ====================================
# LÍMITES DE SEGURIDAD
# ====================================
MAX_POSITION_SIZE=100
# Máximo $100 por trade (empieza con poco!)

MAX_DAILY_TRADES=10
# Máximo 10 trades por día

DAILY_LOSS_LIMIT=50
# Para si pierdes más de $50 en un día

# ====================================
# PARÁMETROS DE ESTRATEGIA
# ====================================
TRADING_PAIR=BTC-USD

PROFIT_TARGET=1.5
# 1.5% de profit neto (después de fees)

STOP_LOSS=1.0
# 1% de pérdida máxima por trade

# ====================================
# AUTO TRADING
# ====================================
AUTO_BUY_ENABLED=false
# false = Compras manuales

AUTO_SELL_ENABLED=true
# true = Vende automático en target/stop
```

---

## ✅ Paso 3: Validar Configuración

### 3.1 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3.2 Probar conexión

```bash
python coinbase_api.py
```

**Resultado esperado en SIMULATION:**
```
======================================================================
COINBASE API CONNECTION TEST
======================================================================

Mode: [SIMULATION]

✅ Spot Price: $35,000.00

⚠️  Authenticated endpoints not tested (simulation mode)
======================================================================
```

**Resultado esperado en LIVE (con credenciales correctas):**
```
======================================================================
COINBASE API CONNECTION TEST
======================================================================

Mode: [LIVE]

✅ Spot Price: $35,000.00

✅ Account Balances:
   USD: 1000.00
   BTC: 0.00284
======================================================================
```

---

## 🚀 Paso 4: Comenzar a Operar

### Modo 1: SIMULATION (Recomendado para empezar)

```bash
# En .env
TRADING_MODE=SIMULATION

# Ejecutar bot
python btc_trader.py
```

**En este modo:**
- ✅ Precios reales de Coinbase
- ✅ Todos los cálculos reales
- ✅ Simula compras/ventas
- ❌ NO ejecuta órdenes reales
- ❌ NO gasta dinero real

### Modo 2: LIVE (Trading Real)

⚠️ **Solo cuando estés 100% seguro**

```bash
# En .env
TRADING_MODE=LIVE
MAX_POSITION_SIZE=20  # Empieza con poco!

# Ejecutar bot
python btc_trader.py
```

**En este modo:**
- ✅ Ejecuta órdenes REALES
- ✅ Gasta dinero REAL
- ✅ Compra/vende BTC real
- ⚠️ Riesgo de pérdida real

---

## 🛡️ Seguridad y Mejores Prácticas

### Protección de Credenciales

```bash
# Verificar que .env está en .gitignore
cat .gitignore | grep .env

# Nunca subir .env a Git
git status  # No debe aparecer .env
```

### Límites de Seguridad

```env
# Comienza conservador
MAX_POSITION_SIZE=20       # $20 por trade
MAX_DAILY_TRADES=5         # Solo 5 trades al día
DAILY_LOSS_LIMIT=10        # Para si pierdes $10
```

### Monitoreo

```bash
# Ver logs en tiempo real
python btc_trader.py

# Revisar trades
# (El bot muestra cada operación en consola)
```

---

## 📊 Paso 5: Validar Operación Correcta

### Checklist Pre-Trading:

- [ ] API Keys configuradas correctamente
- [ ] Conexión a Coinbase exitosa
- [ ] Balance de cuenta verificado
- [ ] Límites de seguridad configurados
- [ ] Modo SIMULATION probado primero
- [ ] Entiendes los riesgos

### Primera Operación en LIVE:

1. **Configura límites bajos:**
   ```env
   MAX_POSITION_SIZE=10  # Solo $10
   ```

2. **Monitorea activamente:**
   - Observa la consola
   - Verifica en Coinbase.com
   - Confirma que las órdenes se ejecutan

3. **Aumenta gradualmente:**
   - Si todo funciona bien
   - Incrementa position size poco a poco

---

## 🔧 Troubleshooting

### Error: "Invalid API Key"
```bash
# Verificar que copiaste correctamente
# No debe haber espacios al inicio/final
COINBASE_API_KEY=abc123...  # ✅ Correcto
COINBASE_API_KEY= abc123... # ❌ Espacio extra
```

### Error: "Insufficient permissions"
```bash
# Revisa permisos en Coinbase:
# - wallet:accounts:read
# - wallet:buys:create
# - wallet:sells:create
```

### Error: "Insufficient funds"
```bash
# Verifica balance en Coinbase
# Asegúrate de tener fondos disponibles
# Position size debe ser menor a tu balance
```

### Bot no conecta
```bash
# 1. Verificar internet
ping coinbase.com

# 2. Probar endpoint público
python coinbase_api.py

# 3. Verificar firewall/antivirus
```

---

## ⚠️ Advertencias Importantes

### 🚨 NUNCA:
- ❌ Compartas tus API keys
- ❌ Subas .env a Git/repositorio público
- ❌ Uses API keys en código fuente
- ❌ Des permisos de withdrawal
- ❌ Ignores los límites de seguridad

### ✅ SIEMPRE:
- ✅ Comienza en SIMULATION
- ✅ Usa cantidades pequeñas al inicio
- ✅ Monitorea activamente
- ✅ Entiende los riesgos
- ✅ Ten un plan de salida

---

## 📈 Niveles de Trading Recomendados

### Nivel 1: Beginner (Primera Semana)
```env
TRADING_MODE=SIMULATION
# Solo simulación, aprender el sistema
```

### Nivel 2: Testing (Segunda Semana)
```env
TRADING_MODE=LIVE
MAX_POSITION_SIZE=10
MAX_DAILY_TRADES=2
# Operaciones reales muy pequeñas
```

### Nivel 3: Conservative (Después de un mes exitoso)
```env
TRADING_MODE=LIVE
MAX_POSITION_SIZE=50
MAX_DAILY_TRADES=5
DAILY_LOSS_LIMIT=25
```

### Nivel 4: Regular (Después de 3 meses exitosos)
```env
TRADING_MODE=LIVE
MAX_POSITION_SIZE=100
MAX_DAILY_TRADES=10
DAILY_LOSS_LIMIT=50
```

---

## 📚 Recursos Adicionales

- **Coinbase API Docs:** https://docs.cloud.coinbase.com/
- **API Status:** https://status.coinbase.com/
- **Support:** https://help.coinbase.com/

---

## ✅ Verificación Final

Antes de operar en LIVE, responde:

- [ ] ¿Entiendes cómo funciona el bot?
- [ ] ¿Probaste en SIMULATION exitosamente?
- [ ] ¿Configuraste límites de seguridad?
- [ ] ¿Tienes fondos que puedes arriesgar?
- [ ] ¿Estás monitoreando activamente?
- [ ] ¿Entiendes que puedes perder dinero?

**Si respondiste SÍ a todo, estás listo para trading real.** 

**Si alguna respuesta es NO, quédate en SIMULATION.** 🛡️

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs del bot
2. Verifica configuración en .env
3. Prueba con `python coinbase_api.py`
4. Revisa este documento completo
5. Consulta la documentación de Coinbase

**¡Buena suerte y opera responsablemente!** 🚀
