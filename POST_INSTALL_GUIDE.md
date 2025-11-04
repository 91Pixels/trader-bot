# ✅ CRIPTO-BOT INSTALADO - GUÍA POST-INSTALACIÓN

## 🎉 ¡Felicidades! El instalador se completó exitosamente

---

## 📍 UBICACIÓN DEL PROGRAMA

```
C:\Program Files\Cripto-Bot\
├─ Cripto-Bot.exe           ← Aplicación principal
├─ assets\                  ← Logo e íconos
├─ docs\                    ← Documentación
├─ .env.example             ← Template para configuración
└─ coinbase_ecdsa_key.txt   ← Ejemplo de key file
```

---

## 🔑 PASO 1: CONFIGURAR API KEYS (CRÍTICO)

### **Opción A: Archivo .env (Recomendado)**

1. **Navegar a:** `C:\Program Files\Cripto-Bot\`

2. **Abrir** `.env.example` con Notepad

3. **Editar** con tus credenciales:
   ```env
   COINBASE_API_KEY=organizations/xxx/apiKeys/xxx
   COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----
   MHcCAQEEI...tu_clave_privada_aqui...
   -----END EC PRIVATE KEY-----
   TRADING_MODE=LIVE
   SIMULATION_MODE=False
   ```

4. **Guardar Como:**
   - Nombre: `.env` (QUITAR `.example`)
   - Ubicación: `C:\Program Files\Cripto-Bot\.env`
   - Tipo: Todos los archivos (*.*)

---

### **Opción B: Key File Separado**

Si tienes tu private key en archivo separado:

1. Copia tu archivo `coinbase_ecdsa_key.txt` a:
   ```
   C:\Program Files\Cripto-Bot\coinbase_ecdsa_key.txt
   ```

2. Crea `.env` con:
   ```env
   COINBASE_API_KEY=organizations/xxx/apiKeys/xxx
   COINBASE_PRIVATE_KEY_FILE=coinbase_ecdsa_key.txt
   TRADING_MODE=LIVE
   ```

---

## 🚀 PASO 2: EJECUTAR CRIPTO-BOT

### **Desde Desktop:**
```
Doble-click en: Cripto-Bot (si creaste acceso directo)
```

### **Desde Menú Inicio:**
```
Inicio → Cripto-Bot → Cripto-Bot
```

### **Directamente:**
```
C:\Program Files\Cripto-Bot\Cripto-Bot.exe
```

---

## ✅ VERIFICACIÓN - Primera Ejecución

### **Debe Mostrar:**
```
✅ Found .env at: C:\Program Files\Cripto-Bot\.env
📁 Running as executable, DB path: C:\Program Files\Cripto-Bot\trading_bot.db
✅ Database connected: trading_bot.db
✅ Logo loaded: 200x145px
✅ Window icon set

Connection Status:
🟢 ONLINE - All endpoints working

Coinbase API: ✅ Connected
Balance: Using Real Balance
Mode: LIVE

