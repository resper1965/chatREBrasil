# ness. Build & Deploy Script - PowerShell
# Desenvolvido por: ness.

Write-Host "=== 🏗️  ness. BUILD & DEPLOY ===" -ForegroundColor Cyan
Write-Host ""

# Mudar para diretório do projeto usando WSL path
$wslPath = "\\wsl.localhost\Ubuntu\home\resper\chatREBrasil"
if (Test-Path $wslPath) {
    Set-Location $wslPath
} else {
    # Tentar caminho alternativo
    $altPath = "C:\Users\$env:USERNAME\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu*\LocalState\rootfs\home\resper\chatREBrasil"
    $foundPath = Get-ChildItem -Path (Split-Path $altPath) -Filter "CanonicalGroupLimited.Ubuntu*" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($foundPath) {
        $fullPath = Join-Path $foundPath.FullName "LocalState\rootfs\home\resper\chatREBrasil"
        if (Test-Path $fullPath) {
            Set-Location $fullPath
        } else {
            Write-Host "❌ Erro: Diretório do projeto não encontrado" -ForegroundColor Red
            Write-Host "   Por favor, navegue manualmente até o diretório do projeto" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "❌ Erro: Diretório do projeto não encontrado" -ForegroundColor Red
        Write-Host "   Por favor, navegue manualmente até o diretório do projeto" -ForegroundColor Yellow
        exit 1
    }
}

if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Erro: docker-compose.yml não encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Parando containers existentes..." -ForegroundColor Blue
docker compose down

Write-Host "🔨 Buildando aplicação..." -ForegroundColor Blue
docker compose build --no-cache

Write-Host "🚀 Iniciando containers..." -ForegroundColor Blue
docker compose up -d

Write-Host "⏳ Aguardando serviços iniciarem (30s)..." -ForegroundColor Blue
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "✅ Build completo!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Status dos serviços:"
docker compose ps

Write-Host ""
Write-Host "🔗 Acesse: http://localhost:8502" -ForegroundColor Green
Write-Host "👤 Login: admin / 123" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Ver logs: docker compose logs -f app-agent"
Write-Host "🛑 Parar: docker compose down"
Write-Host ""
Write-Host "Desenvolvido por ness. 🚀" -ForegroundColor Cyan






