# 🔧 Correção: Conexão MCP SQL Server

## ⚠️ Problema

Quando você usa `localhost` para conectar ao SQL Server via MCP, dá erro de timeout porque `localhost` dentro do container aponta para o próprio container, não para o container do MSSQL.

## ✅ Solução

**Use o hostname do container Docker:** `mssql`

### Frase Correta para Conectar:

```
Conectar SQL Server mssql, base REB_BI_IA, user sa, senha Str0ng!Passw0rd, porta 1433
```

**Note:** `localhost` → `mssql` (nome do serviço no docker-compose.yml)

## 📊 Detalhes Técnicos

### Docker Network

```
app-agent:  172.19.0.4/16  (container da aplicação)
mssql:      172.19.0.2/16  (container do SQL Server)
```

### Por que `mssql` funciona?

O Docker Compose cria uma rede interna onde cada serviço é acessível pelo nome definido em `docker-compose.yml`. O nome `mssql` é resolvido automaticamente para o IP correto na rede interna.

### Exemplo de Conexão

```python
# ❌ ERRADO (timeout)
SERVER=localhost

# ✅ CORRETO
SERVER=mssql
```

## 🎯 Como Usar

1. **Na barra lateral:** "My MCPs" → "Connect" (se já não estiver)

2. **No chat, digite:**
   ```
   Conectar SQL Server mssql, base REB_BI_IA, user sa, senha Str0ng!Passw0rd, porta 1433
   ```

3. **Pronto!** ✅

## 💡 Alternativa: Configurar Auto-Connect

Se quiser que sempre use `mssql` automaticamente, atualize o `.env`:

```bash
MSSQL_SERVER=mssql
MSSQL_DATABASE=REB_BI_IA
```

Depois faça rebuild e a conexão será automática!

---

**Desenvolvido por ness.** 🚀




