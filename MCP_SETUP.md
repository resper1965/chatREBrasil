# 🔌 MCP SQL Server - Configuração e Uso

**Desenvolvido por ness.**

Sistema de acesso nativo a SQL Server via MCP (Model Context Protocol) no Chainlit.

---

## 📋 Visão Geral

Este MCP server permite que o Chainlit descubra e execute ferramentas SQL automaticamente através de uma interface padronizada, mantendo a flexibilidade para usar outras fontes de dados.

**✨ NOVIDADES v1.1:**
- Actions rápidas no welcome message para conectar MCP
- Instruções passo-a-passo integradas na UI
- Exemplos práticos de uso disponíveis via botões
- Credenciais dinâmicas via ferramentas (não hardcoded)
- Interface totalmente traduzida para português

---

## 🏗️ Arquitetura

```
Chainlit App (app/app.py)
├─ @cl.on_mcp_connect → Discovery automático
├─ @cl.step(type="tool") → Execução transparente
└─ Integração LLM ↔ MCP nativa
         ↓
MCP Server (mcp_sqlserver_stdio.py)
├─ Connect database → Descobre schema
├─ Get schema → Retorna metadados
├─ Execute query → SELECT seguro
├─ Analyze relationships → JOINs sugeridos
├─ Preview table → Primeiras linhas
└─ Search data → Busca em texto
         ↓
SQL Server (localhost:1433)
```

---

## 🔧 Configuração

### 1. Dependências

Já incluído no `requirements.txt`:
- `chainlit>=1.0.0`
- `openai>=1.12.0`
- `pyodbc>=5.0.0`
- `mcp>=1.19.0`

### 2. Handlers MCP

Os handlers nativos já estão implementados em `app/app.py`:

```python
@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    """Discovery automático de tools"""

@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session: ClientSession):
    """Cleanup automático"""

@cl.step(type="tool")
async def call_tool(tool_use):
    """Execução de tools"""
```

### 3. Config do Chainlit

O `config.toml` já está configurado:

```toml
[features.mcp]
enabled = true

[features.mcp.stdio]
enabled = true
allowed_executables = [ "python" ]
```

---

## 🚀 Como Usar

### Opção 1: Via Interface Chainlit (Recomendado)

1. Acesse http://localhost:8502
2. Faça login (admin / 123)
3. Na UI, clique em **"My MCPs"** ou **"Add MCP"**
4. Configure:
   - **Connection name:** `sql-server`
   - **Client type:** `stdio`
   - **Command:** `python mcp_sqlserver_stdio.py`
5. Clique em **"Connect"**

O Chainlit automaticamente:
- Descobrirá as 6 ferramentas disponíveis
- Permitirá que o LLM as use transparentemente
- Exibirá confirmação de conexão

### Opção 2: Conexão Automática (Futuro)

Configurar auto-connect no `.chainlit/config.toml` ou via environment variables.

---

## 🛠️ Ferramentas Disponíveis

### 1. `connect_database`
Conecta ao SQL Server e descobre schema automaticamente

**Parâmetros:**
- `server` (string, obrigatório): Endereço do servidor
- `database` (string, obrigatório): Nome da base
- `username` (string, obrigatório): Usuário SQL
- `password` (string, obrigatório): Senha
- `port` (integer, opcional): Porta (padrão: 1433)

**Retorna:**
```json
{
  "success": true,
  "message": "Conectado a localhost/master",
  "tables_discovered": 42
}
```

### 2. `get_database_schema`
Retorna metadados completos do banco

**Parâmetros:** Nenhum

**Retorna:**
```json
{
  "tables": [
    {
      "schema": "dbo",
      "name": "Properties",
      "full_name": "dbo.Properties",
      "columns": [...],
      "primary_keys": ["id"],
      "foreign_keys": [...],
      "approx_rows": 1500
    }
  ],
  "discovered_at": "2025-10-31T12:00:00"
}
```

### 3. `execute_query`
Executa query SELECT de forma segura

**Parâmetros:**
- `query` (string, obrigatório): Query SQL SELECT
- `limit` (integer, opcional): Limite de resultados (padrão: 100)

**Validações:**
- ✅ Apenas SELECT permitido
- ✅ Blacklist: DROP, DELETE, UPDATE, INSERT, EXEC, XP_CMDSHELL, SP_
- ✅ Timeout: 30s
- ✅ Limite padrão: 100 linhas

