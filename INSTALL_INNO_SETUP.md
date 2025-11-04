# 📥 INSTALACIÓN DE INNO SETUP - GUÍA PASO A PASO

## 🎯 PASO 1: DESCARGAR INNO SETUP

### **Link de Descarga:**
```
https://jrsoftware.org/isdl.php
```

### **Archivo a Descargar:**
```
innosetup-6.3.3.exe (o versión más reciente)
Tamaño: ~2-3 MB
```

**Instrucciones:**
1. Abre tu navegador
2. Copia y pega el link: https://jrsoftware.org/isdl.php
3. Busca "Inno Setup 6.x.x" en la página
4. Click en "Download Inno Setup 6.x.x"
5. Guarda el archivo

---

## 🔧 PASO 2: INSTALAR INNO SETUP

### **Ejecutar el Instalador:**
1. Doble-click en `innosetup-6.x.x.exe` descargado
2. Click "Yes" si Windows pregunta (UAC)
3. Selecciona idioma: **English** (recomendado)
4. Click "OK"

### **Wizard de Instalación:**
```
1. Welcome Screen → Click "Next"
2. License Agreement → Click "I accept" → "Next"
3. Select Destination → Dejar default:
   C:\Program Files (x86)\Inno Setup 6
   → Click "Next"
4. Select Components → Dejar todo seleccionado → "Next"
5. Select Start Menu Folder → Dejar default → "Next"
6. Select Additional Tasks → Dejar default → "Next"
7. Ready to Install → Click "Install"
8. Completing Setup → Click "Finish"
```

**LISTO! Inno Setup instalado** ✅

---

## 🚀 PASO 3: CREAR EL INSTALADOR

### **Volver a tu proyecto:**

Abre PowerShell en:
```
C:\Users\393di\Desktop\Cripto-Agent
```

### **Ejecutar el script:**
```powershell
powershell -ExecutionPolicy Bypass -File build_installer.ps1
```

### **El script hará:**
```
✅ Verificar que Inno Setup esté instalado
✅ Verificar que Cripto-Bot.exe exista
✅ Compilar el instalador
✅ Copiar a Desktop
✅ Preguntar si quieres ejecutarlo
```

---

## 📦 RESULTADO ESPERADO:

```
========================================
  Cripto-Bot Installer Builder
========================================

✅ Inno Setup found
✅ Executable found
✅ All required files found

🔨 Building installer...

[Compilando...]

========================================
  ✅ INSTALLER CREATED SUCCESSFULLY!
========================================

📦 Installer location:
   C:\Users\393di\Desktop\Cripto-Agent\installer_output\Cripto-Bot-Setup-v1.0.exe

📏 Size: 38.5 MB

✅ Copied to Desktop: Cripto-Bot-Setup-v1.0.exe

========================================
Run installer now? (Y/N):
```

---

## ✅ SI TODO VA BIEN:

Verás en tu Desktop:
```
C:\Users\393di\Desktop\
└─ Cripto-Bot-Setup-v1.0.exe  (~40 MB)
```

**¡ESE ES TU INSTALADOR PROFESIONAL!** 🎉

---

## 🔍 VERIFICACIÓN RÁPIDA:

### **Después de instalar Inno Setup, verifica:**

```powershell
Test-Path "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

**Debe devolver:** `True`

Si devuelve `True` → Todo OK, ejecuta el script!

---

## 🐛 SI HAY PROBLEMAS:

### **"Inno Setup not found":**
- Reinstala Inno Setup
- Asegúrate que se instaló en: `C:\Program Files (x86)\Inno Setup 6`
- Verifica con el comando de arriba

### **"Cripto-Bot.exe not found":**
- El script lo construirá automáticamente
- O ejecuta manualmente: `pyinstaller build_exe.spec --clean`

### **Otros errores:**
- Lee el mensaje de error en pantalla
- Verifica que todos los archivos estén presentes
- Ejecuta de nuevo el script

---

## 📞 RESUMEN EJECUTIVO:

```
1️⃣ Descargar Inno Setup: https://jrsoftware.org/isdl.php
2️⃣ Instalar con opciones por defecto
3️⃣ Ejecutar: powershell -ExecutionPolicy Bypass -File build_installer.ps1
4️⃣ Resultado: Cripto-Bot-Setup-v1.0.exe en Desktop
```

**¡En 5-10 minutos tendrás tu instalador listo!** ⚡

---

**Siguiente:** Ejecuta el instalador y tu bot se instalará en Program Files como un programa profesional.
