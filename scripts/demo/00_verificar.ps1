# Revisa que todas las herramientas de la demostración estén instaladas.
. "$PSScriptRoot\comun.ps1"
Titulo 'Verificación de herramientas'

function Funciona([scriptblock]$Comando) {
    try { & $Comando 2>$null | Out-Null; return $LASTEXITCODE -eq 0 } catch { return $false }
}

$revisiones = @(
    @{ Nombre = 'Python del backend (venv)'; Ok = (Test-Path $Python) },
    @{ Nombre = 'Node.js'; Ok = [bool](Get-Command node -ErrorAction SilentlyContinue) },
    @{ Nombre = 'Dependencias del frontend (node_modules)'; Ok = (Test-Path (Join-Path $Raiz 'node_modules')) },
    @{ Nombre = 'Cypress'; Ok = (Test-Path (Join-Path $Raiz 'node_modules\cypress')) },
    @{ Nombre = 'Google Chrome'; Ok = (Test-Path 'C:\Program Files\Google\Chrome\Application\chrome.exe') },
    @{ Nombre = 'Selenium (Python)'; Ok = (Funciona { python -c "import selenium" }) },
    @{ Nombre = 'JMeter 5.6.3'; Ok = (Test-Path $JMeter) },
    @{ Nombre = 'JDK 21 para JMeter'; Ok = (Test-Path (Join-Path $JavaHome 'bin\java.exe')) },
    @{ Nombre = 'pygount'; Ok = (Funciona { python -c "import pygount" }) },
    @{ Nombre = 'Docker Desktop encendido (ZAP y SonarQube)'; Ok = (Funciona { docker info }) }
)
foreach ($r in $revisiones) {
    if ($r.Ok) { Write-Host "  [OK]    $($r.Nombre)" -ForegroundColor Green }
    else { Write-Host "  [FALTA] $($r.Nombre)" -ForegroundColor Yellow }
}

Titulo 'Servicios desplegados'
foreach ($url in @('https://shifts-chash-version-amaya.vercel.app/', 'https://shiftschash-api.onrender.com/')) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 90
        Write-Host "  [OK]    $url ($($r.StatusCode))" -ForegroundColor Green
    } catch { Write-Host "  [FALLA] $url no responde" -ForegroundColor Red }
}
