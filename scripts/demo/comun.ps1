# Rutas y utilidades comunes de los scripts de demostración.
$Raiz = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Backend = Join-Path $Raiz 'backend'
$Python = Join-Path $Backend 'venv\Scripts\python.exe'
$Herramientas = Join-Path $env:LOCALAPPDATA 'shiftcash-tools'
$JavaHome = Join-Path $Herramientas 'jdk\jdk-21.0.13.1+2'
$JMeter = Join-Path $Herramientas 'jmeter\apache-jmeter-5.6.3\bin\jmeter.bat'
$Evidencias = Join-Path $Raiz 'docs\evidencias'
$UrlApi = 'http://localhost:8000'
$UrlWeb = 'http://127.0.0.1:5173'

function Esperar-Url([string]$Url, [int]$Segundos = 60) {
    $limite = (Get-Date).AddSeconds($Segundos)
    while ((Get-Date) -lt $limite) {
        try { Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 | Out-Null; return $true } catch { Start-Sleep -Seconds 2 }
    }
    return $false
}

function Titulo([string]$Texto) {
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor DarkGray
    Write-Host "  $Texto" -ForegroundColor Cyan
    Write-Host ('=' * 70) -ForegroundColor DarkGray
}
