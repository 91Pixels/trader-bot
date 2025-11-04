# Cripto-Bot Installer Builder
# This script creates a professional Windows installer using Inno Setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cripto-Bot Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Inno Setup is installed
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $innoPath)) {
    Write-Host "ERROR: Inno Setup not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Inno Setup from:" -ForegroundColor Yellow
    Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Download: innosetup-6.x.x.exe" -ForegroundColor Yellow
    Write-Host "Install it, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    
    # Offer to open download page
    $response = Read-Host "Open download page now? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Start-Process "https://jrsoftware.org/isdl.php"
    }
    
    exit 1
}

Write-Host "OK: Inno Setup found" -ForegroundColor Green

# Check if executable exists
if (-not (Test-Path "dist\Cripto-Bot.exe")) {
    Write-Host "ERROR: Cripto-Bot.exe not found in dist folder!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Building executable first..." -ForegroundColor Yellow
    
    # Build executable
    python -m PyInstaller build_exe.spec --clean
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to build executable" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "OK: Executable built successfully" -ForegroundColor Green
}

Write-Host "OK: Executable found" -ForegroundColor Green

# Check required files
$requiredFiles = @(
    "installer_setup.iss",
    "LICENSE.txt",
    "INSTALL_INFO.txt",
    "assets\Cripto-Bot.ico",
    ".env.example"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "ERROR: Missing required files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    exit 1
}

Write-Host "OK: All required files found" -ForegroundColor Green
Write-Host ""

# Create output directory
if (-not (Test-Path "installer_output")) {
    New-Item -ItemType Directory -Path "installer_output" | Out-Null
}

Write-Host "Building installer..." -ForegroundColor Cyan
Write-Host ""

# Compile installer
& $innoPath "installer_setup.iss"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Installer build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  INSTALLER CREATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Find the installer
$installerPath = Get-ChildItem "installer_output\Cripto-Bot-Setup-*.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($installerPath) {
    Write-Host "Installer location:" -ForegroundColor Cyan
    Write-Host "   $($installerPath.FullName)" -ForegroundColor White
    Write-Host ""
    Write-Host "Size: $([math]::Round($installerPath.Length / 1MB, 2)) MB" -ForegroundColor Cyan
    Write-Host ""
    
    # Copy to Desktop
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $desktopInstaller = Join-Path $desktopPath $installerPath.Name
    
    Copy-Item $installerPath.FullName $desktopInstaller -Force
    Write-Host "OK: Copied to Desktop: $($installerPath.Name)" -ForegroundColor Green
    Write-Host ""
    
    # Ask to run installer
    Write-Host "========================================" -ForegroundColor Cyan
    $response = Read-Host "Run installer now? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Start-Process $desktopInstaller
    }
} else {
    Write-Host "WARNING: Installer file not found in output folder" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
