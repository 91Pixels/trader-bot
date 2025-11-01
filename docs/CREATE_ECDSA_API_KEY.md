# 🔑 Crear API Key Correcta para Advanced Trade API

## ❌ Problema Actual

Tu API Key "Bot2" fue creada con:
```
Algoritmo de firma: Ed25519
Formato de clave: Base64 (euydfD2s5O0y8db...)
```

**Esto NO funciona** con Advanced Trade API.

---

## ✅ Solución: Crear Nueva API Key con ECDSA

### Documentación Oficial:
https://docs.cdp.coinbase.com/coinbase-app/authentication-authorization/api-key-authentication

**Cita textual:**
> "Required: Change signature algorithm to ECDSA. 
> Do NOT select Ed25519 as it is not supported by Coinbase App APIs."

---

## 📋 Paso a Paso

### Paso 1: Ir al Portal

```
https://portal.cdp.coinbase.com/projects/api-keys
```

### Paso 2: Create API Key

Click en el botón **"Create API key"**

### Paso 3: Configuración Básica

```
API key nickname: TradingBot_ECDSA
```

### Paso 4: API Restrictions

**Expand "API restrictions"**

Seleccionar permisos:
```
✅ View   (ver balances, órdenes, historial)
✅ Trade  (comprar/vender, crear órdenes)
❌ Transfer  (NO marcar - muy peligroso)
```

### Paso 5: Advanced Settings ⚠️ **MÁS IMPORTANTE**

**Expand "Advanced Settings"**

#### IP Allowlist:
```
24.157.20.150
```

#### Signature Algorithm: ⚠️ **CRÍTICO**

```
⚠️⚠️⚠️ SELECCIONAR: ECDSA
❌❌❌ NO SELECCIONAR: Ed25519
```

**Esto es LO MÁS IMPORTANTE. Si seleccionas Ed25519, NO funcionará.**

### Paso 6: Create

Click en **"Create API key"**

### Paso 7: Descargar Credenciales

Se descargará automáticamente un archivo JSON.

**Formato esperado del archivo:**

```json
{
  "name": "TradingBot_ECDSA",
  "privateKey": "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIxyz...\n-----END EC PRIVATE KEY-----"
}
```

**O formato alternativo:**

```json
{
  "keyName": "organizations/abc-123/apiKeys/def-456",
  "privateKey": "-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----"
}
```

### Paso 8: Guardar Archivo

**Guarda el archivo en:**
```
C:\Users\393di\Desktop\Cripto-Agent\coinbase_ecdsa_key.json
```

### Paso 9: Configurar en el Bot

Abre el archivo JSON y copia el contenido completo aquí en el chat.

---

## 🔍 Cómo Verificar que Está Correcto

### Características de la Clave CORRECTA:

1. ✅ **privateKey** empieza con: `-----BEGIN EC PRIVATE KEY-----`
2. ✅ **privateKey** termina con: `-----END EC PRIVATE KEY-----`
3. ✅ Tiene múltiples líneas separadas por `\n`
4. ✅ **keyName** tiene formato: `organizations/xxx/apiKeys/yyy`

### Características de la Clave INCORRECTA (Ed25519):

1. ❌ **privateKey** es solo Base64: `euydfD2s5O0y8db...`
2. ❌ **id** en vez de **keyName**
3. ❌ Formato corto sin BEGIN/END

---

## 📊 Comparación Visual

### ❌ INCORRECTO (Ed25519 - Bot2 actual):

```json
{
  "id": "7b2c3267-51f6-4c7b-987e-c72230022eda",
  "privateKey": "euydfD2s5O0y8db96sPw7/vZV8bX280CDjTLWHwXyLI..."
}
```

### ✅ CORRECTO (ECDSA - lo que necesitas):

```json
{
  "name": "TradingBot_ECDSA",
  "privateKey": "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIBRq3FwXZ8YrUW5pnvKLM9X2jN4hQ7RsT1VbU8wP9yKZ\noAoGCCqGSM49AwEHoUQDQgAE7i9kP2mL5nR8wQxT3vUoK1pY\n7jH9sN2cW5eF4rT6qX8dL3mY9pK1wN5vR7sT8mP4kL2nW9\nxY3jF5qR8tL7mP2g==\n-----END EC PRIVATE KEY-----"
}
```

