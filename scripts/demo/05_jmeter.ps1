# Prueba de carga con Apache JMeter (50 usuarios, 60 s de rampa, 10 iteraciones).
#   -Gui     abre el plan en la interfaz de JMeter para mostrarlo
#   -Render  ejecuta contra la API desplegada en lugar de la local
param([switch]$Gui, [switch]$Render)
. "$PSScriptRoot\comun.ps1"
Titulo 'JMeter: prueba de carga'

$env:JAVA_HOME = $JavaHome
$env:PATH = "$JavaHome\bin;$env:PATH"
$plan = Join-Path $Raiz 'tests\carga\shiftcash.jmx'
if ($Gui) { & $JMeter -t $plan; exit }

if ($Render) { $api = 'https://shiftschash-api.onrender.com'; $propiedades = @('-Jhost=shiftschash-api.onrender.com', '-Jport=443', '-Jprotocol=https') }
else { $api = $UrlApi; $propiedades = @('-Jhost=localhost', '-Jport=8000', '-Jprotocol=http') }

$credenciales = '{"email":"demo@correo.com","password":"Demo12345"}'
if ($Render) { $credenciales = Read-Host 'JSON de login de una cuenta de prueba en Render, p. ej. {"email":"...","password":"..."}' }
$token = (Invoke-RestMethod -Method Post -Uri "$api/auth/login" -ContentType 'application/json' -Body $credenciales).access_token
$categorias = Invoke-RestMethod -Uri "$api/categories/" -Headers @{ Authorization = "Bearer $token" }
$categoria = ($categorias | Where-Object { $_.type -eq 'expense' } | Select-Object -First 1).category_id

$salida = Join-Path $Evidencias ('jmeter_' + (Get-Date -Format 'yyyyMMdd_HHmm'))
New-Item -ItemType Directory -Force $salida | Out-Null
& $JMeter -n -t $plan @propiedades "-Jtoken=$token" "-Jcategoria=$categoria" -l "$salida\resultados.jtl" -e -o "$salida\reporte"
Start-Process "$salida\reporte\index.html"
