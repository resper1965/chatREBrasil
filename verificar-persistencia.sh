#!/bin/bash
# Script de Verificação de Persistência - Chainlit

set -e

echo "🔍 Verificando Configuração de Persistência do Chainlit..."
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Verificar DATABASE_URL no container
echo "1️⃣ Verificando DATABASE_URL no container..."
DB_URL=$(docker compose exec -T app-agent env | grep DATABASE_URL || echo "")
if [ -z "$DB_URL" ]; then
    echo -e "${RED}✗${NC} DATABASE_URL não encontrada no container!"
    echo "   Corrija docker-compose.yml e rebuild"
    exit 1
else
    echo -e "${GREEN}✓${NC} DATABASE_URL encontrada"
    echo "   $DB_URL"
fi
echo ""

# 2. Verificar PostgreSQL rodando
echo "2️⃣ Verificando se PostgreSQL está rodando..."
PG_STATUS=$(docker compose ps db-persist | grep -i "running" || echo "")
if [ -z "$PG_STATUS" ]; then
    echo -e "${RED}✗${NC} PostgreSQL NÃO está rodando!"
    echo "   Execute: docker compose up -d db-persist"
    exit 1
else
    echo -e "${GREEN}✓${NC} PostgreSQL rodando"
fi
echo ""

# 3. Verificar conexão com PostgreSQL
echo "3️⃣ Testando conexão com PostgreSQL..."
docker compose exec -T db-persist psql -U chainlit -d chainlit -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Conexão com PostgreSQL OK"
else
    echo -e "${RED}✗${NC} Erro ao conectar no PostgreSQL!"
    exit 1
fi
echo ""

# 4. Verificar tabelas do Chainlit
echo "4️⃣ Verificando tabelas do Chainlit no PostgreSQL..."
TABLES=$(docker compose exec -T db-persist psql -U chainlit -d chainlit -t -c "\dt" 2>/dev/null | grep -i "thread\|step\|user\|element" || echo "")
if [ -z "$TABLES" ]; then
    echo -e "${YELLOW}⚠${NC}  Tabelas do Chainlit NÃO encontradas"
    echo "   Isso é normal se for primeira execução"
    echo "   As tabelas serão criadas automaticamente ao iniciar chat"
else
    echo -e "${GREEN}✓${NC} Tabelas do Chainlit encontradas:"
    docker compose exec -T db-persist psql -U chainlit -d chainlit -t -c "\dt"
fi
echo ""

# 5. Verificar asyncpg instalado
echo "5️⃣ Verificando asyncpg instalado no container..."
ASYNCPG=$(docker compose exec -T app-agent pip list | grep asyncpg || echo "")
if [ -z "$ASYNCPG" ]; then
    echo -e "${RED}✗${NC} asyncpg NÃO instalado!"
    echo "   Adicione 'asyncpg>=0.29.0' ao requirements.txt e rebuild"
    exit 1
else
    echo -e "${GREEN}✓${NC} asyncpg instalado"
    echo "   $ASYNCPG"
fi
echo ""

# 6. Verificar config.toml
echo "6️⃣ Verificando persistence no config.toml..."
PERSIST=$(docker compose exec -T app-agent grep -A 2 "\[persistence\]" /app/.chainlit/config.toml)
if echo "$PERSIST" | grep -q "enabled = true"; then
    echo -e "${GREEN}✓${NC} Persistence habilitada no config.toml"
else
    echo -e "${RED}✗${NC} Persistence NÃO habilitada no config.toml!"
    echo "   Adicione 'enabled = true' na seção [persistence]"
    exit 1
fi
echo ""

# 7. Verificar logs do Chainlit
echo "7️⃣ Verificando logs do Chainlit para erros de persistência..."
ERRORS=$(docker compose logs app-agent | grep -i "database\|persist" | grep -i "error\|fail" | tail -5 || echo "")
if [ -n "$ERRORS" ]; then
    echo -e "${RED}✗${NC} Erros relacionados a persistência encontrados nos logs:"
    echo "$ERRORS"
else
    echo -e "${GREEN}✓${NC} Nenhum erro de persistência nos logs"
fi
echo ""

# 8. Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ VERIFICAÇÃO COMPLETA${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Próximos passos para testar:"
echo "   1. Acesse: http://localhost:8502"
echo "   2. Faça login"
echo "   3. Envie algumas mensagens"
echo "   4. Feche o navegador"
echo "   5. Reabra http://localhost:8502"
echo "   6. Verifique se há botão 'History' na sidebar"
echo "   7. Clique em 'History' e veja se seus chats estão salvos"
echo ""
echo "🔍 Para verificar dados salvos no PostgreSQL:"
echo "   docker compose exec db-persist psql -U chainlit -d chainlit"
echo "   SELECT * FROM threads;"
echo "   SELECT * FROM steps;"
echo ""
echo "📋 Para ver estrutura completa das tabelas:"
echo "   docker compose exec db-persist psql -U chainlit -d chainlit -c '\d'"
echo ""