---

## ⚠️ Notas Importantes

### 1. Signature Algorithm es LO MÁS CRÍTICO

```
Si seleccionas Ed25519:
  ❌ NO funcionará con Advanced Trade API
  ❌ Solo funciona con CDP SDK (blockchain)
  ❌ No puedes comprar/vender en el exchange

Si seleccionas ECDSA:
  ✅ Funciona con Advanced Trade API
  ✅ Puedes comprar/vender en el exchange
  ✅ Trading bot funcionará
```

### 2. No Confundir APIs

```
CDP SDK API:
  - Usa Ed25519
  - Para blockchain operations
  - cdp.evm.create_account()
  
Advanced Trade API:
  - Usa ECDSA
  - Para exchange trading
  - /api/v3/brokerage/accounts
```

### 3. Formato de Clave

La clave privada en formato PEM tiene estas características:

```
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEI...  (línea 1 del contenido)
BRq3FwXZ8Y...  (línea 2 del contenido)
...
-----END EC PRIVATE KEY-----
```

En JSON se representa con `\n`:

```
"-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEI...\nBRq3FwXZ8Y...\n-----END EC PRIVATE KEY-----"
```

---

## 🚀 Una Vez Creada la API Key

### Paso 1: Pegar Contenido del JSON Aquí

Abre el archivo descargado y copia **TODO** el contenido.

### Paso 2: Yo Configuraré el Bot

Actualizaré automáticamente:
- `.env` con las nuevas credenciales
- Formato correcto para JWT authentication
- Testing scripts

### Paso 3: Probar Conexión

```bash
python coinbase_advanced_trade_jwt.py
```

**Resultado esperado:**
```
✅ JWT Format: ECDSA (correct)
✅ Public API works: BTC = $109,xxx.xx
✅ Authentication works!
   Balances: {'USD': xxx.xx, 'BTC': x.xxxx}
```

### Paso 4: Ejecutar Tests

```bash
python tests/run_all_tests.py
```

**Resultado esperado:**
```
62/62 tests PASSED ✅
```

### Paso 5: Iniciar Trading

```bash
python btc_trader.py
```

---

## ⏱️ Timeline

```
1. Crear API key ECDSA:          3 minutos
2. Descargar y pegar JSON:       1 minuto
3. Configurar en bot:            1 minuto (automático)
4. Probar conexión:              30 segundos
5. Bot funcionando:              ✅

TOTAL: ~5 minutos
```

---

## 🆘 Si Tienes Problemas

### Error: "No encuentro opción de ECDSA"

**Solución:** Debes expandir "Advanced Settings" en el formulario de creación de API key.

### Error: "Solo veo Ed25519"

**Solución:** Asegúrate de estar en la sección correcta:
- ✅ Correcto: "Secret API Keys" → "Create API key"
- ❌ Incorrecto: CDP SDK settings

### Error: "Descargué pero no tiene format PEM"

**Solución:** Verifica que seleccionaste ECDSA (no Ed25519).
Si es Ed25519, borra esa key y crea una nueva con ECDSA.

---

## ✅ Checklist Final

Antes de crear la API key, verifica:

- [ ] Estoy en: https://portal.cdp.coinbase.com/projects/api-keys
- [ ] Click en "Create API key"
- [ ] Nickname: TradingBot_ECDSA
- [ ] Permissions: View ✅, Trade ✅, Transfer ❌
- [ ] IP allowlist: 24.157.20.150
- [ ] **⚠️ Advanced Settings expandido**
- [ ] **⚠️ Signature algorithm: ECDSA (NO Ed25519)**
- [ ] Click "Create API key"
- [ ] Archivo JSON descargado
- [ ] privateKey empieza con "-----BEGIN EC PRIVATE KEY-----"

---

**Una vez que tengas el archivo JSON con formato ECDSA (PEM), pégalo aquí y configuraré todo automáticamente.** 🚀
