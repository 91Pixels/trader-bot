# 🔧 Executable Fix - API & Database Connection

## ❌ Problema Identificado

El ejecutable anterior tenía problemas con:
1. **No encontraba el archivo `.env`** → API no conectaba
2. **Database se creaba en carpeta temporal** → Datos no persistían

---

## ✅ Solución Aplicada

### **1. Config.py - Búsqueda Multi-ubicación de .env**

Ahora el ejecutable busca `.env` en múltiples ubicaciones:

```python
if getattr(sys, 'frozen', False):
    # Running as executable
    env_locations = [
        os.path.join(application_path, '.env'),  # Same folder as exe
        os.path.join(os.path.dirname(application_path), '.env'),  # Parent
        os.path.join(os.path.expanduser('~'), 'Desktop', '.env'),  # Desktop
        os.path.join(sys._MEIPASS, '.env'),  # Temp (if bundled)
    ]
```

**Orden de búsqueda:**
1. Misma carpeta que `Cripto-Bot.exe`
2. Carpeta padre
3. Desktop (`C:\Users\393di\Desktop\.env`)
4. Carpeta temporal de PyInstaller

---

### **2. Database.py - Guardar en Carpeta del Ejecutable**

La base de datos ahora se guarda junto al ejecutable:

```python
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    self.db_path = os.path.join(application_path, db_path)
    print(f"📁 Running as executable, DB path: {self.db_path}")
```

**Resultado:**
```
C:\Users\393di\Desktop\
├─ Cripto-Bot.exe
├─ .env                  ← API Keys
└─ trading_bot.db        ← Database persistente
```

---

### **3. btc_trader.py - Assets Path Fix**

Los assets (logo) ahora se cargan desde la ubicación correcta:

```python
if getattr(sys, 'frozen', False):
    # Running as executable
    application_path = os.path.dirname(sys.executable)
    assets_dir = os.path.join(application_path, "assets")
    # If not found, try _MEIPASS (temp folder)
    if not os.path.exists(assets_dir):
        assets_dir = os.path.join(sys._MEIPASS, "assets")
```

---

## 📋 Configuración Correcta

### **Estructura de Archivos en Desktop:**

```
C:\Users\393di\Desktop\
│
├─ Cripto-Bot.exe          ← Ejecutable
├─ .env                    ← TUS API KEYS (CRÍTICO)
└─ trading_bot.db          ← Se crea automáticamente
```

---

## 🔑 Archivo .env Requerido

**Ubicación:** `C:\Users\393di\Desktop\.env`

**Contenido mínimo:**
```env
COINBASE_API_KEY=tu_api_key_aqui
COINBASE_API_SECRET=tu_api_secret_aqui
TRADING_MODE=LIVE
SIMULATION_MODE=False
```

**O si usas archivo de clave:**
```env
COINBASE_API_KEY=tu_api_key_aqui
COINBASE_PRIVATE_KEY_FILE=coinbase_ecdsa_key.txt
TRADING_MODE=LIVE
SIMULATION_MODE=False
```

---

## 🧪 Verificación

### **Al ejecutar Cripto-Bot.exe, deberías ver:**

```
✅ Found .env at: C:\Users\393di\Desktop\.env
📁 Running as executable, DB path: C:\Users\393di\Desktop\trading_bot.db
✅ Database connected: C:\Users\393di\Desktop\trading_bot.db
✅ Logo loaded: 200x145px
✅ Window icon set
🟢 Connection Status: ONLINE
```

### **Connection Status debe mostrar:**
```
Coinbase API: ✅ Connected
Balance: Using Real Balance
Mode: LIVE
🟢 ONLINE - All endpoints working

Endpoints Status:
✅ BTC Price: ONLINE
✅ Wallet Balance: ONLINE
✅ Orders (Buy/Sell): ONLINE
✅ Products: ONLINE
```

---

## 🐛 Solución de Problemas

### **Problema: "Not Connected" / "OFFLINE"**

**Causa:** Archivo `.env` no encontrado o mal formateado

