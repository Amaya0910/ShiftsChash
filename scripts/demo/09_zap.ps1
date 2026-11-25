# Escaneo de seguridad con OWASP ZAP (requiere Docker Desktop encendido).
#   -Api  escanea la API desplegada a partir de su OpenAPI; sin el parámetro, el frontend en Vercel
param([switch]$Api)
. "$PSScriptRoot\comun.ps1"
Titulo 'OWASP ZAP'

$salida = Join-Path $Evidencias 'zap'
New-Item -ItemType Directory -Force $salida | Out-Null
$volumen = "${salida}:/zap/wrk:rw"
if ($Api) {
    docker run --rm -v $volumen -t ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py `
        -t https://shiftschash-api.onrender.com/openapi.json -f openapi -r zap_api.html
    Start-Process (Join-Path $salida 'zap_api.html')
} else {
    docker run --rm -v $volumen -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py `
        -t https://shifts-chash-version-amaya.vercel.app/ -r zap_frontend.html
    Start-Process (Join-Path $salida 'zap_frontend.html')
}
