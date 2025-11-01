# Jenkins CI/CD Setup Guide

Este documento explica cómo configurar Jenkins para ejecutar tests automáticamente antes de permitir merge a `main`.

## 🎯 Objetivo

Prevenir que código con tests fallidos llegue a la rama `main` mediante validación automática en Pull Requests.

## 📋 Requisitos Previos

- Jenkins instalado (versión 2.300+)
- Plugins de Jenkins necesarios:
  - GitHub Integration Plugin
  - Pipeline Plugin
  - HTML Publisher Plugin
  - JUnit Plugin
  - Cobertura Plugin
  - GitHub Pull Request Builder Plugin

## 🔧 Configuración de Jenkins

### 1. Instalar Plugins Necesarios

En Jenkins, ve a: **Manage Jenkins → Plugin Manager → Available**

Instala:
```
- GitHub Integration
- Pipeline
- HTML Publisher
- JUnit
- Cobertura
- GitHub Pull Request Builder
```

### 2. Crear Nuevo Pipeline Job

1. **New Item** → Nombre: `BTC-Trading-Bot-PR-Validation`
2. Tipo: **Multibranch Pipeline** o **Pipeline**
3. Click **OK**

### 3. Configurar el Job

#### Opción A: Multibranch Pipeline (Recomendado)

**Branch Sources:**
```
- Add source: GitHub
- Repository URL: https://github.com/91Pixels/trader-bot
- Credentials: [Add GitHub token]
- Behaviors:
  ✅ Discover branches
  ✅ Discover pull requests from origin
  ✅ Discover pull requests from forks
```

**Build Configuration:**
```
Mode: by Jenkinsfile
Script Path: Jenkinsfile
```

**Scan Multibranch Pipeline Triggers:**
```
✅ Periodically if not otherwise run
Interval: 5 minutes
```

#### Opción B: Pipeline Simple

**Pipeline Definition:**
```
Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/91Pixels/trader-bot
Branch Specifier: */main (for main) or */PR-* (for PRs)
Script Path: Jenkinsfile
```

### 4. Configurar GitHub Webhook

En GitHub: **Settings → Webhooks → Add webhook**

```
Payload URL: http://your-jenkins-server/github-webhook/
Content type: application/json
Events: 
  ✅ Pull requests
  ✅ Pushes
```

## 🔒 Configurar Branch Protection en GitHub

### Proteger la Rama Main

1. Ve a tu repo: **Settings → Branches → Branch protection rules**
2. Click **Add rule**
3. Branch name pattern: `main`

**Configuración recomendada:**

```
✅ Require a pull request before merging
   ✅ Require approvals (1 approval mínimo)
   
✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   Status checks:
     ✅ Jenkins CI/Tests (o el nombre de tu job)
     
✅ Require conversation resolution before merging

✅ Do not allow bypassing the above settings

✅ Restrict who can push to matching branches
   (Solo administradores si es necesario)
```

**Resultado:** ¡Nadie podrá hacer merge a `main` si los tests fallan!

## 🚀 Workflow de Desarrollo

### Para Desarrolladores

1. **Crear Feature Branch:**
```bash
git checkout -b feature/nueva-funcionalidad
```

2. **Hacer cambios y commit:**
```bash
git add .
git commit -m "Add nueva funcionalidad"
git push origin feature/nueva-funcionalidad
```

3. **Crear Pull Request en GitHub**
   - Jenkins automáticamente detectará el PR
   - Ejecutará todos los 118 unit tests
   - Mostrará el resultado en el PR

4. **Ver resultados:**
   - ✅ **Pasa**: El PR puede ser mergeado
   - ❌ **Falla**: Debes arreglar los tests primero

5. **Merge a main:**
   - Solo posible si todos los tests pasan
   - Requiere aprobación (si está configurado)

## 📊 Reportes Generados

El pipeline genera:

1. **Test Report HTML** - Resumen visual de todos los tests
2. **Coverage Report** - Cobertura de código actual (mínimo 50%)
3. **JUnit XML** - Resultados en formato estándar
4. **Security Scan** - Análisis de seguridad

**Acceder a reportes:**
- En Jenkins: Build → HTML Reports → Test Report / Coverage Report

## 🛠️ Troubleshooting

### Tests fallan en Jenkins pero pasan localmente

**Problema:** Diferencia de entornos

**Solución:**
```bash
# Asegúrate de que TRADING_MODE esté en SIMULATION
# El Jenkinsfile ya lo configura, pero verifica:
export TRADING_MODE=SIMULATION  # Linux/Mac
set TRADING_MODE=SIMULATION     # Windows

# Ejecuta tests localmente como lo hace Jenkins:
python tests/run_all_tests.py
```

### Jenkins no detecta PRs

**Problema:** Webhook no configurado o plugins faltantes

**Solución:**
1. Verifica que el webhook esté activo en GitHub
2. Revisa los logs: **Manage Jenkins → System Log**
3. Confirma que GitHub Pull Request Builder plugin esté instalado

### Tests pasan pero Jenkins marca como UNSTABLE

**Problema:** Cobertura de código menor al umbral (50%)

**Solución:**
```python
# Aumenta la cobertura escribiendo más tests
# O ajusta el umbral en Jenkinsfile:
--cov-fail-under=50  # Cambiar a menor valor si es necesario
```

## 🔐 Seguridad

### GitHub Token para Jenkins

1. En GitHub: **Settings → Developer settings → Personal access tokens**
2. Generate new token:
   ```
   Scopes necesarios:
   - repo (full control)
   - admin:repo_hook
   ```
3. En Jenkins: **Credentials → Add Credentials**
   ```
   Kind: Secret text
   Secret: [tu token]
   ID: github-token
   Description: GitHub Access Token
   ```

## 📈 Métricas de Calidad

El pipeline falla si:
- ❌ Cualquier unit test falla
- ❌ Cobertura < 50%
- ⚠️ Problemas críticos de seguridad (opcional)

El pipeline tiene warnings si:
- ⚠️ Código no cumple con estándares (pylint/flake8)
- ⚠️ Vulnerabilidades encontradas

## 🎓 Ejemplo de Uso

### Escenario: Agregar nueva funcionalidad

```bash
# 1. Crear branch
git checkout -b feature/connection-retry
git push -u origin feature/connection-retry

# 2. Hacer cambios
# ... editar código ...

# 3. Ejecutar tests localmente
python tests/run_all_tests.py

# 4. Commit y push
git add .
git commit -m "Add connection retry logic"
git push

# 5. Crear PR en GitHub
# Jenkins automáticamente:
# - Ejecuta 118 tests
# - Genera reportes
# - Marca PR como ✅ o ❌

# 6. Si pasa: Merge a main
# 7. Si falla: Arreglar y push nuevamente
```

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs de Jenkins: **Console Output**
2. Verifica que todos los plugins estén actualizados
3. Confirma que las credenciales de GitHub sean correctas
4. Asegúrate de que el webhook esté funcionando

---

**¡Con esta configuración, tu código siempre estará protegido con tests automáticos antes de cada merge!** 🛡️
