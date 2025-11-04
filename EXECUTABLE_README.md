# 🚀 Cripto-Bot Executable

## ✅ Executable Creado Exitosamente!

**Ubicación:** `C:\Users\393di\Desktop\Cripto-Bot.exe`

---

## 📋 Instrucciones de Uso

### **1. Ejecutar la Aplicación:**

Simplemente haz doble clic en `Cripto-Bot.exe` en tu escritorio.

```
📁 Desktop
   └─ Cripto-Bot.exe  ← Doble click aquí
```

---

### **2. Primera Ejecución:**

El ejecutable incluye:
- ✅ Todos los archivos necesarios
- ✅ Logo y assets
- ✅ Database sqlite
- ✅ Configuración .env

**IMPORTANTE:** El archivo `.env` con tus API keys debe estar en la misma carpeta que el ejecutable o en:
- `C:\Users\393di\Desktop\Cripto-Agent\.env`

---

### **3. Características del Ejecutable:**

| Característica | Estado |
|----------------|--------|
| **Tamaño** | ~50-80 MB (todo incluido) |
| **Requisitos** | Ninguno (standalone) |
| **Ícono** | Logo Cripto-Bot ✅ |
| **Consola** | Oculta (GUI only) |
| **Python** | No necesario (empaquetado) |
| **Dependencias** | Todas incluidas |

---

## 🔧 Configuración

### **API Keys:**

El ejecutable buscará el archivo `.env` en estas ubicaciones (en orden):
1. Carpeta donde se encuentra el `.exe`
2. Carpeta del proyecto original: `C:\Users\393di\Desktop\Cripto-Agent\`

**Contenido necesario en .env:**
```env
COINBASE_API_KEY=tu_api_key
COINBASE_API_SECRET=tu_api_secret
SIMULATION_MODE=True
```

---

## 📊 Archivos Generados

El ejecutable creará estos archivos automáticamente:

```
C:\Users\393di\Desktop\
├─ Cripto-Bot.exe          ← Ejecutable principal
├─ trading_bot.db          ← Database (se crea automáticamente)
└─ .env                    ← Tus API keys (debes tener este)
```

---

## 🎯 Distribución

### **Para compartir el bot:**

1. Copia `Cripto-Bot.exe` a cualquier PC Windows
2. Incluye el archivo `.env.example` (sin tus keys)
3. El usuario debe crear su propio `.env` con sus API keys

### **Requisitos del sistema:**
- ✅ Windows 10/11 (64-bit)
- ✅ 4GB RAM mínimo
- ✅ 100MB espacio en disco
- ✅ Conexión a internet

---

## 🔄 Actualizar el Ejecutable

Si haces cambios al código fuente:

```bash
# En la carpeta del proyecto
cd C:\Users\393di\Desktop\Cripto-Agent

# Reconstruir ejecutable
pyinstaller build_exe.spec --clean

# Mover a Desktop
move dist\Cripto-Bot.exe C:\Users\393di\Desktop\Cripto-Bot.exe
```

---

## 🐛 Solución de Problemas

### **El ejecutable no abre:**
- Verifica que Windows Defender no lo esté bloqueando
- Click derecho → Propiedades → Desbloquear

### **Error de API Keys:**
- Verifica que `.env` esté en la misma carpeta
- Verifica formato de las API keys

### **Database error:**
- Elimina `trading_bot.db` y se recreará

### **Logo no aparece:**
- El logo está empaquetado internamente
- Si falta, reconstruye con `pyinstaller`

---

## 📦 Archivos del Build

### **Archivos temporales (puedes eliminar):**
```
build/              ← Archivos temporales de build
dist/               ← Carpeta de distribución (después de mover .exe)
build_exe.spec      ← Configuración de PyInstaller
create_icon.py      ← Script de conversión de ícono
__pycache__/        ← Cache de Python
*.pyc               ← Bytecode compilado
```

### **Archivos importantes (mantener):**
```
btc_trader.py           ← Código fuente
assets/                 ← Logos e imágenes
.env                    ← API keys
database.py             ← Database handler
coinbase_complete_api.py ← API wrapper
```

---

## 🎨 Información del Software

```
Nombre: Cripto-Bot
Versión: 1.0 Beta
Creator: Michael Camacho
License: 91pixelsusa@gmail.com
Platform: Windows 64-bit
Framework: Python + Tkinter
```

---

## ✅ Verificación Post-Build

Archivos verificados:
- [x] `Cripto-Bot.exe` en Desktop
- [x] Ícono integrado (Cripto-Bot.ico)
- [x] Logo interno (assets/Cripto-Bot.png)
- [x] Database handler incluido
- [x] API wrapper incluido
- [x] WebSocket feed incluido
- [x] Config module incluido
- [x] Sin ventana de consola
- [x] Tamaño optimizado con UPX

---

## 🚀 Listo para Usar!

El ejecutable `Cripto-Bot.exe` está en tu escritorio y listo para usar.

**Doble click y a operar!** 📈✨

---

**Build completado:** Noviembre 3, 2025  
**PyInstaller Version:** 6.16.0  
**Python Version:** 3.10
