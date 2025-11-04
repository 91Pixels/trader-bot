# 🧪 Pruebas Manuales del BTC Trading Bot

**Versión:** 1.0  
**Fecha:** Noviembre 3, 2025  
**Idioma:** Español

---

## 📋 Índice de Pruebas

1. [Inicio y Conexión](#1-inicio-y-conexión)
2. [Sincronización de Entry Price](#2-sincronización-de-entry-price)
3. [Carga de Sesión desde DB](#3-carga-de-sesión-desde-db)
4. [Auto-Save](#4-auto-save)
5. [Cálculo de Target](#5-cálculo-de-target)
6. [Auto Buy](#6-auto-buy)
7. [Auto Sell](#7-auto-sell)
8. [Exportar Reporte HTML](#8-exportar-reporte-html)
9. [Persistencia de Datos](#9-persistencia-de-datos)
10. [Validación de Fees](#10-validación-de-fees)

---

## 1. Inicio y Conexión

### **Objetivo:** Verificar que el bot inicia correctamente y se conecta a Coinbase

### **Pasos:**

1. Abre una terminal en la carpeta del proyecto
2. Ejecuta: `python btc_trader.py`
3. Espera 10 segundos

### **Resultado Esperado:**

```
✅ Database connected: trading_bot.db
✅ Real balance loaded:
   USD: $[amount]
   BTC: [amount]
✅ WebSocket connected to Coinbase
📡 Subscribed to BTC-USD ticker
```

### **Verificar en UI:**

- [ ] Precio BTC se actualiza en tiempo real
- [ ] Estado "✅ WebSocket Conectado" visible
- [ ] Latency < 100ms
- [ ] Balance de Coinbase cargado correctamente

### **Criterios de Éxito:**

✅ Bot abre ventana GUI  
✅ WebSocket conectado  
✅ Balance real cargado  
✅ Precio actualizándose

### **Falla Si:**

❌ Error de conexión a Coinbase  
❌ WebSocket no conecta  
❌ GUI no abre  
❌ Balance no carga

---

## 2. Sincronización de Entry Price

### **Objetivo:** Sincronizar el Entry Price desde Coinbase manualmente

### **Pre-requisitos:**

- Bot iniciado
- Coinbase conectado
- Tener BTC en balance

### **Pasos:**

1. Abre la app de Coinbase en tu teléfono/navegador
2. Ve a tus holdings de BTC
3. Copia el valor de **"Avg Entry"** (ej: $112,413.63)
4. En el bot, ve a **"Auto Sell Configuration"**
5. Busca **"🔗 Sync Avg Entry from Coinbase:"**
6. Pega el valor en el campo **"Coinbase Avg Entry ($)"**
7. Click en **"✅ Set & Calculate Target"**

### **Resultado Esperado en Console:**

```
======================================================================
🔗 COINBASE AVG ENTRY SYNCHRONIZED
======================================================================
Entry Price:          $112,413.63
BTC Amount:           0.00006117
Cost Basis:           $6.88

📊 Calculating Auto Sell Target:
   Buy Fee:           0.6%
   Sell Fee:          0.6%
   Desired Profit:    2.5%

   🎯 Calculation:
      Cost Basis:     $6.88
      Desired Net:    $7.05 (+2.5%)
      Before Fee:     $7.09
      Target Price:   $115,919.49

======================================================================
✅ AUTO SELL TARGET CALCULATED:
======================================================================
Entry:                $112,413.63
Target:               $115,919.49 (+3.12%)
Expected Profit:      $0.17 (2.5%)
======================================================================

💾 Auto-saved to database: Entry $112,413.63
```

### **Verificar en UI:**

- [ ] Campo "Coinbase Avg Entry" muestra el valor ingresado
- [ ] Label azul muestra: "📊 Entry from Coinbase: $[price] | Target: $[price]"
- [ ] Campo "Sell when price reaches" muestra el target
- [ ] Sección "Current Position" muestra Entry correcto
- [ ] Target Price verde muestra valor correcto

### **Criterios de Éxito:**

✅ Entry se sincroniza  
✅ Target se calcula automáticamente  
✅ Se guarda en DB  
✅ UI se actualiza  
✅ Console muestra cálculos

### **Falla Si:**

❌ Entry no se acepta  
❌ Target no se calcula  
❌ Error en console  
❌ UI no se actualiza

---

## 3. Carga de Sesión desde DB

### **Objetivo:** Cargar la última sesión guardada desde la base de datos

### **Pre-requisitos:**

- Haber guardado una sesión previamente (Prueba #2)
- Bot cerrado y reabierto

### **Pasos:**

1. Cierra el bot (X en ventana)
2. Espera 3 segundos
3. Reabre el bot: `python btc_trader.py`
4. Espera a que cargue completamente
5. Ve a **"Auto Sell Configuration"**
6. Busca **"💾 Database Session:"**
7. Click en **"📂 Load Last Saved Session"**

### **Resultado Esperado en Console:**

```
======================================================================
📂 LOADING LAST SAVED SESSION FROM DATABASE
======================================================================

📊 SESSION DATA RETRIEVED:
   Saved: 2025-11-03 12:28:45
   Loaded: 2025-11-03 12:51:30
   Entry Price: $112,413.63
   Position Size: $6.88
   BTC Amount: 0.00006117
   Target Price: $115,919.49
   Stop Loss: $111,289.49

======================================================================
✅ SESSION LOADED SUCCESSFULLY
======================================================================
🎯 Entry Price: $112,413.63
🎯 Target Price: $115,919.49 (+3.12%)
💾 Saved on: 2025-11-03 12:28:45
🕐 Loaded on: 2025-11-03 12:51:30
======================================================================
```

### **Verificar en UI:**

- [ ] Popup muestra: "✅ Last session loaded successfully!"
- [ ] Popup incluye timestamp de "Saved" y "Loaded"
- [ ] Label debajo del botón muestra: "🕐 Last Load: [timestamp]"
- [ ] Entry price se carga en campos
- [ ] Target price se carga en campos

### **Criterios de Éxito:**

✅ Sesión se carga desde DB  
✅ Todos los datos coinciden  
✅ Timestamp de load se muestra  
✅ Popup de confirmación aparece  
✅ UI se actualiza correctamente

### **Falla Si:**

❌ "No session found"  
❌ Datos incorrectos  
❌ Timestamp no se muestra  
❌ Error en carga

---

## 4. Auto-Save

### **Objetivo:** Verificar que los datos se guardan automáticamente al cambiar

### **Pre-requisitos:**

- Bot iniciado
- Entry price configurado

### **Pasos:**

1. Sincroniza un entry price (Prueba #2)
2. Observa la console
3. Busca mensaje de auto-save

### **Resultado Esperado:**

```
💾 Auto-saved to database: Entry $112,413.63
```

### **Verificar:**

- [ ] Mensaje "Auto-saved" aparece después de sincronizar
- [ ] No se requiere acción manual para guardar
- [ ] Cada cambio genera un auto-save

### **Criterios de Éxito:**

✅ Auto-save se ejecuta automáticamente  
✅ Mensaje visible en console  
✅ Sin intervención del usuario

### **Falla Si:**

❌ No aparece mensaje de auto-save  
❌ Requiere save manual  
❌ Datos no se guardan

---

## 5. Cálculo de Target

### **Objetivo:** Verificar que el target se calcula correctamente con fees incluidos

### **Pre-requisitos:**

- Entry price conocido
- BTC balance conocido

### **Datos de Prueba:**

```
Entry: $112,413.63
BTC Amount: 0.00006117
Cost Basis: $6.88
Profit Target: 2.5%
Buy Fee: 0.6%
Sell Fee: 0.6%
```

### **Pasos:**

1. Ingresa entry price
2. Click "Set & Calculate Target"
3. Anota el target calculado

### **Cálculo Manual:**

```
1. Desired Net = $6.88 × 1.025 = $7.052
2. Required Gross = $7.052 / 0.994 = $7.094
3. Target Price = $7.094 / 0.00006117 = $115,919.49
```

### **Resultado Esperado:**

```
Target Price: $115,919.49
Expected Profit: $0.17 (2.5%)
```

### **Verificar:**

- [ ] Target = $115,919.49 (±$1)
- [ ] Profit = $0.17 (±$0.01)
- [ ] Incremento = +3.12% desde entry
- [ ] Fórmula incluye ambos fees

### **Criterios de Éxito:**

✅ Target correcto (±$1)  
✅ Profit = 2.5% neto  
✅ Fees incluidos  
✅ Matemáticas correctas

### **Falla Si:**

❌ Target incorrecto  
❌ Profit ≠ 2.5%  
❌ Fees no incluidos  
❌ Error de cálculo

---

## 6. Auto Buy

### **Objetivo:** Verificar que Auto Buy se activa y funciona correctamente

### **Pre-requisitos:**

- Bot iniciado
- Balance BTC = 0 (sin posición abierta)
- Precio actual conocido

### **Pasos:**

1. Ve a **"Auto Buy Configuration"**
2. Click checkbox **"Enable Auto Buy"**
3. Observa que se auto-calcula precio (Current -1%)
4. Verifica estado: **"🟢 Auto Buy: ACTIVE at $[price]"**

### **Resultado Esperado:**

```
🤖 Auto Buy ENABLED:
   Current Price: $106,590.77
   Auto Buy Price: $105,554.70 (-1% safety margin)
   💡 Strategy: Buy when price dips 1% below current
```

### **Verificar en UI:**

- [ ] Checkbox marcado
- [ ] Precio trigger calculado automáticamente
- [ ] Status muestra "🟢 Auto Buy: ACTIVE"
- [ ] Campo de precio deshabilitado (gris)

### **Condiciones de Trigger:**

```
✅ Auto Buy ejecutará SI:
   • Balance BTC = 0
   • Precio actual ≤ Trigger price
   • Auto Buy enabled
```

### **Criterios de Éxito:**

✅ Auto Buy se activa  
✅ Precio se calcula automáticamente  
✅ Status se actualiza  
✅ UI refleja estado activo

### **Falla Si:**

❌ No se activa  
❌ Precio no se calcula  
❌ Status incorrecto  
❌ Checkbox no funciona

---

## 7. Auto Sell

### **Objetivo:** Verificar que Auto Sell se configura y activa correctamente

### **Pre-requisitos:**

- Bot iniciado
- Entry price configurado
- Balance BTC > 0 (posición abierta)

### **Pasos:**

1. Ve a **"Auto Sell Configuration"**
2. Click checkbox **"Enable Auto Sell"**
3. Verifica que usa el target calculado automáticamente
4. Observa status: **"🟢 Auto Sell: ACTIVE at $[price]"**

### **Resultado Esperado en Console:**

```
🤖 Auto Sell ENABLED:
   Entry Price: $112,413.63
   Target Price: $115,919.49 (+3.12%)
   Expected Net Profit: $0.17 (2.5%)
   💡 Strategy: Sell at calculated target for 2.5% profit
```

### **Verificar en UI:**

- [ ] Checkbox marcado
- [ ] Campo "Sell when price reaches" muestra target
- [ ] Status muestra "🟢 Auto Sell: ACTIVE at $[price]"
- [ ] Label muestra entry y target

### **Condiciones de Trigger:**

```
✅ Auto Sell ejecutará SI:
   • Balance BTC > 0
   • Precio actual ≥ Target price
   • Auto Sell enabled
```

### **Criterios de Éxito:**

✅ Auto Sell se activa  
✅ Target correcto  
✅ Status actualizado  
✅ Condiciones verificadas

### **Falla Si:**

❌ No se activa  
❌ Target incorrecto  
❌ Status no cambia  
❌ Checkbox no funciona

---

## 8. Exportar Reporte HTML

### **Objetivo:** Generar y exportar un reporte HTML de trading

### **Pre-requisitos:**

- Bot iniciado
- Al menos 1 trade en historial (opcional)

### **Pasos:**

1. En el tab **"Trading"**
2. Busca el botón **"📊 Export HTML Report"**
3. Click en el botón
4. Observa la console
5. Espera el popup de confirmación
6. Click **"Yes"** para abrir el reporte

### **Resultado Esperado en Console:**

```
📊 Generating HTML report...
✅ Report saved: C:\Users\...\btc_trading_report_20251103_125145.html
🌐 Opening report in browser...
```

### **Verificar:**

- [ ] Popup pregunta: "Would you like to open it now?"
- [ ] Archivo HTML se crea en la carpeta del proyecto
- [ ] Nombre formato: `btc_trading_report_YYYYMMDD_HHMMSS.html`
- [ ] Reporte se abre en navegador (si aceptas)
- [ ] HTML muestra estadísticas y trades

### **Contenido del Reporte HTML:**

- [ ] Header con título "BTC Trading Report"
- [ ] Timestamp de generación
- [ ] Estadísticas: Total trades, Win rate, Profit
- [ ] Tabla con historial de trades
- [ ] Diseño responsive y profesional

### **Criterios de Éxito:**

✅ Archivo HTML se genera  
✅ Contiene datos correctos  
✅ Se abre en navegador  
✅ Diseño profesional

### **Falla Si:**

❌ Error al generar  
❌ Archivo no se crea  
❌ HTML corrupto  
❌ No se puede abrir

---

## 9. Persistencia de Datos

### **Objetivo:** Verificar que los datos persisten entre reinicios

### **Pre-requisitos:**

- Entry price configurado
- Sesión guardada

### **Pasos:**

1. Configura entry price: $112,413.63
2. Observa mensaje "Auto-saved"
3. Cierra el bot completamente (X)
4. Espera 5 segundos
5. Reabre el bot: `python btc_trader.py`
6. Espera que cargue completamente
7. Click "Load Last Saved Session"
8. Compara datos

### **Datos a Verificar:**

| Dato | Antes de Cerrar | Después de Reabrir |
|------|----------------|-------------------|
| Entry Price | $112,413.63 | $112,413.63 ✅ |
| Target Price | $115,919.49 | $115,919.49 ✅ |
| BTC Amount | 0.00006117 | 0.00006117 ✅ |
| Position Size | $6.88 | $6.88 ✅ |

### **Verificar en Console:**

```
✅ Entry price restored from DB: $112,413.63
```

### **Criterios de Éxito:**

✅ Todos los datos coinciden  
✅ Entry price persiste  
✅ Target persiste  
✅ No se pierde información

### **Falla Si:**

❌ Datos diferentes  
❌ Entry no persiste  
❌ Sesión no se carga  
❌ Error de DB

---

## 10. Validación de Fees

### **Objetivo:** Verificar que los fees se calculan e incluyen correctamente

### **Pre-requisitos:**

- Entry price configurado
- Conocer fees configurados

### **Datos de Configuración:**

```
Buy Fee: 0.6%
Sell Fee: 0.6%
Profit Target: 2.5%
```

### **Pasos:**

1. Ve a **"Current Position & Profit Calculator"**
2. Verifica los valores mostrados
3. Compara con cálculo manual

### **Cálculo Manual:**

```
Entry: $112,413.63
BTC: 0.00006117
Cost Basis: $6.88

Target Calculation:
1. Desired Net = $6.88 × 1.025 = $7.052
2. Gross Before Fee = $7.052 / (1 - 0.006) = $7.094
3. Target Price = $7.094 / 0.00006117 = $115,919.49

At Target:
Value at Target = 0.00006117 × $115,919.49 = $7.09
Sell Fee = $7.09 × 0.006 = $0.04
Net Proceeds = $7.09 - $0.04 = $7.05
Profit = $7.05 - $6.88 = $0.17 (2.5%)
```

### **Verificar en UI:**

- [ ] Buy Fee (0.6%): $0.00 (ya comprado)
- [ ] Sell Fee (0.6%): $0.04
- [ ] Final Profit: $0.17 (verde)
- [ ] Profit %: 2.5%

### **Criterios de Éxito:**

✅ Fees se incluyen en cálculos  
✅ Profit neto = 2.5%  
✅ Matemáticas correctas  
✅ UI muestra fees correctamente

### **Falla Si:**

❌ Fees no incluidos  
❌ Profit ≠ 2.5%  
❌ Cálculo incorrecto  
❌ UI muestra datos erróneos

---

## 📊 Resumen de Pruebas

### **Checklist General:**

- [ ] 1. Inicio y Conexión
- [ ] 2. Sincronización de Entry Price
- [ ] 3. Carga de Sesión desde DB
- [ ] 4. Auto-Save
- [ ] 5. Cálculo de Target
- [ ] 6. Auto Buy
- [ ] 7. Auto Sell
- [ ] 8. Exportar Reporte HTML
- [ ] 9. Persistencia de Datos
- [ ] 10. Validación de Fees

### **Criterio de Aprobación:**

✅ **PASS**: 10/10 pruebas exitosas  
⚠️ **WARNING**: 8-9/10 pruebas exitosas  
❌ **FAIL**: <8/10 pruebas exitosas

---

## 🐛 Reporte de Bugs

**Si encuentras un bug, reporta:**

1. **Prueba que falló**: [Nombre]
2. **Paso específico**: [Número]
3. **Resultado obtenido**: [Descripción]
4. **Resultado esperado**: [Descripción]
5. **Screenshot**: [Si es posible]
6. **Console output**: [Copy/paste]
7. **Timestamp**: [Cuando ocurrió]

---

## ✅ Firma de Pruebas

**Probado por**: _________________  
**Fecha**: _________________  
**Versión del Bot**: _________________  
**Resultado**: ⬜ PASS  ⬜ WARNING  ⬜ FAIL  

**Comentarios adicionales:**

_________________________________________________

_________________________________________________

_________________________________________________

---

**Fin del Documento de Pruebas Manuales**
