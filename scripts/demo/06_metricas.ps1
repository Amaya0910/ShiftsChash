# Métricas internas (tamaño, complejidad, suite CK) y estimación.
. "$PSScriptRoot\comun.ps1"
Set-Location $Raiz
$env:PYTHONIOENCODING = 'utf-8'

Titulo 'Tamaño del código (script propio, sin pruebas)'
python docs/scripts/metricas.py tamano --sin-pruebas

Titulo 'Tamaño con pygount'
$archivos = git ls-files --cached --others --exclude-standard | Where-Object {
    $_ -match '\.(py|jsx|js|css|html|json|yml)$' -and $_ -notmatch '^(docs/|dist/|scripts/|backend/tests/|tests/|cypress/|cypress\.config\.js|package-lock\.json)'
}
python -m pygount --format=summary @archivos

Titulo 'Complejidad ciclomática (McCabe)'
python docs/scripts/metricas.py complejidad

Titulo 'Componentes del frontend con más puntos de decisión'
python docs/scripts/metricas.py frontend

Titulo 'Suite de Chidamber y Kemerer'
python docs/scripts/metricas.py ck

Titulo 'Estimación: cinco modelos y presupuesto'
python docs/scripts/estimacion.py
