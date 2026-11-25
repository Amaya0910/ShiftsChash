# Lighthouse sobre la portada (rendimiento, accesibilidad y buenas prácticas).
#   -Desplegada  mide la app en Vercel; sin el parámetro, compila y mide la versión local de producción
#   -Escritorio  usa el perfil de escritorio (por defecto, móvil)
param([switch]$Desplegada, [switch]$Escritorio)
. "$PSScriptRoot\comun.ps1"
Titulo 'Lighthouse'
Set-Location $Raiz
$env:CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

$proceso = $null
if ($Desplegada) { $url = 'https://shifts-chash-version-amaya.vercel.app/' }
else {
    npm run build | Out-Null
    $proceso = Start-Process cmd -ArgumentList '/c', 'npx vite preview --port 4173 --host 127.0.0.1 --strictPort' -PassThru -WindowStyle Hidden
    $url = 'http://127.0.0.1:4173/'
    if (-not (Esperar-Url $url 90)) { Write-Host 'El servidor de vista previa no arrancó.' -ForegroundColor Red; exit 1 }
}
$salida = Join-Path $Evidencias ('lighthouse_' + (Get-Date -Format 'yyyyMMdd_HHmm'))
$opciones = @('-y', 'lighthouse@12', $url, '--quiet', '--chrome-flags=--headless=new',
              '--only-categories=performance,accessibility,best-practices', '--output=html', "--output-path=$salida.html")
if ($Escritorio) { $opciones += '--preset=desktop' }
npx @opciones
if ($proceso) { Stop-Process -Id $proceso.Id -Force -ErrorAction SilentlyContinue; Get-NetTCPConnection -LocalPort 4173 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force } }
Start-Process "$salida.html"
