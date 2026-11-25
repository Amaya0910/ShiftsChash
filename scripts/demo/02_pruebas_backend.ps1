# Pruebas unitarias y de integración con pytest, y reporte de cobertura.
param([string]$Filtro = '')
. "$PSScriptRoot\comun.ps1"
Titulo 'pytest: pruebas unitarias y de integración con cobertura'

Set-Location $Backend
$argumentos = @('-m', 'pytest', '-v', '-p', 'no:warnings', '--cov=app', '--cov-report=term')
if ($Filtro) { $argumentos += @('-k', $Filtro) }                       # solo algunas pruebas
else { $argumentos += '--cov-report=html:../docs/cobertura_html' }     # suite completa: reporte HTML
& $Python @argumentos
if (-not $Filtro) { Start-Process (Join-Path $Raiz 'docs\cobertura_html\index.html') }
