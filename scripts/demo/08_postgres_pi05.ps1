# PI-05 sobre PostgreSQL: borrar una categoría con transacciones debe responder 409.
# Sin parámetros crea una base PostgreSQL 16 desechable en Docker (requiere Docker Desktop encendido).
# Con -Url usa otra base, que debe estar VACÍA: las pruebas borran y recrean todas las tablas.
param([string]$Url = '')
. "$PSScriptRoot\comun.ps1"
Titulo 'PI-05 sobre PostgreSQL'

$contenedor = $false
if (-not $Url) {
    docker rm -f shiftcash-pg 2>$null | Out-Null
    docker run -d --name shiftcash-pg -e POSTGRES_PASSWORD=demo -p 5433:5432 postgres:16 | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host 'No se pudo crear la base: encienda Docker Desktop.' -ForegroundColor Red; exit 1 }
    Write-Host 'Esperando a PostgreSQL...'
    for ($i = 0; $i -lt 30; $i++) {
        docker exec shiftcash-pg pg_isready -U postgres 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { break }
        Start-Sleep -Seconds 2
    }
    Start-Sleep -Seconds 2
    $Url = 'postgresql://postgres:demo@localhost:5433/postgres'
    $contenedor = $true
}
$env:TEST_DATABASE_URL = $Url
Set-Location $Backend
& $Python -m pytest -v -p no:warnings -k 'pi05 or pi13'
Remove-Item Env:\TEST_DATABASE_URL
if ($contenedor) { docker rm -f shiftcash-pg | Out-Null }
