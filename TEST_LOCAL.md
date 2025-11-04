# 🧪 PRUEBA LOCAL - CONFIGURACIÓN DE API

## ✅ PASOS PARA PROBAR

### **1. El programa está ejecutándose**
```
python btc_trader.py ya se ejecutó
```

### **2. Ir a Configuration Tab**
```
Click en: ⚙️ Configuration
```

### **3. Probar Editar API Key**

1. **Click en ✏️** junto a "API Key"
2. El campo debe **limpiarse** y quedar vacío
3. **Pega** una API Key de prueba (o tu real):
   ```
   organizations/test123/apiKeys/abc123
   ```
4. Presiona Tab o click fuera del campo

### **4. Probar Editar API Secret**

1. **Click en ✏️** junto a "API Secret"
2. El campo debe **limpiarse** y quedar vacío
3. **Pega** un secret de prueba (o tu real):
   ```
   -----BEGIN EC PRIVATE KEY-----
   MHcCAQEEITest123...
   -----END EC PRIVATE KEY-----
   ```
4. Presiona Tab o click fuera del campo

### **5. Guardar Configuración**

**Click en:** `💾 Save Configuration to .env`

---

## ✅ DEBE SUCEDER:

### **Si TODO está bien:**

1. **Popup aparece:**
   ```
   ┌─────────────────────────────────┐
   │  Configuration Saved            │
   ├─────────────────────────────────┤
   │  ✅ Configuration saved          │
   │     successfully!               │
   │                                 │
   │  Location: C:\Users\..\.env     │
   │  Trading Mode: SIMULATION       │
   │                                 │
   │  The API connection has been    │
   │  reloaded.                      │
   │  Click 'Test API Connection'    │
   │  to verify.                     │
   │                                 │
   │           [ OK ]                │
   └─────────────────────────────────┘
   ```

2. **En consola debe aparecer:**
   ```
   ✅ API Key updated
   ✅ API Secret updated
   
   ✅ Configuration saved to .env file
      Location: C:\Users\393di\Desktop\Cripto-Agent\.env
      Profit Target: 2.5%
      Position Size: $5.00
      Trading Mode: SIMULATION
   
   🔄 Reloading configuration...
   
   ✅ Configuration reloaded successfully
   ```

---

## ❌ SI HAY ERROR:

### **Popup de error aparece:**
```
┌─────────────────────────────────┐
│  Error al Guardar               │
├─────────────────────────────────┤
│  ❌ No se pudo guardar la        │
│     configuración.              │
│                                 │
│  Error: [mensaje específico]   │
│                                 │
│  Verifica que:                  │
│  • Las credenciales sean        │
│    válidas                      │
│  • Tengas permisos de           │
│    escritura                    │
│  • El formato sea correcto      │
│                                 │
│           [ OK ]                │
└─────────────────────────────────┘
```

---

## 🔍 VERIFICAR QUE SE GUARDÓ:

### **Método 1: Ver archivo .env**
```powershell
Get-Content C:\Users\393di\Desktop\Cripto-Agent\.env
```

### **Método 2: Dentro del programa**
1. Click **👁️** junto a API Key
2. Debe mostrar la key completa que pegaste
3. Click **👁️** de nuevo para ocultar

---

## 🧪 PRUEBA COMPLETA:

### **Escenario 1: Credenciales Válidas**
```
1. ✏️ Editar API Key → Pegar real
2. ✏️ Editar API Secret → Pegar real
3. 💾 Save Configuration
4. ✅ Debe aparecer popup de éxito
5. 🧪 Test API Connection
6. 🟢 Debe mostrar ONLINE
```

### **Escenario 2: Credenciales Inválidas**
```
1. ✏️ Editar API Key → Pegar "test123"
2. ✏️ Editar API Secret → Pegar "test456"
3. 💾 Save Configuration
4. ✅ Debe aparecer popup de éxito (guarda igual)
5. 🧪 Test API Connection
6. 🔴 Debe mostrar OFFLINE con error
```

### **Escenario 3: Campo Vacío**
```
1. ✏️ Editar API Key → Dejar vacío
2. 💾 Save Configuration
3. ⚠️ Se guarda pero no actualiza la key
```

---

## 📊 CHECKLIST DE PRUEBA:

- [ ] Programa se ejecuta sin errores
- [ ] Configuration tab se ve correctamente
- [ ] Botón ✏️ limpia el campo API Key
- [ ] Botón ✏️ limpia el campo API Secret
- [ ] Se puede pegar texto en los campos
- [ ] Save Configuration muestra popup
- [ ] Popup tiene botón OK
- [ ] Consola muestra mensajes de confirmación
- [ ] Archivo .env se crea/actualiza
- [ ] Test Connection funciona
- [ ] Botones 👁️ muestran/ocultan credenciales

---

## ⚠️ PROBLEMAS COMUNES:

### **"No aparece popup"**
**Causa:** Error en import de messagebox

**Solución:** Verificar que tienes:
```python
from tkinter import messagebox
```

### **"Error de permisos"**
**Causa:** No puede escribir en carpeta

**Solución:** 
- Ejecutar como admin
- O cambiar ubicación del proyecto

### **"No se guarda nada"**
**Causa:** Variables no capturadas correctamente

**Debug:**
```python
print(f"API Key var: {self.api_key_var.get()}")
print(f"API Secret var: {self.api_secret_var.get()}")
```

---

## 🎯 QUÉ PROBAR ESPECÍFICAMENTE:

1. **Click ✏️ en API Key**
   - ¿Se limpia el campo? ✅/❌
   
2. **Pegar credencial**
   - ¿Se pega correctamente? ✅/❌
   
3. **Click Save**
   - ¿Aparece popup? ✅/❌
   - ¿Qué dice el popup? _________
   
4. **Verificar .env**
   - ¿Se creó el archivo? ✅/❌
   - ¿Tiene las credenciales? ✅/❌
   
5. **Test Connection**
   - ¿Funciona el botón? ✅/❌
   - ¿Qué status muestra? _________

---

## 📝 REPORTAR RESULTADOS:

Si algo no funciona, reporta:

1. **Qué paso fallé:**
   ```
   Ejemplo: "Paso 3 - No aparece popup"
   ```

2. **Qué apareció en consola:**
   ```
   Copia los mensajes de error aquí
   ```

3. **Qué esperabas:**
   ```
   "Esperaba ver popup de confirmación"
   ```

4. **Screenshot si es posible**

---

**¡Ahora prueba y reporta los resultados!** 🧪✅