Endpoints Status:
✅ BTC Price: ONLINE
✅ Wallet Balance: ONLINE
✅ Orders (Buy/Sell): ONLINE
✅ Products: ONLINE
```

---

## ❌ SI NO CONECTA (TROUBLESHOOTING)

### **Error: "Not Connected" / "OFFLINE"**

**Causa:** .env no encontrado o mal configurado

**Solución:**

1. Verifica que existe:
   ```
   C:\Program Files\Cripto-Bot\.env
   ```

2. Verifica contenido (sin espacios extras):
   ```env
   COINBASE_API_KEY=organizations/xxx/apiKeys/xxx
   COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----
   [tu clave privada completa aquí]
   -----END EC PRIVATE KEY-----
   TRADING_MODE=LIVE
   ```

3. **IMPORTANTE:** 
   - NO debe tener extensión `.txt`
   - Debe ser exactamente `.env`
   - Incluir todo el bloqueo de BEGIN/END

---

### **Error: "Invalid credentials format"**

**Causa:** Formato incorrecto de API key

**Solución:**
- API Key debe empezar con: `organizations/`
- Private Key debe tener: `-----BEGIN EC PRIVATE KEY-----`
- Private Key debe terminar con: `-----END EC PRIVATE KEY-----`

---

## 📊 ARCHIVOS GENERADOS

Después de la primera ejecución, verás:

```
C:\Program Files\Cripto-Bot\
├─ .env                     ← Tus API keys (TÚ CREASTE)
├─ trading_bot.db           ← Database (SE CREA AUTO)
└─ Cripto-Bot.exe           ← Aplicación
```

La base de datos `trading_bot.db` se crea automáticamente y guarda:
- Historial de trades
- Posiciones abiertas
- Estadísticas
- Configuraciones

---

## 🎯 USO DEL PROGRAMA

### **Primer Uso - Modo SIMULATION (Recomendado):**

1. En `.env` configura:
   ```env
   TRADING_MODE=SIMULATION
   ```

2. Prueba el bot sin riesgo

3. Cuando estés listo, cambia a:
   ```env
   TRADING_MODE=LIVE
   ```

---

### **Trading Tab:**
```
✅ Precio en tiempo real (WebSocket)
✅ Configuración de profit/stop-loss
✅ Auto Buy/Sell configuración
✅ Posición actual y calculadora de profit
✅ Balance real de Coinbase
✅ Estadísticas de trading
✅ Botones manuales Buy/Sell
```

---

### **Configuration Tab:**
```
✅ API keys management
✅ Test connection
✅ Trading mode (SIMULATION/LIVE)
✅ Safety limits
✅ Auto-trading settings
```

---

### **Buying Testing Tab:**
```
✅ Test manual buy
✅ Test manual sell
✅ Ver balance después de test
```

---

## 🗑️ DESINSTALAR

Si necesitas desinstalar:

### **Método 1: Panel de Control**
```
1. Panel de Control
2. Programas y características
3. Buscar "Cripto-Bot"
4. Click "Desinstalar"
```

### **Método 2: Menú Inicio**
```
Inicio → Cripto-Bot → Uninstall Cripto-Bot
```

**Qué se elimina:**
- ✅ Programa completo
- ✅ Accesos directos
- ⚠️ `.env` (opcional - pregunta)
- ⚠️ `trading_bot.db` (opcional - pregunta)

---

## 🔄 ACTUALIZAR A NUEVA VERSIÓN

Cuando haya una actualización:

1. Desinstalar versión actual
2. Instalar nueva versión
3. Copiar tu `.env` de respaldo
4. La database se preserva automáticamente

---

## 🎨 CARACTERÍSTICAS

```
✅ Logo profesional 200x145px
✅ Version: 1.0 Beta
✅ Creator: Michael Camacho
✅ License: 91pixelsusa@gmail.com
✅ Tema oscuro moderno
✅ Botones amarillos (#ffc107)
✅ Responsive design
✅ Iconos de ayuda "?" en cada sección
✅ Real-time WebSocket price feed
✅ Automatic target calculation (2.5% profit)
✅ Stop-loss protection
✅ Database persistence
```

---

## 📞 SOPORTE

**Email:** 91pixelsusa@gmail.com

**Documentación:**
- `C:\Program Files\Cripto-Bot\docs\README.md`
- `C:\Program Files\Cripto-Bot\docs\MANUAL_TEST_CASES_ES.md`

---

## ⚠️ ADVERTENCIAS IMPORTANTES

1. **SEGURIDAD:**
   - NUNCA compartas tu archivo `.env`
   - Mantén tus API keys seguras
   - No uses screenshot del .env

2. **TRADING:**
   - Empezar con SIMULATION mode
   - Trading de cryptos tiene riesgo
   - Usa solo dinero que puedas perder
   - 2.5% profit por trade (después de fees)

3. **API PERMISSIONS:**
   - Necesitas permisos de trading en Coinbase
   - Verifica que tu API key tenga permisos

---

## ✅ CHECKLIST FINAL

Antes de operar, verifica:

- [ ] Cripto-Bot instalado en Program Files
- [ ] `.env` creado con tus API keys
- [ ] Bot ejecuta sin errores
- [ ] Connection Status: 🟢 ONLINE
- [ ] Balance real visible
- [ ] Precio BTC actualizándose
- [ ] Probado en SIMULATION mode
- [ ] Listo para LIVE trading

---

## 🎉 ¡LISTO PARA OPERAR!

Tu bot está completamente instalado y configurado como un programa profesional de Windows.

**Ubicaciones clave:**
- 📁 Programa: `C:\Program Files\Cripto-Bot\`
- 🔑 Config: `C:\Program Files\Cripto-Bot\.env`
- 💾 Database: `C:\Program Files\Cripto-Bot\trading_bot.db`
- 🚀 Ejecutable: Desktop o Menú Inicio

---

**¡Feliz Trading!** 📈✨

**Cripto-Bot v1.0 Beta**  
**Created by Michael Camacho**  
**License: 91pixelsusa@gmail.com**
