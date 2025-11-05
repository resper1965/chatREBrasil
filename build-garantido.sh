#!/bin/bash
# Script de Build Garantido - Gabi. by ness.
# Garante que TODAS as alterações sejam aplicadas no container

set -e  # Parar em caso de erro

echo "🚀 Iniciando build garantido do chatREBrasil..."
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar arquivos críticos
echo "📋 Verificando arquivos críticos..."
FILES=(
    ".chainlit/config.toml"
    "app/app.py"
    "public/custom.css"
    "public/custom.js"
    "docker-compose.yml"
    "Dockerfile"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - AUSENTE!"
        exit 1
    fi
done
echo ""

# 2. Verificar configurações críticas no config.toml
echo "🔍 Verificando configurações MCP..."
if grep -q "enabled = true" .chainlit/config.toml; then
    echo -e "${GREEN}✓${NC} MCP habilitado"
else
    echo -e "${RED}✗${NC} MCP NÃO habilitado!"
    exit 1
fi

if grep -q "default_sidebar_state = \"open\"" .chainlit/config.toml; then
    echo -e "${GREEN}✓${NC} Sidebar configurada para abrir"
else
    echo -e "${YELLOW}⚠${NC} Sidebar não está configurada para abrir por padrão"
fi
echo ""

# 3. Parar containers existentes
echo "🛑 Parando containers existentes..."
docker compose down
echo -e "${GREEN}✓${NC} Containers parados"
echo ""

# 4. Remover imagem antiga (forçar rebuild)
echo "🗑️  Removendo imagem antiga para forçar rebuild completo..."
docker rmi chatrebrasil-app-agent:latest 2>/dev/null || echo "Imagem não encontrada (ok)"
docker compose rm -f app-agent 2>/dev/null || echo "Container não encontrado (ok)"
echo ""

# 5. Build SEM cache
echo "🏗️  Construindo imagem (sem cache)..."
docker compose build --no-cache app-agent
echo -e "${GREEN}✓${NC} Imagem construída"
echo ""

# 6. Iniciar containers
echo "▶️  Iniciando containers..."
docker compose up -d
echo -e "${GREEN}✓${NC} Containers iniciados"
echo ""

# 7. Aguardar app inicializar
echo "⏳ Aguardando aplicação inicializar (30 segundos)..."
sleep 30
echo ""

# 8. Verificar arquivos dentro do container
echo "🔍 Verificando arquivos DENTRO do container..."
echo ""

echo "📄 Verificando public/custom.css..."
docker compose exec app-agent cat /app/public/custom.css | head -5
echo ""

echo "📄 Verificando public/custom.js..."
if docker compose exec app-agent test -f /app/public/custom.js; then
    echo -e "${GREEN}✓${NC} custom.js existe no container"
    docker compose exec app-agent cat /app/public/custom.js | head -5
else
    echo -e "${RED}✗${NC} custom.js NÃO existe no container!"
fi
echo ""

echo "📄 Verificando .chainlit/config.toml..."
docker compose exec app-agent grep -A 2 "\[features.mcp\]" /app/.chainlit/config.toml
echo ""

echo "📄 Verificando app/app.py (on_chat_start)..."
docker compose exec app-agent grep -A 3 "def start():" /app/app/app.py
echo ""

# 9. Verificar logs
echo "📋 Últimas linhas dos logs:"
docker compose logs --tail=20 app-agent
echo ""

# 10. Resumo final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ BUILD COMPLETO!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Acesse: http://localhost:8502"
echo ""
echo "📝 Próximos passos:"
echo "   1. Limpar cache do navegador (Ctrl+Shift+Del)"
echo "   2. Hard reload (Ctrl+Shift+R)"
echo "   3. Fazer logout e login novamente"
echo "   4. Verificar:"
echo "      - Tela de login SEM logo do Chainlit"
echo "      - Sidebar aberta com 'My MCPs'"
echo "      - Console do navegador com mensagens do custom.js"
echo ""
echo "🔧 Para ver logs em tempo real:"
echo "   docker compose logs -f app-agent"
echo ""
echo "🐛 Para debug:"
echo "   docker compose exec app-agent bash"
echo ""
