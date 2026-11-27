# Menú de las pruebas de ShiftCash para la demostración en vivo.
# Cada opción corre una prueba real del documento (Segunda y Tercera parte).
# Antes: ejecute 01_levantar_app.ps1 -BaseNueva (app local con datos de prueba).
. "$PSScriptRoot\comun.ps1"
Set-Location $Raiz

function Pytest([string]$Titulo, [string[]]$Argumentos) {
    Titulo $Titulo
    Set-Location $Backend
    & $Python -m pytest -v -p no:warnings @Argumentos
    Set-Location $Raiz
}

function Docker-Listo {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) { Write-Host 'Docker Desktop no está encendido: ábralo y espere a que diga «Engine running».' -ForegroundColor Red; return $false }
    return $true
}

$opciones = [ordered]@{
    '1'  = 'Unitarias: caja negra y caja blanca (58 casos, pytest)'
    '2'  = 'Integración incremental ascendente y por hilos (40 pruebas, pytest)'
    '3'  = 'Integración de punta a punta en la interfaz de Cypress (8 pruebas)'
    '4'  = 'Sistema - Seguridad: autenticación, aislamiento, hash, CORS, cabeceras (pytest)'
    '5'  = 'Sistema - Seguridad: escaneo OWASP ZAP del frontend desplegado (Docker)'
    '6'  = 'Sistema - Rendimiento: JMeter, 50 usuarios y 1 500 peticiones'
    '7'  = 'Sistema - Usabilidad: Lighthouse (accesibilidad) y la tarea PU-06'
    '8'  = 'Sistema - Portabilidad: la app en una ventana del tamaño de un celular'
    '9'  = 'Sistema - Fiabilidad: recurrentes, entradas inválidas, D-15 y /salud'
    '10' = 'Sistema - Mantenibilidad: tamaño, complejidad, suite CK y estimación'
    '11' = 'Sistema - Mantenibilidad: panel de SonarQube (Docker)'
    '12' = 'Aceptación automatizada con Selenium (Chrome se maneja solo)'
    '13' = 'PI-05 sobre PostgreSQL real (Docker)'
    '14' = 'Suite completa: 98 pruebas con reporte de cobertura'
}

while ($true) {
    Titulo 'ShiftCash - pruebas en vivo'
    foreach ($k in $opciones.Keys) { Write-Host ('  {0,3}. {1}' -f $k, $opciones[$k]) }
    Write-Host '    0. Salir'
    $op = Read-Host "`nOpción"
    switch ($op) {
        '0'  { return }
        '1'  { Pytest $opciones['1'] @('tests/test_unitarias.py') }
        '2'  { Pytest $opciones['2'] @('tests/test_integracion.py') }
        '3'  { & "$PSScriptRoot\03_cypress.ps1" -Abrir }
        '4'  { Pytest $opciones['4'] @('tests/test_integracion.py', '-k',
                 'd06 or pi01 or rnf01 or rnf03 or ps07 or pi15 or pi14 or ajeno or ajena or login or duplicado or pi17') }
        '5'  { if (Docker-Listo) { & "$PSScriptRoot\09_zap.ps1" } }
        '6'  { & "$PSScriptRoot\05_jmeter.ps1" }
        '7'  { & "$PSScriptRoot\07_lighthouse.ps1"
               Write-Host "`nPU-06: con un cronómetro, registre un gasto de 25 000 en Alimentación («Almuerzo»)." -ForegroundColor Yellow
               Start-Process "$UrlWeb/login" }
        '8'  { $chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
               Start-Process $chrome -ArgumentList '--new-window', '--window-size=390,844', "--app=$UrlWeb/"
               Write-Host 'Ventana de 390 x 844 (celular). En otra pestaña use F12 > modo dispositivo para cambiar de equipo.' -ForegroundColor Yellow }
        '9'  { Pytest $opciones['9'] @('-k', 'pi08 or pi09 or pi10 or pi11 or pi12 or d15 or salud or d14 or pi13')
               Titulo 'API desplegada: /salud'
               try { (Invoke-WebRequest 'https://shiftschash-api.onrender.com/salud' -UseBasicParsing -TimeoutSec 90).Content }
               catch { Write-Host 'La API desplegada no respondió (D-09): use la local.' -ForegroundColor Red } }
        '10' { & "$PSScriptRoot\06_metricas.ps1" }
        '11' { if (Docker-Listo) { & "$PSScriptRoot\10_sonarqube.ps1" } }
        '12' { & "$PSScriptRoot\04_selenium.ps1" }
        '13' { if (Docker-Listo) { & "$PSScriptRoot\08_postgres_pi05.ps1" } }
        '14' { & "$PSScriptRoot\02_pruebas_backend.ps1" }
        default { Write-Host 'Opción no válida' -ForegroundColor Red }
    }
    Set-Location $Raiz
    Read-Host "`nEnter para volver al menú"
}
