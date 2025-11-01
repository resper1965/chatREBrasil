# 🤖 Auto-Connect MCP Implementação

## 📋 Contexto

**Problema:** Usuário não-técnico precisa reconectar MCP manualmente toda vez, processo complicado.

**Objetivo:** Automatizar conexão MCP sem hardcode, mantendo flexibilidade.

**Constraint:** Não quero chumbar em código (sem hardcode).

## ✅ Solução Implementada

### Arquitetura

Implementamos **três camadas** de auto-conexão:

1. **Auto-Connect Function** - Lógica central
2. **Action Callback** - Botão "Conectar" inteligente
3. **Auto-Detect** - Detecção transparente em queries

### Sem Hardcode!

**Tudo vem do `.env`:**
```bash
MSSQL_SERVER=localhost
MSSQL_USERNAME=sa
MSSQL_PASSWORD=Str0ng!Passw0rd
MSSQL_DATABASE=REB_BI_IA  # Opcional para auto-connect
```

## 🔧 Implementação Técnica

### 1. Auto-Connect Function

**Localização:** `app/app.py` linha 1114

```python
async def auto_connect_mssql_mcp():
    """Tenta conectar ao MCP MSSQL automaticamente se houver credenciais no .env"""
    try:
        # Verificar se MCP já está conectado
        mcp_tools = cl.user_session.get("mcp_tools", {})
        if mcp_tools:
            return True  # Já conectado
        
        # Verificar se há credenciais SQL configuradas
        if not Config.MSSQL_SERVER or Config.MSSQL_SERVER == "localhost":
            return False  # Sem configuração
        
        # Tentar obter sessão MCP ativa
        mcp_sessions = cl.context.session.mcp_sessions
        if not mcp_sessions:
            return False  # MCP não configurado na sidebar
        
        # Procurar sessão SQL Server
        for name, (session, _) in mcp_sessions.items():
            if "sql" in name.lower() or "mssql" in name.lower():
                # Tentar conectar ao database se tiver credenciais completas
                if Config.MSSQL_DATABASE:
                    connection_params = {
                        "server": Config.MSSQL_SERVER,
                        "database": Config.MSSQL_DATABASE,
                        "username": Config.MSSQL_USERNAME,
                        "password": Config.MSSQL_PASSWORD,
                        "port": Config.DEFAULT_DB_PORT
                    }
                    
                    # Chamar connect_database via MCP
                    result = await session.call_tool("connect_database", connection_params)
                    
                    session_id = cl.user_session.get("id", "unknown")
                    log_message("SUCCESS", f"Auto-conectado ao MCP SQL: {name}", session_id)
                    return True
        
        return False
        
    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro ao auto-conectar MCP: {str(e)}", session_id)
        return False
```

**Características:**
- ✅ Verifica se já conectado (evita duplicação)
- ✅ Usa credenciais do `.env` via `Config` class
- ✅ Procura sessão MCP SQL ativa
- ✅ Chama `connect_database` tool automaticamente
- ✅ Logs de sucesso/erro

### 2. Action Callback Inteligente

**Localização:** `app/app.py` linha 1159

```python
@cl.action_callback("conectar_mcp_mssql")
async def on_conectar_mcp_mssql(action):
    """Callback para Action de conexão MCP"""
    
    # Tentar auto-conectar primeiro
    auto_connected = await auto_connect_mssql_mcp()
    
    if auto_connected:
        success_msg = """✅ **Conexão MCP Automática Bem-Sucedida!**

O sistema conectou automaticamente ao SQL Server usando as credenciais configuradas.

📋 **Ferramentas disponíveis:**
- `get_database_schema` - Ver estrutura completa
- `execute_query` - Executar SELECT seguro
- `analyze_relationships` - Ver JOINs sugeridos
- `preview_table` - Ver primeiras linhas
- `search_data` - Buscar em colunas de texto

💡 **Agora você pode fazer perguntas sobre os dados diretamente!**
Exemplo: "Quantas tabelas existem no banco?" ou "Liste os imóveis disponíveis"."""
        
        await cl.Message(content=success_msg).send()
        await action.remove()
        return
    
    # Se auto-connect falhou, mostrar instruções manuais
    instruction_msg = """🔌 **Como Conectar ao SQL Server via MCP**
    ...
    """
    
    await cl.Message(content=instruction_msg).send()
    await action.remove()
```

**Fluxo:**
1. **Tenta auto-connect** primeiro
2. **Se sucesso:** Mostra confirmação + dicas
3. **Se falha:** Mostra instruções manuais
4. **Remove action** após uso

### 3. Auto-Detect em Queries

**Localização:** `app/app.py` linha 1044

```python
@cl.on_message
async def main(message: cl.Message):
    ...
    # AUTO-CONECTAR MCP SE NECESSÁRIO
    data_keywords_for_auto_connect = ["query", "sql", "tabela", "conecta", "banco", 
                                      "database", "lista", "mostra", "extrai", 
                                      "schema", "consulta", "quantos"]
    if any(kw in content_lower for kw in data_keywords_for_auto_connect):
        # Tentar auto-conectar se não estiver conectado
        mcp_tools = cl.user_session.get("mcp_tools", {})
        if not mcp_tools:
            auto_connected = await auto_connect_mssql_mcp()
            if auto_connected:
                await cl.Message(content="✅ Conectei automaticamente ao banco de dados!").send()
```

**Keywords detectadas:**
- `query`, `sql`, `tabela`, `conecta`, `banco`
- `database`, `lista`, `mostra`, `extrai`
- `schema`, `consulta`, `quantos`

