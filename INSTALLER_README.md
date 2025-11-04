# 📦 Cripto-Bot Professional Installer

## 🎯 Objetivo

Crear un instalador profesional tipo setup.exe que instala Cripto-Bot en **Program Files** como un programa tradicional de Windows.

---

## ✅ Ventajas del Instalador

### **vs Ejecutable Suelto:**
```
❌ Ejecutable suelto:
   - Archivos dispersos
   - Sin estructura organizada
   - Usuario no sabe dónde está todo
   - Difícil de desinstalar

✅ Con Instalador:
   - Instalación en Program Files
   - Estructura organizada
   - Accesos directos automáticos
   - Desinstalador incluido
   - Profesional y confiable
```

---

## 📋 Qué Incluye el Instalador

### **Archivos que se Instalan:**
```
C:\Program Files\Cripto-Bot\
├─ Cripto-Bot.exe          ← Aplicación principal
├─ assets\
│  ├─ Cripto-Bot.png       ← Logo
│  └─ Cripto-Bot.ico       ← Ícono
├─ docs\
│  ├─ README.md
│  ├─ MANUAL_TEST_CASES_ES.md
│  ├─ EXECUTABLE_README.md
│  └─ EXECUTABLE_FIX.md
├─ .env.example            ← Template para API keys
├─ coinbase_ecdsa_key.txt  ← Key file example
└─ trading_bot.db          ← Se crea automáticamente
```

### **Accesos Directos Creados:**
```
✅ Menú Inicio: Cripto-Bot
✅ Escritorio: Cripto-Bot (opcional)
✅ Desinstalador: En Menú Inicio
```

---

## 🔧 Requisitos

### **Para Crear el Instalador:**

1. **Inno Setup 6** (gratuito)
   - Descargar: https://jrsoftware.org/isdl.php
   - Archivo: innosetup-6.x.x.exe
   - Instalar en ubicación predeterminada

2. **Archivos del Proyecto:**
   ```
   ✅ dist\Cripto-Bot.exe (ya creado)
   ✅ assets\Cripto-Bot.ico
   ✅ LICENSE.txt
   ✅ INSTALL_INFO.txt
   ✅ installer_setup.iss
   ```

---

## 🚀 Cómo Crear el Instalador

### **Opción 1: Usar Script PowerShell (Recomendado)**

```powershell
# En la carpeta del proyecto
cd C:\Users\393di\Desktop\Cripto-Agent

# Ejecutar script
powershell -ExecutionPolicy Bypass -File build_installer.ps1
```

El script:
1. ✅ Verifica que Inno Setup esté instalado
2. ✅ Verifica que el ejecutable exista
3. ✅ Compila el instalador
4. ✅ Lo copia al Desktop
5. ✅ Pregunta si quieres ejecutarlo

---

### **Opción 2: Manual con Inno Setup**

1. Instalar Inno Setup desde https://jrsoftware.org/isdl.php

2. Abrir `installer_setup.iss` con Inno Setup Compiler

3. Click en "Compile" (⚙️)

4. El instalador se crea en: `installer_output\Cripto-Bot-Setup-v1.0.exe`

---

## 📦 Resultado

### **Installer Output:**
```
installer_output\
└─ Cripto-Bot-Setup-v1.0.exe  (~35-40 MB)
```

### **Se Copia a:**
```
C:\Users\393di\Desktop\
└─ Cripto-Bot-Setup-v1.0.exe
```

---

## 🎯 Proceso de Instalación (Usuario Final)

### **Paso 1: Ejecutar Setup**
```
Doble-click en: Cripto-Bot-Setup-v1.0.exe
```

### **Paso 2: Wizard de Instalación**
```
1. Bienvenida
2. Licencia de uso
3. Información importante
4. Seleccionar carpeta (default: C:\Program Files\Cripto-Bot)
5. Crear accesos directos (Desktop opcional)
6. Instalación
7. Configurar API keys
```

### **Paso 3: Primer Uso**
```
1. El instalador abre .env.example automáticamente
2. Usuario agrega sus API keys
3. Guarda como ".env" (quita .example)
4. Cierra y abre Cripto-Bot desde Desktop o Menú Inicio
```

---

## 🔐 Configuración Post-Instalación

### **Ubicación del Programa:**
```
C:\Program Files\Cripto-Bot\
```

### **Archivo .env que Usuario Debe Crear:**
```
C:\Program Files\Cripto-Bot\.env
```

### **Contenido .env:**
```env
COINBASE_API_KEY=organizations/xxx/apiKeys/xxx
COINBASE_API_SECRET=-----BEGIN EC PRIVATE KEY-----
MHcCAQEEI...
-----END EC PRIVATE KEY-----
TRADING_MODE=LIVE
SIMULATION_MODE=False
```

---

## 📊 Características del Instalador

### **Ventana de Bienvenida:**
```
- Logo de Cripto-Bot
- Versión 1.0 Beta
- Información del creador
```

