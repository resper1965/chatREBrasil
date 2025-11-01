# 🔌 Configuração MSSQL - ness.

**Desenvolvido por:** ness.

---

## 📊 Como o Chat Conecta ao MSSQL

### 🔍 Entendendo o Fluxo

O chat **não conhece a estrutura do banco automaticamente**. Ele funciona em **modo dinâmico**:

1. **Primeiro**: Você fornece credenciais de conexão
2. **Depois**: O agente explora o banco usando ferramentas SQL
3. **Por fim**: O agente aprende a estrutura executando queries

---

## 🎯 Duas Formas de Configurar

### ✅ Opção 1: Auto-Connect via .env (RECOMENDADO)

Configure as credenciais no `.env`:

```bash
# MSSQL Auto-Connection
MSSQL_SERVER=localhost           # ou IP do servidor
MSSQL_DATABASE=your_database_name
MSSQL_USERNAME=sa
MSSQL_SA_PASSWORD=Str0ng!Passw0rd
DB_PORT=1433
```

**Vantagem:** Conexão automática ao iniciar o chat.

**Como funciona:**
- Ao abrir o chat, sistema tenta conectar automaticamente
- Se sucesso: ✅ mostra no welcome
- Se falha: ⚠️ mostra erro
- Se não configurado: 💡 mostra mensagem informativa

### 📝 Opção 2: Manual via Chat

Forneça credenciais diretamente no chat:

```
Conecta ao servidor 192.168.1.100, base RealEstateDB, 
user admin, senha MySecret123
```

**Vantagem:** Flexível para múltiplos bancos.

---

## 🔧 Configuração Passo a Passo

### 1. Editar .env

```bash
cd /home/resper/chatREBrasil
nano .env  # ou vim, code, etc.
```

Adicione:

```bash
# MSSQL Auto-Connection
MSSQL_SERVER=seu_servidor
MSSQL_DATABASE=nome_do_banco
MSSQL_USERNAME=seu_usuario
MSSQL_SA_PASSWORD=sua_senha
DB_PORT=1433
```

### 2. Reiniciar Container

```bash
docker compose restart app-agent
```

Ou se não está em Docker:

```bash
# Parar processo atual (Ctrl+C)
# Reiniciar
chainlit run app/app.py -w
```

### 3. Verificar Conexão

Abra o chat e veja mensagem de boas-vindas:

- ✅ **"Conectado automaticamente: localhost/RealEstateDB"** → Sucesso
- ⚠️ **"Auto-conexão MSSQL falhou: ..."** → Erro (verificar credenciais)
- 💡 **"Configure MSSQL_DATABASE no .env"** → Não configurado

---

## 🧩 Como o Agente Descobre a Estrutura

### Exploração Automática

O agente usa ferramentas SQL para mapear o banco:

#### 1. **list_tables**
```sql
SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
```
**Resultado:** Lista de tabelas disponíveis

#### 2. **describe_table**
```sql
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Imoveis'
ORDER BY ORDINAL_POSITION
```
**Resultado:** Estrutura da tabela

#### 3. **execute_query**
```sql
SELECT TOP 10 * FROM Imoveis WHERE cidade = 'São Paulo'
```
**Resultado:** Dados da tabela

### Exemplo de Diálogo

```
Você: "Mostre imóveis em SP"

Sistema (internamente):
1. Analisa pergunta
2. Identifica necessidade de SQL
3. Verifica conexão ativa
4. Executa: list_tables() 
   → ["Imoveis", "Clientes", "Vendas"]
5. Executa: describe_table("Imoveis")
   → [{"name": "cidade", "type": "varchar"}, ...]
6. Executa: SELECT * FROM Imoveis WHERE cidade LIKE '%SP%'
7. Retorna resultados formatados
```

---

## 🔐 Segurança

### Recomendações

1. **Produção**: Nunca exponha credenciais no código
2. **Desenvolvimento**: Use `.env` (ignorado no git)
3. **Containers**: Use secrets do Docker em produção
4. **Usuário**: Considere criar user SQL dedicado

### Exemplo .env Seguro

```bash
# Desenvolvimento
MSSQL_SERVER=localhost
MSSQL_DATABASE=dev_db
MSSQL_USERNAME=dev_user
MSSQL_SA_PASSWORD=dev_password

# Produção (usar secrets Docker)
# MSSQL_SERVER=${MSSQL_SERVER_SECRET}
# MSSQL_DATABASE=${MSSQL_DB_SECRET}
```

---

## 🧪 Testando a Conexão

### Teste 1: Conexão Automática

1. Configure `.env`
2. Inicie o chat
3. Verifique mensagem de welcome

### Teste 2: Conexão Manual

```
Você: "Conecta ao servidor localhost, 
      base TestDB, user sa, senha Test123"

Sistema: "✅ Conectado à base TestDB no servidor localhost"
```

### Teste 3: Exploração

```
Você: "Lista todas as tabelas"

Sistema: [Lista tabelas com list_tables]

Você: "Descreve a tabela Imoveis"

Sistema: [Lista colunas com describe_table]

Você: "Mostra 10 imóveis"

Sistema: [Executa SELECT e retorna dados]
```

---

## ⚙️ Docker Compose

Se usando containers separados:

```yaml
services:
  mssql:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - MSSQL_SA_PASSWORD=${MSSQL_SA_PASSWORD:-Str0ng!Passw0rd}
    ports:
      - "1433:1433"
```

Configuração em `.env`:

```bash
# Se MSSQL no mesmo host
MSSQL_SERVER=localhost

# Se MSSQL em container Docker
MSSQL_SERVER=mssql  # nome do serviço
```

---

## 🔍 Troubleshooting

### Erro: "Nenhuma conexão ativa"

**Causa:** Não conectou ao banco.

**Solução:**
- Configure auto-connect no `.env`
- Ou conecte manualmente via chat

### Erro: "Login failed for user"

**Causa:** Credenciais incorretas.

**Solução:**
- Verifique `.env`
- Teste conexão manual
- Confirme senha do SQL Server

### Erro: "Cannot open database"

**Causa:** Banco não existe ou user sem permissão.

**Solução:**
- Verifique nome do banco
- Conceda permissões ao user
- Confirme que banco está rodando

### ODBC Driver 18 not found

**Causa:** Driver não instalado no container.

**Solução:**
- Já resolvido no Dockerfile
- Se local, instale: `apt-get install msodbcsql18`

---

## 📚 Referências

- **ODBC Driver**: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- **PyODBC**: https://github.com/mkleehammer/pyodbc
- **Chainlit MCP**: https://docs.chainlit.io/integrations/mcp

---

## ✅ Checklist

- [ ] `.env` configurado com credenciais MSSQL
- [ ] Container reiniciado (se Docker)
- [ ] Mensagem "✅ Conectado automaticamente" no chat
- [ ] Teste: "Lista tabelas" funciona
- [ ] Teste: "Descreve tabela X" funciona
- [ ] Teste: "SELECT * FROM ..." funciona

---

**Versão:** 1.0  
**Data:** 2025-10-30  
**Desenvolvido por:** ness.