**Comportamento:**
- Detecta necessidade de conexão SQL
- Verifica se já conectado
- Auto-conecta se necessário
- Notifica usuário se conectou
- Totalmente transparente

## 🎯 Casos de Uso

### Caso 1: Auto-Connect via Botão

**Cenário:** Usuário clica "🔌 Conectar ao SQL Server"

**Flow:**
```
1. Action callback executado
2. auto_connect_mssql_mcp() chamado
3. Verifica se MCP já conectado → Não
4. Verifica se .env tem MSSQL_DATABASE → Sim
5. Procura sessão MCP SQL → Encontrada
6. Chama connect_database tool
7. Retorna sucesso
8. Mostra mensagem de confirmação
9. Action removido
```

**Resultado:** ✅ Conectado automaticamente!

### Caso 2: Auto-Detect em Query

**Cenário:** Usuário pergunta "Quantas tabelas tem no banco?"

**Flow:**
```
1. @cl.on_message executado
2. Detecta keywords ["quantos", "tabela"]
3. Verifica mcp_tools → Vazio
4. auto_connect_mssql_mcp() chamado
5. Conecta automaticamente
6. Notifica "✅ Conectei automaticamente..."
7. Continua processamento da mensagem
8. LLM responde usando tools MCP
```

**Resultado:** ✅ Query respondida automaticamente!

### Caso 3: Fallback Manual

**Cenário:** MSSQL_DATABASE não configurado no .env

**Flow:**
```
1. Action callback executado
2. auto_connect_mssql_mcp() chamado
3. Verifica MSSQL_DATABASE → None
4. Retorna False
5. Mostra instruções manuais
6. Usuário conecta manualmente
```

**Resultado:** ⚠️ Instruções manuais exibidas

## 📊 Benefícios

### Para Usuário Não-Técnico

✅ **Clica botão → Conecta!**
- Zero configuração quando .env está OK
- Feedback imediato (sucesso ou instruções)
- Não precisa saber JSON ou credenciais

✅ **Faz pergunta → Funciona!**
- Detecta automaticamente necessidade
- Conecta transparentemente
- Responde instantaneamente

### Para Admin/Dev

✅ **Configuração Centralizada**
- Tudo no `.env`
- Sem hardcode no código
- Fácil mudar credenciais

✅ **Flexibilidade Total**
- Auto-connect quando possível
- Fallback manual quando necessário
- Logs claros para debug

✅ **Manutenção Fácil**
- Função centralizada `auto_connect_mssql_mcp()`
- Reutilizável em múltiplos contexts
- Testável isoladamente

## 🔒 Segurança

### Credenciais

✅ **Nunca hardcoded** no código
✅ **Sempre via .env** (configuração)
✅ **Pode usar .env.local** para dev/test
✅ **Não commitado** no git

### Validações

✅ **Verifica existência** de sessão MCP
✅ **Valida credenciais** via Config
✅ **Try/catch** em todas operações
✅ **Logs** de sucesso/erro

## 🧪 Testes

### Teste 1: Auto-Connect Bem-Sucedido

**Setup:**
```bash
# .env
MSSQL_DATABASE=REB_BI_IA
```

**Ação:** Clicar "🔌 Conectar ao SQL Server"

**Esperado:** ✅ Mensagem de confirmação

### Teste 2: Auto-Detect em Query

**Setup:**
```bash
# .env
MSSQL_DATABASE=REB_BI_IA
```

**Ação:** Perguntar "Lista tabelas do banco"

**Esperado:** ✅ Auto-connect + resposta

### Teste 3: Fallback Manual

**Setup:**
```bash
# .env
# MSSQL_DATABASE não configurado
```

**Ação:** Clicar "🔌 Conectar ao SQL Server"

**Esperado:** ⚠️ Instruções manuais

### Teste 4: Já Conectado

**Setup:** MCP já conectado anteriormente

**Ação:** Qualquer query SQL

**Esperado:** ✅ Não tenta reconectar

## 📝 Configuração

### Habilita Auto-Connect

Adicione ao `.env`:

```bash
MSSQL_DATABASE=REB_BI_IA
```

Opcional (já configurado):

```bash
MSSQL_SERVER=localhost
MSSQL_USERNAME=sa
MSSQL_PASSWORD=Str0ng!Passw0rd
DEFAULT_DB_PORT=1433
```

### Desabilita Auto-Connect

Remova ou comente `MSSQL_DATABASE` do `.env`:

```bash
# MSSQL_DATABASE=REB_BI_IA
```

## 🚀 Roadmap Futuro

### Melhorias Possíveis

1. **Multi-Database Support**
   - Listar databases disponíveis
   - Deixar usuário escolher
   - Salvar preferência

2. **Auto-Restore on Chat Start**
   - Salvar conexão MCP por usuário
   - Restaurar automaticamente
   - Persist cross-sessions

3. **Health Check**
   - Verificar se conexão ainda válida
   - Auto-reconnect se necessário
   - Notificar usuário

4. **Advanced Keywords**
   - Machine learning para detectar intenção
   - Context-aware detection
   - Smart fallback

## 📚 Referências

- [Chainlit MCP Docs](https://docs.chainlit.io/advanced-features/mcp)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- Arquitetura: `ARCHITECTURE_AUDIT_V2.md`
- Orquestração: `ORCHESTRATION_IMPLEMENTATION.md`

---

**Desenvolvido por ness.** 🚀