### **Licencia:**
```
- Términos de uso
- Disclaimer de trading
- Copyright info
```

### **Info Importante:**
```
- Requisitos del sistema
- Qué necesitas antes de instalar
- Pasos post-instalación
- Advertencias de seguridad
```

### **Opciones de Instalación:**
```
✅ Carpeta de destino (customizable)
✅ Acceso directo en Desktop (opcional)
✅ Acceso directo en Quick Launch (opcional)
✅ Componentes a instalar (todos por default)
```

### **Post-Instalación:**
```
✅ Abre .env.example en Notepad
✅ Muestra mensaje de configuración
✅ Ofrece ejecutar Cripto-Bot
```

---

## 🗑️ Desinstalación

### **Proceso:**
```
1. Panel de Control → Programas y características
2. Buscar "Cripto-Bot"
3. Click en "Desinstalar"
```

### **O desde Menú Inicio:**
```
Inicio → Cripto-Bot → Uninstall Cripto-Bot
```

### **Qué se Elimina:**
```
✅ C:\Program Files\Cripto-Bot\ (carpeta completa)
✅ Accesos directos
✅ Entradas del registro
✅ trading_bot.db (opcional)
✅ .env (opcional)
```

---

## 📝 Archivos del Proyecto

### **Para Crear Instalador:**
```
installer_setup.iss         ← Script Inno Setup
LICENSE.txt                 ← Licencia
INSTALL_INFO.txt            ← Info pre-instalación
build_installer.ps1         ← Script PowerShell
```

### **Generados:**
```
installer_output\
└─ Cripto-Bot-Setup-v1.0.exe  ← INSTALADOR FINAL
```

---

## 🎨 Personalización

### **En installer_setup.iss puedes cambiar:**

**Información de la App:**
```
#define MyAppName "Cripto-Bot"
#define MyAppVersion "1.0"
#define MyAppPublisher "Michael Camacho"
```

**Carpeta de Instalación:**
```
DefaultDirName={autopf}\{#MyAppName}
// {autopf} = C:\Program Files
```

**Ícono del Setup:**
```
SetupIconFile=assets\Cripto-Bot.ico
```

**Compresión:**
```
Compression=lzma
SolidCompression=yes
```

---

## ✅ Ventajas de Este Método

### **Para el Usuario:**
```
✅ Instalación profesional y confiable
✅ Todo organizado en Program Files
✅ Accesos directos automáticos
✅ Fácil de desinstalar
✅ Wizard guiado paso a paso
✅ Detecta si ya está instalado
```

### **Para ti (Desarrollador):**
```
✅ Distribución profesional
✅ Fácil de actualizar (nuevo instalador)
✅ Control de versiones
✅ Instalación silenciosa posible
✅ Logs de instalación
✅ Firma digital (opcional)
```

---

## 🔄 Actualización de Versión

### **Para Nueva Versión:**

1. Actualiza código fuente
2. Rebuild ejecutable: `pyinstaller build_exe.spec --clean`
3. Cambia versión en `installer_setup.iss`:
   ```
   #define MyAppVersion "1.1"
   ```
4. Recompila instalador
5. Distribuye nuevo `Cripto-Bot-Setup-v1.1.exe`

---

## 📊 Comparación

| Aspecto | Ejecutable Suelto | Con Instalador |
|---------|-------------------|----------------|
| **Profesionalismo** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Organización** | ❌ | ✅ |
| **Desinstalación** | Manual | Automática |
| **Accesos Directos** | Manual | Automático |
| **Actualizaciones** | Confuso | Claro |
| **Confianza Usuario** | Baja | Alta |

---

## 🚀 Próximos Pasos

1. **Instalar Inno Setup:**
   - https://jrsoftware.org/isdl.php
   - Descargar innosetup-6.x.x.exe
   - Instalar con opciones por defecto

2. **Ejecutar Script:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File build_installer.ps1
   ```

3. **El Script Hará:**
   - ✅ Verificar Inno Setup
   - ✅ Verificar ejecutable
   - ✅ Compilar instalador
   - ✅ Copiar a Desktop
   - ✅ Preguntar si ejecutar

4. **Resultado:**
   ```
   C:\Users\393di\Desktop\
   └─ Cripto-Bot-Setup-v1.0.exe ← LISTO PARA DISTRIBUIR
   ```

---

## 📞 Soporte

**Si tienes problemas:**
1. Verifica que Inno Setup esté instalado
2. Verifica que dist\Cripto-Bot.exe exista
3. Ejecuta: `powershell -ExecutionPolicy Bypass -File build_installer.ps1`
4. Lee mensajes de error en pantalla

---

**¡Ahora tu bot tiene una instalación profesional tipo software comercial!** 🎉

**Creador:** Michael Camacho  
**License:** 91pixelsusa@gmail.com  
**Version:** 1.0 Beta
