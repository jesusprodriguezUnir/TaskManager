# Script para levantar OpenStudy en Windows (Back + Front)

$env:OPENSTUDY_DEPLOY_LOG='.logs/openstudy-deploy.log'

Write-Host ">>> Levantando Backend y Base de Datos (Docker)..." -ForegroundColor Cyan
bash -lc './deploy.sh'

if ($LASTEXITCODE -ne 0) {
    Write-Host "!!! Error al levantar el backend. Revisa los logs en .logs/openstudy-deploy.log" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ">>> Backend listo. Verificando dependencias del Frontend..." -ForegroundColor Green
Set-Location web
if (-not (Test-Path "node_modules")) {
    Write-Host ">>> node_modules no encontrado. Instalando dependencias (esto puede tardar un poco)..." -ForegroundColor Yellow
    pnpm install
}

Write-Host ">>> Iniciando Frontend en modo desarrollo..." -ForegroundColor Green
pnpm dev
