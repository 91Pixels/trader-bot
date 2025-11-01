# Setup Jenkins Local
Write-Host "Configurando Jenkins localmente..." -ForegroundColor Green

# 1. Verificar Java
Write-Host "Verificando Java..." -ForegroundColor Cyan
$javaPath = "C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot\bin"
if (Test-Path $javaPath) {
    $env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot"
    $env:Path = $javaPath + ";" + $env:Path
    & "$javaPath\java.exe" -version
    Write-Host "Java instalado correctamente" -ForegroundColor Green
} else {
    Write-Host "Java no encontrado" -ForegroundColor Red
    exit 1
}

# 2. Crear directorio para Jenkins
Write-Host "Creando directorio Jenkins..." -ForegroundColor Cyan
$jenkinsDir = "$PSScriptRoot\jenkins"
if (!(Test-Path $jenkinsDir)) {
    New-Item -ItemType Directory -Path $jenkinsDir | Out-Null
}
Set-Location $jenkinsDir

# 3. Descargar Jenkins WAR
Write-Host "Descargando Jenkins WAR..." -ForegroundColor Cyan
$jenkinsWar = "$jenkinsDir\jenkins.war"
if (!(Test-Path $jenkinsWar)) {
    $url = "https://get.jenkins.io/war-stable/2.426.2/jenkins.war"
    Write-Host "Descargando desde: $url" -ForegroundColor Yellow
    Write-Host "Tamano aproximado: 92 MB - Por favor espera..." -ForegroundColor Yellow
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $jenkinsWar -UseBasicParsing
        Write-Host "Jenkins descargado exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "Error descargando Jenkins: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Jenkins WAR ya existe" -ForegroundColor Green
}

# 4. Iniciar Jenkins
Write-Host "Iniciando Jenkins..." -ForegroundColor Cyan
Write-Host "Puerto: 8080" -ForegroundColor Yellow
Write-Host "URL: http://localhost:8080" -ForegroundColor Yellow
Write-Host "Jenkins esta arrancando (puede tomar 30-60 segundos)..." -ForegroundColor Yellow

# Ejecutar Jenkins
$jenkinsProcess = Start-Process -FilePath "$javaPath\java.exe" -ArgumentList "-jar", $jenkinsWar, "--httpPort=8080" -WorkingDirectory $jenkinsDir -PassThru

Write-Host "Jenkins iniciado (PID: $($jenkinsProcess.Id))" -ForegroundColor Green

# 5. Esperar a que Jenkins este listo
Write-Host "Esperando a que Jenkins este listo..." -ForegroundColor Yellow
$timeout = 120
$elapsed = 0
$ready = $false

while ($elapsed -lt $timeout -and !$ready) {
    Start-Sleep -Seconds 3
    $elapsed += 3
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 403) {
            $ready = $true
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if ($ready) {
    Write-Host ""
    Write-Host "Jenkins esta LISTO!" -ForegroundColor Green
    Write-Host "CONTRASENA INICIAL:" -ForegroundColor Cyan
    
    # Leer contrasena inicial
    Start-Sleep -Seconds 5
    $secretFile = "$jenkinsDir\.jenkins\secrets\initialAdminPassword"
    if (Test-Path $secretFile) {
        $password = Get-Content $secretFile
        Write-Host $password -ForegroundColor Yellow
        Write-Host "Copia esta contrasena - la necesitaras en el navegador" -ForegroundColor Red
    } else {
        Write-Host "Archivo: $secretFile" -ForegroundColor Yellow
    }
    
    Write-Host "Abriendo navegador en http://localhost:8080..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8080"
    
    Write-Host "PROXIMOS PASOS:" -ForegroundColor Cyan
    Write-Host "1. Pega la contrasena inicial en el navegador" -ForegroundColor White
    Write-Host "2. Selecciona 'Install suggested plugins'" -ForegroundColor White
    Write-Host "3. Crea un usuario admin" -ForegroundColor White
    Write-Host "4. Click 'Save and Continue'" -ForegroundColor White
    Write-Host "Para detener Jenkins: Cierra esta ventana o presiona Ctrl+C" -ForegroundColor Yellow
    
    # Mantener el proceso corriendo
    Write-Host "Jenkins corriendo... Presiona Ctrl+C para detener" -ForegroundColor Green
    Wait-Process -Id $jenkinsProcess.Id
    
} else {
    Write-Host "Jenkins no respondio a tiempo" -ForegroundColor Red
    Write-Host "Verifica que el puerto 8080 no este en uso" -ForegroundColor Yellow
    Stop-Process -Id $jenkinsProcess.Id -Force
    exit 1
}
