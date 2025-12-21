# Install-Kyber.ps1 - Correct PowerShell Installer
Write-Host "Starting Kyber1024 Quantum-Safe Suite Installation..." -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/4] Checking for Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = (python --version 2>&1) -replace 'Python ', ''
    Write-Host "  Found Python $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Python not found in PATH." -ForegroundColor Red
    Write-Host "  Please install Python 3.8+ from https://python.org and try again." -ForegroundColor Yellow
    exit 1
}

# 2. Clone repository
Write-Host "`n[2/4] Downloading suite files..." -ForegroundColor Yellow
$targetDir = "$env:USERPROFILE\Kyber1024-Suite"
if (Test-Path $targetDir) {
    Remove-Item $targetDir -Recurse -Force
}
git clone https://github.com/Basty-devel/-Kyber1024-Quantum-Safe-Cryptography-Suite-v3.0.git $targetDir
Set-Location $targetDir

# 3. Install dependencies
Write-Host "`n[3/4] Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create launcher
Write-Host "`n[4/4] Creating launcher..." -ForegroundColor Yellow
$launcherPath = "$env:USERPROFILE\Desktop\Kyber1024-Suite.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($launcherPath)
$shortcut.TargetPath = "python"
$shortcut.Arguments = """$targetDir\kyber1024.py"""
$shortcut.WorkingDirectory = $targetDir
$shortcut.Save()

Write-Host "`n✅ Installation Complete!" -ForegroundColor Green
Write-Host "  • Files installed to: $targetDir" -ForegroundColor Cyan
Write-Host "  • Launcher created on Desktop" -ForegroundColor Cyan
Write-Host "`nLaunch the suite from the desktop shortcut or run:" -ForegroundColor Yellow
Write-Host "  python `"$targetDir\kyber1024.py`""