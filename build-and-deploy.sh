#!/bin/bash
# ness. Build & Deploy Script
# Desenvolvido por: ness.

set -e

echo "=== 🏗️  ness. BUILD & DEPLOY ==="
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: docker-compose.yml não encontrado"
    echo "Execute este script no diretório raiz do projeto"
    exit 1
fi

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Parando containers existentes...${NC}"
docker compose down 2>/dev/null || true

echo -e "${BLUE}🔨 Buildando aplicação...${NC}"
docker compose build --no-cache

echo -e "${BLUE}🚀 Iniciando containers...${NC}"
docker compose up -d

echo -e "${BLUE}⏳ Aguardando serviços iniciarem (30s)...${NC}"
sleep 30

echo ""
echo -e "${GREEN}✅ Build completo!${NC}"
echo ""
echo "📊 Status dos serviços:"
docker compose ps

echo ""
echo "🔗 Acesse: http://localhost:8502"
echo "👤 Login: admin / 123"
echo ""
echo "📋 Ver logs: docker compose logs -f app-agent"
echo "🛑 Parar: docker compose down"
echo ""
echo "Desenvolvido por ness. 🚀"