**Solución:**
1. Verifica que `.env` existe en Desktop:
   ```powershell
   Test-Path C:\Users\393di\Desktop\.env
   ```

2. Verifica contenido:
   ```powershell
   Get-Content C:\Users\393di\Desktop\.env
   ```

3. Asegúrate que tiene este formato (sin espacios extras):
   ```env
   COINBASE_API_KEY=organizations/xxx/apiKeys/xxx
   COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----
   MHcCAQ...
   -----END EC PRIVATE KEY-----
   TRADING_MODE=LIVE
   ```

---

### **Problema: "Database not working"**

**Causa:** Permisos o ubicación incorrecta

**Solución:**
1. Elimina database anterior:
   ```powershell
   Remove-Item C:\Users\393di\Desktop\trading_bot.db
   ```

2. Re-ejecuta Cripto-Bot.exe (se creará automáticamente)

---

### **Problema: Logo no aparece**

**Causa:** Assets no bundled correctamente

**Solución:**
- El logo está empaquetado en el .exe
- Si no aparece, copia la carpeta `assets` al Desktop:
  ```
  C:\Users\393di\Desktop\
  ├─ Cripto-Bot.exe
  ├─ assets\
  │  └─ Cripto-Bot.png
  └─ .env
  ```

---

## 🔄 Rebuild Instructions

Si necesitas reconstruir el ejecutable:

```bash
# 1. Navegar al proyecto
cd C:\Users\393di\Desktop\Cripto-Agent

# 2. Reconstruir
pyinstaller build_exe.spec --clean

# 3. Eliminar ejecutable anterior
Remove-Item C:\Users\393di\Desktop\Cripto-Bot.exe -Force

# 4. Mover nuevo ejecutable
move dist\Cripto-Bot.exe C:\Users\393di\Desktop\Cripto-Bot.exe

# 5. Verificar .env está en Desktop
Test-Path C:\Users\393di\Desktop\.env
```

---

## ✅ Cambios en el Código

### **Archivos Modificados:**

1. **config.py**
   - ✅ Multi-location .env search
   - ✅ Soporte PyInstaller frozen mode
   - ✅ Debug output para ubicación encontrada

2. **database.py**
   - ✅ DB path relativo al ejecutable
   - ✅ No más database en temp folder
   - ✅ Persistencia garantizada

3. **btc_trader.py**
   - ✅ Assets path detection
   - ✅ Soporte _MEIPASS
   - ✅ Fallback locations

4. **build_exe.spec**
   - ✅ Assets bundled
   - ❌ .env NO bundled (por seguridad)
   - ✅ .env.example incluido

---

## 📦 Nuevo Build Info

```
Nombre: Cripto-Bot.exe
Tamaño: ~34.5 MB
Build: Nov 3, 2025 2:00 PM
Versión: 1.0 Beta (Fixed)
Python: 3.10
PyInstaller: 6.16.0

Cambios:
✅ .env multi-location search
✅ Database persistent location
✅ Assets path fix
✅ Better error messages
```

---

## 🎯 Testing Checklist

Antes de usar el ejecutable, verifica:

- [ ] `.env` existe en Desktop
- [ ] `.env` tiene API keys válidas
- [ ] `Cripto-Bot.exe` está en Desktop
- [ ] Doble-click en Cripto-Bot.exe
- [ ] Ver console output: "✅ Found .env at..."
- [ ] Ver Connection Status: "🟢 ONLINE"
- [ ] Ver endpoints: "✅ ONLINE"
- [ ] Database se crea: `trading_bot.db`
- [ ] Logo aparece correctamente
- [ ] Version info aparece

---

## 🚀 Ready to Use!

El ejecutable actualizado ahora:
- ✅ Encuentra tu `.env` automáticamente
- ✅ Guarda database de forma persistente
- ✅ Carga assets correctamente
- ✅ Se conecta a Coinbase API
- ✅ Muestra balance real
- ✅ Funciona como standalone app

**¡Ejecuta y a operar!** 📈✨

---

**Fix aplicado:** Noviembre 3, 2025  
**Status:** ✅ RESUELTO
