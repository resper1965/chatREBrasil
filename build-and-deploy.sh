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

# Detectar se estamos no WSL e Docker Desktop não está acessível
DOCKER_CMD="docker"
if ! command -v docker &> /dev/null; then
    DOCKER_EXE="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
    if [ -f "$DOCKER_EXE" ]; then
        echo "⚠️  Docker não encontrado no WSL, tentando usar Docker Desktop do Windows..."
        DOCKER_CMD="$DOCKER_EXE"
    else
        echo "❌ Erro: Docker não encontrado. Por favor:"
        echo "   1. Inicie o Docker Desktop no Windows"
        echo "   2. Habilite a integração WSL nas configurações do Docker Desktop"
        exit 1
    fi
fi

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se Docker está rodando
echo -e "${BLUE}🔍 Verificando Docker...${NC}"
if ! $DOCKER_CMD version &> /dev/null; then
    echo -e "${RED}❌ Erro: Docker Desktop não está rodando${NC}"
    echo -e "${YELLOW}   Por favor, inicie o Docker Desktop no Windows${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker encontrado!${NC}"
echo ""

echo -e "${BLUE}📦 Parando containers existentes...${NC}"
$DOCKER_CMD compose down 2>/dev/null || true

echo -e "${BLUE}🔨 Buildando aplicação (isso pode demorar alguns minutos)...${NC}"
$DOCKER_CMD compose build --no-cache

echo -e "${BLUE}🚀 Iniciando containers...${NC}"
$DOCKER_CMD compose up -d

echo -e "${BLUE}⏳ Aguardando serviços iniciarem (30s)...${NC}"
sleep 30

echo ""
echo -e "${GREEN}✅ Build completo!${NC}"
echo ""
echo "📊 Status dos serviços:"
$DOCKER_CMD compose ps

echo ""
echo -e "${GREEN}🔗 Acesse: http://localhost:8502${NC}"
echo -e "${YELLOW}👤 Login: admin / 123${NC}"
echo ""
echo "📋 Ver logs: $DOCKER_CMD compose logs -f app-agent"
echo "🛑 Parar: $DOCKER_CMD compose down"
echo ""
echo "Desenvolvido por ness. 🚀"






