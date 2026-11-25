# Pruebas de integración con Cypress contra la app local (01_levantar_app.ps1 debe estar corriendo).
#   -Abrir  abre la interfaz gráfica de Cypress para mostrar cada prueba en vivo
param([switch]$Abrir)
. "$PSScriptRoot\comun.ps1"
Titulo 'Cypress: pruebas de integración'

if (-not (Esperar-Url "$UrlApi/" 5)) { Write-Host 'Primero ejecute 01_levantar_app.ps1' -ForegroundColor Red; exit 1 }
Set-Location $Raiz
$env:CYPRESS_BASE_URL = $UrlWeb
$variables = "API=$UrlApi,SC_EMAIL=demo@correo.com,SC_PASS=Demo12345"
if ($Abrir) { npx cypress open --e2e --browser chrome --env $variables }
else { npx cypress run --spec cypress/e2e/integracion.cy.js --env $variables }