### 4. `analyze_relationships`
Analisa foreign keys e sugere JOINs

**Parâmetros:** Nenhum

**Retorna:**
```json
{
  "total_relationships": 15,
  "relationships": [
    {
      "from_table": "dbo.Properties",
      "from_column": "owner_id",
      "to_table": "dbo.Owners",
      "to_column": "id",
      "join_suggestion": "JOIN dbo.Owners ON dbo.Properties.owner_id = dbo.Owners.id"
    }
  ]
}
```

### 5. `preview_table`
Mostra primeiras linhas de uma tabela

**Parâmetros:**
- `table` (string, obrigatório): Nome completo (schema.table)
- `limit` (integer, opcional): Quantidade de linhas (padrão: 10)

### 6. `search_data`
Busca termo em colunas de texto

**Parâmetros:**
- `table` (string, obrigatório): Nome completo da tabela
- `search_term` (string, obrigatório): Termo a buscar
- `columns` (array, opcional): Colunas específicas

---

## 💬 Uso no Chat

Após conectar o MCP, você pode conversar naturalmente:

### Exemplos de Comandos

```
"Conecta ao banco localhost, base RealEstateDB, user sa, senha MinhaSenha"
→ Usa connect_database automaticamente

"Lista todas as tabelas"
→ Usa get_database_schema automaticamente

"Mostra as primeiras 10 linhas de Properties"
→ Usa preview_table automaticamente

"Busca por 'São Paulo' na tabela Properties"
→ Usa search_data automaticamente

"Qual o total de imóveis?"
→ LLM gera SELECT COUNT(*) e usa execute_query

"Analisa relacionamentos entre tabelas"
→ Usa analyze_relationships automaticamente
```

**O LLM escolhe a ferramenta correta automaticamente!**

---

## 🔒 Segurança

✅ **Implementado:**
- Apenas SELECT permitido
- Blacklist de comandos perigosos
- Timeout de 30s por operação
- Limite padrão de 100 linhas
- Validação de SQL injection básica

⚠️ **Recomendações:**
- Use usuário SQL com permissões read-only
- Configure firewall apropriadamente
- Monitore custos OpenAI
- Não exponha credenciais publicamente

---

## 🧪 Teste Manual do MCP Server

```bash
# No terminal
python mcp_sqlserver_stdio.py

# Ou via uvx (se disponível)
uvx run mcp_sqlserver_stdio.py
```

---

## 📁 Estrutura de Arquivos

```
chatREBrasil/
├── app/
│   └── app.py                    # Handlers MCP nativos
├── mcp_sqlserver_stdio.py        # MCP Server stdio
├── sql-agent-openai/
│   ├── mcp_sqlserver.py          # Implementação original (referência)
│   └── app_openai_mcp.py         # Exemplo de uso
├── requirements.txt               # mcp>=1.19.0 incluído
├── .chainlit/
│   └── config.toml               # MCP habilitado
└── MCP_SETUP.md                  # Este arquivo
```

---

## 🎯 Vantagens MCP Nativo

| Aspecto | MCP Nativo | Implementação Anterior |
|---------|------------|------------------------|
| Discovery | ✅ Automático | ❌ Manual (MCP_TOOLS estático) |
| Integração LLM | ✅ Transparente | ❌ Function calling manual |
| Sessões | ✅ Multi-connection | ❌ Single connection |
| Cleanup | ✅ Automático | ❌ Manual |
| Padrão | ✅ Oficial Chainlit | ⚠️ Customizado |

---

## 🐛 Troubleshooting

### "Connection refused"
Verifique se:
- SQL Server está rodando (localhost:1433)
- Credenciais estão corretas
- ODBC Driver 18 está instalado

### "MCP not discovered"
Verifique se:
- `python mcp_sqlserver_stdio.py` funciona standalone
- Permissões de execução estão corretas
- Python está no PATH

### "Tool execution failed"
Verifique se:
- Conexão MCP está ativa
- Database está acessível
- Query não viola validações de segurança

---

## 📚 Recursos

- [Chainlit MCP Docs](https://docs.chainlit.io/advanced-features/mcp)
- [MCP Protocol](https://modelcontextprotocol.io)
- [ODBC Driver 18](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

**Desenvolvido por ness.** 🚀

