# 📊 Status do MCP no Chat

**Desenvolvido por:** ness.

---

## ⚠️ MCP vs Function Calling

### O que está implementado
A aplicação **usa OpenAI Function Calling**, não MCP (Model Context Protocol).

### Diferenças

| Aspecto | MCP (Chainlit) | Function Calling (OpenAI) |
|---------|-----------------|---------------------------|
| **Protocolo** | Model Context Protocol | OpenAI Function Calling |
| **Integração** | Chainlit UI | API OpenAI direta |
| **Interface** | Seletor MCP na UI | Automático via API |
| **Status** | 🟡 Configurado mas não usado | ✅ Ativo e funcionando |

---

## 🔍 Como funciona atualmente

### 1. Definição de Ferramentas SQL

As ferramentas SQL são definidas em `app/app.py`:

```python
SQL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "connect_database",
            "description": "Conecta a uma base de dados MS SQL Server",
            "parameters": {
                "type": "object",
                "properties": {
                    "server": {"type": "string"},
                    "database": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_query",
            "description": "Executa query SQL SELECT",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    # ... mais ferramentas
]
```

### 2. Agente Coordenador

O **Coordenador** decide qual agente usar:
- **Analista de Dados** → Ferramentas SQL
- **Especialista Financeiro** → Ferramentas Financeiras

### 3. Processo de Tool Calling

```
Usuário pergunta
    ↓
Coordenador identifica necessidade de SQL
    ↓
Delega para Analista de Dados
    ↓
OpenAI decide chamar ferramentas:
    1. connect_database()
    2. execute_query()
    ↓
Função execute_sql_tool() executa:
    - Conecta via pyodbc
    - Executa query
    - Retorna resultados
    ↓
Resposta formatada para o usuário
```

### 4. Execução de Ferramentas

**Função:** `execute_sql_tool()`

```python
def execute_sql_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Executa ferramentas SQL"""
    session_id = cl.user_session.get("id", "default")
    
    # Armazena conexões por sessão
    if tool_name == "connect_database":
        # Conecta via pyodbc usando ODBC Driver 18
        conn = pyodbc.connect(conn_str, timeout=10)
        connections_store[session_id]["connections"]["main"] = conn
    
    elif tool_name == "execute_query":
        # Executa query SELECT
        cursor.execute(query)
        rows = cursor.fetchmany(limit)
        return json.dumps(results, indent=2)
    
    # ... mais ferramentas
```

### 5. Integração pyodbc

```python
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server},{port};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str, timeout=10)
```

---

## 🎯 Por que MCP não está sendo usado

### Configuração Chainlit

O `config.toml` tem MCP habilitado:

```toml
[features.mcp]
enabled = true

[features.mcp.sse]
enabled = true

[features.mcp.stdio]
enabled = true
allowed_executables = [ "npx", "uvx" ]
```

### Razão

**A aplicação não usa MCP porque:**

1. ✅ OpenAI Function Calling já funciona perfeitamente
2. ✅ Implementação já está completa e testada
3. ✅ Não precisa de configuração adicional
4. ⚠️ MCP seria redundante neste caso

### Quando MCP seria útil

- Integração com ferramentas externas via MCP servers
- Ferramentas customizadas no Chainlit UI
- Extensibilidade para plugins MCP

---

## 📝 Resumo

| Componente | Tecnologia | Status |
|------------|------------|--------|
| **Tool Calling** | OpenAI Function Calling | ✅ Ativo |
| **Conexão SQL** | pyodbc + ODBC Driver 18 | ✅ Funcionando |
| **Agentes** | Multi-agent com Coordenador | ✅ Implementado |
| **MCP** | Model Context Protocol | 🟡 Configurado |
| **UI Seletor MCP** | Chainlit MCP UI | ❌ Não usado |

---

## 🔧 Como habilitar MCP (opcional)

Se quiser usar MCP além do Function Calling:

1. **Configurar MCP Server**
2. **Expor ferramentas MCP no Chainlit**
3. **Mapear ferramentas para MCP tools**

**Nota:** Não é necessário para o funcionamento atual.

---

## ✅ Conclusão

**O chat consegue questionar MSSQL através de:**

1. ✅ **OpenAI Function Calling**
2. ✅ **pyodbc para conexão SQL**
3. ✅ **Multi-agent com Analista de Dados**
4. ✅ **Ferramentas SQL automáticas**
5. 🟡 **MCP configurado mas não utilizado**

**A aplicação está funcionando corretamente sem MCP!**

---

**Versão:** 1.0  
**Data:** 2025-10-30  
**Desenvolvido por:** ness.
