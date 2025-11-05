# 🔧 Guia Rápido - Problemas Comuns

## ❌ Problema: MCP não aparece

### O que é MCP?
MCP são as ferramentas que conectam ao banco de dados. No Chainlit, elas ficam na barra lateral esquerda.

### Solução:

1. **Verifique se o MCP está configurado:**
```bash
# Veja se os servidores MCP estão no config
cat .chainlit/config.toml | grep -A 5 "\[mcp\]"
```

2. **Reinicie a aplicação:**
```bash
docker-compose down
docker-compose up -d
```

3. **Veja os logs:**
```bash
docker-compose logs app-agent | grep -i mcp
```

**IMPORTANTE:** O MCP do Chainlit não funciona via handlers `@cl.on_mcp_connect`. Ele é acessado pela barra lateral ("My MCPs").

---

## ❌ Problema: Chat não persiste

### Sintomas:
- Fecha o navegador e perde o histórico
- Menu lateral não mostra conversas antigas
- Não consegue retomar conversas

### Solução:

1. **Verifique se a persistência está habilitada:**
```bash
cat .chainlit/config.toml | grep -A 2 "\[persistence\]"
# Deve mostrar: enabled = true
```

2. **Verifique se o PostgreSQL está rodando:**
```bash
docker-compose ps | grep db-persist
# Deve estar "Up"
```

3. **Teste conexão ao banco:**
```bash
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "SELECT COUNT(*) FROM threads;"
```

4. **Verifique se a URL do banco está correta:**
```bash
docker-compose logs app-agent | grep CHAINLIT_DATABASE_URL
```

5. **Verifique se há threads no banco:**
```bash
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "
SELECT id, created_at, name FROM threads ORDER BY created_at DESC LIMIT 5;
"
```

### Se ainda não funcionar:

```bash
# Recrie o banco do zero
docker-compose down -v  # CUIDADO: Apaga dados!
docker-compose up -d

# Aguarde ~30 segundos para o banco inicializar
sleep 30

# Inicie uma nova conversa e envie uma mensagem
# Então verifique:
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "
SELECT COUNT(*) FROM threads;
"
```

---

## ❌ Problema: Menu lateral não abre

### Sintomas:
- Clica no menu (☰) e nada acontece
- Não aparece lista de conversas
- Não tem opção de "My MCPs"

### Causas Comuns:
1. **Não há conversas salvas ainda** → Menu fica vazio
2. **Persistência não está funcionando** → Veja seção acima
3. **Problema no JavaScript/CSS** → Limpe o cache

### Solução:

1. **Limpe o cache do navegador:**
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Ou abra em aba anônima

2. **Crie uma conversa primeiro:**
   - Envie qualquer mensagem
   - Aguarde a resposta
   - Feche e abra o navegador
   - O menu deve mostrar essa conversa

3. **Verifique no console do navegador:**
   - Pressione F12
   - Aba "Console"
   - Procure por erros em vermelho

4. **Verifique se está usando HTTPS:**
   - Se estiver atrás de um proxy/load balancer
   - Pode haver problemas com WebSocket

---

## ❌ Problema: Logo Chainlit na autenticação

### Sintomas:
- Logo do Chainlit aparece na tela de login
- CSS não remove o logo

### Solução Temporária:

1. **Limpe cache do navegador** (Ctrl+Shift+Delete)

2. **Force reload** (Ctrl+F5 ou Ctrl+Shift+R)

3. **Verifique se o CSS está sendo carregado:**
   - F12 → Aba "Network"
   - Procure por `custom.css`
   - Se estiver 404, o arquivo não está no build

### Solução Permanente (Rebuild):

```bash
# Rebuild da imagem com o novo CSS
docker-compose down
docker-compose build --no-cache app-agent
docker-compose up -d
```

### Solução Alternativa (Substituir logo):

```bash
# Coloque seu logo no lugar
cp /caminho/do/seu/logo.png public/logo-light.png
cp /caminho/do/seu/logo.png public/logo-dark.png

# Rebuild
docker-compose build app-agent
docker-compose up -d
```

---

## 🔧 Comandos Úteis

### Ver logs em tempo real:
```bash
docker-compose logs -f app-agent
```

### Reiniciar apenas a aplicação:
```bash
docker-compose restart app-agent
```

### Rebuild completo:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Verificar se tudo está rodando:
```bash
docker-compose ps
```

### Acessar o PostgreSQL:
```bash
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit
```

### Ver estrutura das tabelas:
```sql
\dt  -- Lista tabelas
\d threads  -- Estrutura da tabela threads
SELECT * FROM threads LIMIT 5;  -- Ver dados
```

---

## ⚠️ IMPORTANTE: MCP no Chainlit

O Chainlit **NÃO** usa `@cl.on_mcp_connect` para MCP.

### Como funciona:

1. **MCP é configurado no `.chainlit/config.toml`**
2. **Aparece na barra lateral** como "My MCPs"
3. **Usuário conecta manualmente** pela interface

### Se você quer conexão automática:

Use o **botão "🔌 Conectar Banco de Dados"** que foi criado.

Ele chama a função `connect_to_default_mssql()` que:
- Pega credenciais do `.env`
- Conecta via MCP sessions
- Exibe mensagem de sucesso/erro

---

## 📊 Checklist Rápido

Antes de reportar problema:

- [ ] `docker-compose ps` → Todos "Up"?
- [ ] `docker-compose logs app-agent` → Sem erros?
- [ ] Cache do navegador limpo?
- [ ] Testou em aba anônima?
- [ ] PostgreSQL está acessível?
- [ ] Variável `CHAINLIT_DATABASE_URL` está correta?
- [ ] Rebuild foi feito após mudanças?
- [ ] Aguardou 30 segundos após `docker-compose up`?

---

## 🆘 Último Recurso

Se nada funcionar:

```bash
# ATENÇÃO: Isso apaga TODOS os dados!
docker-compose down -v
docker volume rm chatrebrasil_postgres_data chatrebrasil_mssql_data

# Rebuild do zero
docker-compose build --no-cache
docker-compose up -d

# Aguarde inicialização
sleep 30

# Acesse e teste
```

---

## 📞 Contato

Se o problema persistir, forneça:
1. Saída de `docker-compose ps`
2. Últimas 50 linhas dos logs: `docker-compose logs --tail=50 app-agent`
3. Screenshot do problema
4. Console do navegador (F12)
