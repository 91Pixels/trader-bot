# CI/CD Pipeline - Validación Automática de Tests

Este proyecto incluye **2 opciones** para ejecutar tests automáticamente antes de permitir merge a `main`:

## 🚀 Opción 1: GitHub Actions (Más Fácil - Recomendado)

✅ **Ventajas:**
- ✅ Configuración automática (ya está lista)
- ✅ Gratis para repositorios públicos
- ✅ No requiere servidor Jenkins
- ✅ Integración nativa con GitHub

### Cómo activarlo:

1. Los archivos ya están en `.github/workflows/pr-validation.yml`
2. GitHub Actions se activará **automáticamente** cuando:
   - Crees un Pull Request a `main`
   - Hagas push a `main`

3. **Configurar Branch Protection:**
   - Ve a: **Settings → Branches → Add rule**
   - Branch: `main`
   - Activa: ✅ **Require status checks to pass**
   - Selecciona: ✅ **Run Unit Tests**

**¡Listo!** GitHub bloqueará merges si los tests fallan.

---

## 🏗️ Opción 2: Jenkins (Para Infraestructura Propia)

✅ **Ventajas:**
- ✅ Control total del pipeline
- ✅ Integración con infraestructura existente
- ✅ Más opciones de personalización

### Archivos incluidos:
- `Jenkinsfile` - Pipeline principal
- `docs/JENKINS_CI_SETUP.md` - Guía completa de configuración

### Setup rápido:

1. Lee la guía completa: `docs/JENKINS_CI_SETUP.md`
2. Instala plugins necesarios en Jenkins
3. Crea un Multibranch Pipeline
4. Apunta a este repositorio
5. Configura webhook en GitHub

---

## 📊 ¿Qué valida el Pipeline?

Ambas opciones ejecutan:

### ✅ Tests (OBLIGATORIOS para merge)
- 🧪 **118 unit tests** completos
- 📊 Cobertura mínima: **50%**
- ⏱️ Tiempo de ejecución: ~7 segundos

### ⚠️ Validaciones Adicionales (solo warnings)
- 🔍 Calidad de código (pylint, flake8)
- 🔒 Escaneo de seguridad (safety, bandit)

---

## 🎯 Workflow de Desarrollo

### 1. Crear Feature Branch
```bash
git checkout -b feature/mi-funcionalidad
```

### 2. Hacer cambios
```bash
# Edita el código...
git add .
git commit -m "Add mi funcionalidad"
```

### 3. Ejecutar tests LOCALMENTE (importante!)
```bash
python tests/run_all_tests.py
```

### 4. Push a GitHub
```bash
git push -u origin feature/mi-funcionalidad
```

### 5. Crear Pull Request
- Ve a GitHub y crea el PR
- El pipeline se ejecutará **automáticamente**
- Verás el resultado en el PR:
  - ✅ **Checks passing** → Puedes hacer merge
  - ❌ **Checks failing** → Arregla los tests

### 6. Merge a main
- Solo posible si **todos los tests pasan**
- Requiere aprobación si está configurado

---

## 🔒 Branch Protection Configurada

Para máxima seguridad, configura:

```
Rama: main
✅ Require pull request before merging
✅ Require status checks to pass
   ✅ Run Unit Tests (GitHub Actions)
   O
   ✅ Jenkins CI/Tests (Jenkins)
✅ Require conversation resolution
✅ Do not allow bypassing
```

**Resultado:** Nadie puede hacer merge si los tests fallan. ¡Ni siquiera administradores!

---

## 🧪 Tests Incluidos

| Categoría | Tests | Descripción |
|-----------|-------|-------------|
| Calculations | 10 | Fórmulas de profit/fees |
| API Integration | 12 | Coinbase API |
| Trading Logic | 20+ | Auto buy/sell |
| Formula Verification | 10 | Cálculos exactos |
| Balance & Wallet | 15+ | Balances reales |
| Zero Division | 9 | Edge cases |
| Integration | 3 | Tests end-to-end |
| JWT Auth | 5 | Autenticación |
| Complete API | 15+ | API completa |
| **TOTAL** | **118** | **Todos deben pasar** |

---

## 📈 Ver Resultados

### GitHub Actions:
1. Ve a tu PR
2. Scroll down a "Checks"
3. Click en "Details" para ver logs
4. Descarga artifacts con reportes HTML

### Jenkins:
1. Abre Jenkins
2. Ve al build del PR
3. Click en "HTML Reports"
4. Ve Coverage Report y Test Report

---

## ⚡ Tips para Developers

### Antes de hacer Push:
```bash
# Siempre ejecuta tests localmente primero
python tests/run_all_tests.py

# Verifica que TRADING_MODE esté en SIMULATION
echo $TRADING_MODE  # Linux/Mac
echo %TRADING_MODE% # Windows
```

### Si los tests fallan en CI pero pasan local:
```bash
# Asegúrate que el modo sea correcto
set TRADING_MODE=SIMULATION  # Windows
export TRADING_MODE=SIMULATION  # Linux/Mac

# Ejecuta de nuevo
python tests/run_all_tests.py
```

### Para ver cobertura localmente:
```bash
pytest tests/ --cov=. --cov-report=html
# Abre: htmlcov/index.html
```

---

## 🎓 Ejemplo Completo

```bash
# 1. Crear branch
git checkout -b feature/connection-indicator

# 2. Hacer cambios
# ... editar código ...

# 3. Ejecutar tests LOCALMENTE
python tests/run_all_tests.py
# ✅ 118 passed in 7.10s

# 4. Commit y push
git add .
git commit -m "Add connection status indicators"
git push -u origin feature/connection-indicator

# 5. Crear PR en GitHub
# - GitHub Actions se ejecuta automáticamente
# - Espera 1-2 minutos
# - Ve el resultado en el PR

# 6. Si ✅ pasa: Merge!
# 7. Si ❌ falla: Arregla y push de nuevo
```

---

## 🆘 Troubleshooting

### "Tests failed in CI but pass locally"
**Causa:** Diferencias de ambiente  
**Solución:** Verifica `TRADING_MODE=SIMULATION` en CI

### "Coverage below 50%"
**Causa:** No hay suficiente cobertura de tests  
**Solución:** Escribe más tests o ajusta el umbral

### "GitHub Actions not running"
**Causa:** Workflow file tiene errores  
**Solución:** Revisa `.github/workflows/pr-validation.yml`

### "Cannot merge to main"
**Causa:** Tests fallaron  
**Solución:** Arregla los tests y haz push de nuevo

---

## 📞 Soporte

Si necesitas ayuda:
1. Revisa los logs del CI (GitHub Actions o Jenkins)
2. Ejecuta tests localmente con más verbosidad
3. Verifica la documentación completa en `docs/`

---

## ✅ Checklist de Configuración

### Para GitHub Actions:
- [x] Archivo `.github/workflows/pr-validation.yml` creado
- [ ] Branch protection configurada en GitHub
- [ ] Tests ejecutándose en PRs

### Para Jenkins:
- [ ] Jenkins instalado
- [ ] Plugins necesarios instalados
- [ ] Job creado apuntando al repo
- [ ] Webhook configurado
- [ ] Branch protection configurada

---

**¡Con este CI/CD, tu código siempre estará protegido!** 🛡️
