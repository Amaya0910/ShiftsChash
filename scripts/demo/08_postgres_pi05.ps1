# PI-05 sobre PostgreSQL: borrar una categoría con transacciones debe responder 409.
# Use una base VACÍA y desechable: las pruebas borran y recrean todas las tablas.
param([string]$Url = '')
. "$PSScriptRoot\comun.ps1"
Titulo 'PI-05 sobre PostgreSQL'

if (-not $Url) { $Url = Read-Host 'URL de una base vacía, p. ej. postgresql://postgres:CLAVE@localhost:5432/shiftcash_test' }
$env:TEST_DATABASE_URL = $Url
Set-Location $Backend
& $Python -m pytest -v -p no:warnings -k 'pi05 or pi13'
Remove-Item Env:\TEST_DATABASE_URL
