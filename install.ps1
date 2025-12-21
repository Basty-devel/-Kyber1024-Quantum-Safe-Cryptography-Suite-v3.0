# install.ps1 - One-liner for Windows PowerShell
Write-Host "Kyber1024 Quantum-Safe Cryptography Suite" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if we're in PowerShell
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Host "PowerShell 5+ required. Please update PowerShell." -ForegroundColor Red
    exit 1
}

# Download and run installer
$tempFile = "$env:TEMP\kyber1024-installer.ps1"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Basty-devel/-Kyber1024-Quantum-Safe-Cryptography-Suite-v3.0/main/complete-windows-installer.bat" -OutFile $tempFile

Write-Host "Running installer..." -ForegroundColor Yellow
& $tempFile

# Cleanup
Remove-Item $tempFile -ErrorAction SilentlyContinue