# Pruebas de aceptación con Selenium: abre Chrome y recorre PA-01, 02, 03, 05, 06 y 08.
#   -Desplegada  las corre contra la aplicación en Vercel (requiere SC_EMAIL y SC_PASS de una cuenta real)
param([switch]$Desplegada)
. "$PSScriptRoot\comun.ps1"
Titulo 'Selenium: pruebas de aceptación'

if ($Desplegada) {
    $env:SC_BASE_URL = 'https://shifts-chash-version-amaya.vercel.app'
    if (-not $env:SC_EMAIL) { Write-Host 'Defina $env:SC_EMAIL y $env:SC_PASS con una cuenta de prueba.' -ForegroundColor Red; exit 1 }
} else {
    if (-not (Esperar-Url "$UrlApi/" 5)) { Write-Host 'Primero ejecute 01_levantar_app.ps1' -ForegroundColor Red; exit 1 }
    $env:SC_BASE_URL = $UrlWeb
    $env:SC_EMAIL = 'demo@correo.com'
    $env:SC_PASS = 'Demo12345'
}
Remove-Item Env:\SC_HEADLESS -ErrorAction SilentlyContinue   # se ve el navegador
python (Join-Path $Raiz 'tests\aceptacion_selenium.py')
Write-Host "Capturas en $Evidencias" -ForegroundColor Green
