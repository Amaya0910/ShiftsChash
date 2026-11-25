# Levanta la API y el frontend en local con una base SQLite de demostración
# y carga datos ficticios (usuario demo@correo.com / Demo12345).
param([switch]$BaseNueva)
. "$PSScriptRoot\comun.ps1"
Titulo 'Levantar ShiftCash en local'

$carpetaDemo = Join-Path $Raiz '.demo'
New-Item -ItemType Directory -Force $carpetaDemo | Out-Null
$baseDatos = Join-Path $carpetaDemo 'demo.db'
if ($BaseNueva -and (Test-Path $baseDatos)) { Remove-Item $baseDatos -Force }
$urlBase = 'sqlite:///' + ($baseDatos -replace '\\', '/')

$comandoApi = "`$env:DATABASE_URL='$urlBase'; `$env:SECRET_KEY='clave-local-demo'; `$env:ALGORITHM='HS256'; " +
              "`$env:ACCESS_TOKEN_EXPIRE_MINUTES='600'; `$env:BACKEND_URL='$UrlApi'; " +
              "Set-Location '$Backend'; & '$Python' -m uvicorn app.main:app --port 8000"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $comandoApi -WindowStyle Minimized

$comandoWeb = "`$env:VITE_API_URL='$UrlApi'; if (-not `$env:VITE_GOOGLE_CLIENT_ID) { `$env:VITE_GOOGLE_CLIENT_ID='local-demo.apps.googleusercontent.com' }; " +
              "Set-Location '$Raiz'; npm run dev -- --host 127.0.0.1"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $comandoWeb -WindowStyle Minimized

Write-Host 'Esperando a la API...'
if (-not (Esperar-Url "$UrlApi/" 60)) { Write-Host 'La API no arrancó; revise la ventana minimizada.' -ForegroundColor Red; exit 1 }
& $Python (Join-Path $PSScriptRoot 'datos_demo.py')
Write-Host 'Esperando al frontend...'
if (-not (Esperar-Url $UrlWeb 60)) { Write-Host 'El frontend no arrancó; revise la ventana minimizada.' -ForegroundColor Red; exit 1 }

Start-Process "$UrlWeb/login"
Write-Host ''
Write-Host "API:       $UrlApi  (documentación en $UrlApi/docs)" -ForegroundColor Green
Write-Host "Frontend:  $UrlWeb" -ForegroundColor Green
Write-Host 'Usuario:   demo@correo.com / Demo12345' -ForegroundColor Green
Write-Host 'Para cerrar, cierre las dos ventanas de PowerShell minimizadas.'
