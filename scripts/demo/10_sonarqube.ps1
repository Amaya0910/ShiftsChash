# Análisis con SonarQube Community (requiere Docker Desktop encendido).
# 1) Sin parámetros: levanta el servidor en http://localhost:9000 (usuario admin / admin la primera vez).
# 2) Cree un token en My Account > Security y ejecute: .\10_sonarqube.ps1 -Token <token>
param([string]$Token = '')
. "$PSScriptRoot\comun.ps1"
Titulo 'SonarQube'

if (-not (docker ps -a --format '{{.Names}}' | Select-String -SimpleMatch 'sonarqube')) {
    docker run -d --name sonarqube -p 9000:9000 sonarqube:community | Out-Null
} else { docker start sonarqube | Out-Null }
if (-not (Esperar-Url 'http://localhost:9000/api/system/status' 180)) { Write-Host 'SonarQube no arrancó' -ForegroundColor Red; exit 1 }
if (-not $Token) { Start-Process 'http://localhost:9000'; Write-Host 'Cree el token y vuelva a ejecutar con -Token.'; exit }

# Cobertura para el análisis
Set-Location $Backend
& $Python -m pytest -q -p no:warnings --cov=app --cov-report=xml | Out-Null
# El escáner corre en Docker (proyecto en /usr/src): la ruta de Windows del informe no le sirve
$xml = Join-Path $Backend 'coverage.xml'
$texto = [IO.File]::ReadAllText($xml) -replace '<source>[^<]*</source>', '<source>/usr/src/backend/app</source>'
[IO.File]::WriteAllText($xml, $texto)
Set-Location $Raiz
docker run --rm -e SONAR_HOST_URL=http://host.docker.internal:9000 -e SONAR_TOKEN=$Token `
    -v "${Raiz}:/usr/src" sonarsource/sonar-scanner-cli
Start-Process 'http://localhost:9000/dashboard?id=shiftcash'
