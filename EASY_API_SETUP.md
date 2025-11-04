# ✅ CONFIGURACIÓN FÁCIL DE API DESDE LA UI

## 🎯 NUEVA FUNCIONALIDAD

Ahora puedes ingresar tus credenciales de Coinbase **directamente desde el programa** sin editar archivos manualmente!

---

## 📋 PASOS PARA CONFIGURAR API KEYS

### **1. Abrir Cripto-Bot**
```
Ejecuta desde Desktop o Menú Inicio
```

### **2. Ir a Configuration Tab**
```
Click en: ⚙️ Configuration
```

### **3. Editar API Key**

1. **Localiza** la sección "🔐 API Configuration"
2. **Click** en el botón **✏️** junto a "API Key"
3. El campo se limpiará y estará listo para editar
4. **Pega** tu `COINBASE_API_KEY`
   ```
   organizations/xxxxx/apiKeys/xxxxx
   ```

### **4. Editar API Secret**

1. **Click** en el botón **✏️** junto a "API Secret"
2. El campo se limpiará y estará listo para editar
3. **Pega** tu `COINBASE_API_SECRET` completo
   ```
   -----BEGIN EC PRIVATE KEY-----
   MHcCAQEEI...tu_clave_privada_completa...
   -----END EC PRIVATE KEY-----
   ```
   **IMPORTANTE:** Incluye las líneas BEGIN/END completas

### **5. Seleccionar Trading Mode**

- ⚪ **SIMULATION** - Para pruebas sin riesgo
- 🔴 **LIVE** - Para trading real

### **6. Guardar Configuración**

**Click en:** `💾 Save Configuration to .env`

El programa:
- ✅ Guardará las credenciales en `.env`
- ✅ Recargará la configuración automáticamente
- ✅ Mostrará un mensaje de confirmación

---

## 🎨 CARACTERÍSTICAS DE LA INTERFAZ

### **Botones Disponibles:**

| Botón | Función |
|-------|---------|
| **👁️** | Ver/Ocultar credencial (toggle) |
| **✏️** | Editar credencial (limpia campo) |
| **💾 Save Configuration** | Guardar cambios a .env |
| **🔄 Reload Configuration** | Recargar desde .env |
| **🧪 Test API Connection** | Probar conexión |

---

## 📊 EJEMPLO DE USO

### **Paso a Paso Visual:**

```
1. Configuration Tab
   └─ 🔐 API Configuration
      
2. API Key: org*************************xxx
   [👁️] [✏️] ← Click aquí para editar
   
3. Campo se limpia: [ ]
   
4. Pega tu key: [organizations/xxxxx/apiKeys/xxxxx]
   
5. API Secret: -----*************************-----
   [👁️] [✏️] ← Click aquí para editar
   
6. Campo se limpia: [ ]
   
7. Pega tu secret completo (con BEGIN/END)
   
8. Trading Mode:
   ⚪ SIMULATION  🔴 LIVE
   
9. Click: [💾 Save Configuration to .env]

10. ✅ Mensaje de confirmación
```

---

## ✅ VERIFICACIÓN

### **Después de Guardar:**

1. **Mensaje Popup:**
   ```
   ✅ Configuration saved successfully!
   
   Location: C:\Program Files\Cripto-Bot\.env
   Trading Mode: LIVE
   
   The API connection has been reloaded.
   Click 'Test API Connection' to verify.
   ```

2. **Click en:** `🧪 Test API Connection`

3. **Debe Mostrar:**
   ```
   🟢 ONLINE - All endpoints working
   
   Endpoints Status:
   📊 BTC Price: 🟢 ONLINE ($107,234.56)
   💰 Wallet Balance: 🟢 ONLINE
   📝 Orders (Buy/Sell): 🟢 ONLINE
   📈 Products: 🟢 ONLINE
   ```

---

## 🔄 ARCHIVO .ENV GENERADO

El programa creará/actualizará automáticamente:

**Ubicación:**
```
C:\Program Files\Cripto-Bot\.env
```

**Contenido:**
```env
COINBASE_API_KEY=organizations/xxxxx/apiKeys/xxxxx
COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----
MHcCAQEEI...
-----END EC PRIVATE KEY-----
TRADING_MODE=LIVE
SIMULATION_MODE=False
```

---

## 💡 TIPS

### **Formato Correcto:**

✅ **API Key debe empezar con:**
```
organizations/
```

✅ **API Secret debe incluir:**
```
-----BEGIN EC PRIVATE KEY-----
[contenido de la clave]
-----END EC PRIVATE KEY-----
```

### **Errores Comunes:**

❌ **No incluir BEGIN/END:**
```
MHcCAQEEI...  ← INCORRECTO
```

✅ **Incluir TODO:**
```
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEI...
-----END EC PRIVATE KEY-----  ← CORRECTO
```

---

## 🛡️ SEGURIDAD

### **El programa:**
- ✅ Muestra las credenciales enmascaradas por defecto
- ✅ Guarda el .env en la carpeta del programa
- ✅ NO envía credenciales a ningún servidor externo
- ✅ Solo se usan para conectar con Coinbase API

### **Recomendaciones:**
- 🔒 Mantén tu .env privado
- 🔒 No compartas screenshots con credenciales visibles
- 🔒 Usa SIMULATION mode primero para probar

---

## 🔧 TROUBLESHOOTING

### **"Not Connected" después de guardar:**

**Causa:** Formato incorrecto de credenciales

**Solución:**
1. Click **✏️** para editar de nuevo
2. Verifica que API Key empieza con `organizations/`
3. Verifica que API Secret tiene `-----BEGIN` y `-----END`
4. Pega de nuevo las credenciales completas
5. **Save** y **Test Connection**

### **"OFFLINE" en endpoints:**

**Causa:** Credenciales inválidas o sin permisos

**Solución:**
1. Verifica en Coinbase que el API Key existe
2. Verifica que tiene permisos de trading
3. Regenera las credenciales si es necesario
4. Pega las nuevas en el programa
5. **Save** y **Test Connection**

---

## 📊 VENTAJAS DEL NUEVO MÉTODO

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Método** | Editar .env manualmente | UI interactiva ✅ |
| **Ubicación** | Buscar archivo | Click en botón ✅ |
| **Validación** | Manual | Automática ✅ |
| **Test** | Reiniciar programa | Click "Test" ✅ |
| **Errores** | Difícil detectar | Mensajes claros ✅ |

---

## ✅ RESUMEN EJECUTIVO

```
1. Abrir Cripto-Bot
2. Tab "Configuration"
3. Click ✏️ en API Key → Pegar
4. Click ✏️ en API Secret → Pegar
5. Seleccionar SIMULATION o LIVE
6. Click "Save Configuration"
7. Click "Test API Connection"
8. ✅ Listo!
```

**Tiempo estimado:** 2 minutos ⏱️

---

## 🎯 PRÓXIMOS PASOS

Después de configurar:

1. ✅ Verificar que Connection Status = 🟢 ONLINE
2. ✅ Probar con SIMULATION mode primero
3. ✅ Ver Trading Tab para monitorear precio
4. ✅ Cuando estés listo, cambiar a LIVE mode
5. ✅ ¡A operar!

---

**¡Ahora configurar tus credenciales es super fácil!** 🎉

**No más editar archivos manualmente** ✅  
**No más buscar archivos .env** ✅  
**Todo desde la interfaz del programa** ✅

---

**Cripto-Bot v1.0 Beta**  
**Created by Michael Camacho**  
**License: 91pixelsusa@gmail.com**
