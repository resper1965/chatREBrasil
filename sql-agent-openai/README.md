# 🔍 Agente SQL Server com OpenAI GPT-4 + MCP

**Sistema conversacional para análise de dados SQL Server**

Desenvolvido com **GPT-4**, **Chainlit** e **Model Context Protocol (MCP)**.

---

## ✨ Funcionalidades Principais

### 📊 **Descoberta Automática de Schema**
- Descobre todas as tabelas do banco
- Extrai colunas com tipos, nullable, defaults
- Identifica Primary Keys e Foreign Keys
- Analisa relacionamentos entre tabelas
- Contagem aproximada de linhas por tabela

### 🔍 **Análise Inteligente**
- Queries SQL geradas automaticamente via GPT-4
- JOINs sugeridos baseados em FKs
- Busca semântica em dados textuais
- Preview rápido de tabelas

### 🔒 **Execução Segura**
- **Apenas SELECT permitido**
- Blacklist de comandos perigosos (DROP, DELETE, UPDATE, etc)
- Timeout de 30s por query
- Limite de 100 linhas por padrão
- Validação de SQL injection

### 💬 **Interface Conversacional**
- Conversa natural em **português**
- Function Calling automático
- Visualização formatada de resultados
- Step-by-step de execução de queries

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│              Usuário (Browser)                      │
│                  ↓                                  │
│         Chainlit - Interface Web                    │
│            (http://localhost:8000)                  │
│                  ↓                                  │
│         OpenAI GPT-4 Function Calling               │
│              (gpt-4o)                               │
│                  ↓                                  │
│         MCP Server - Descoberta de Schema           │
│          (mcp_sqlserver.py)                         │
│                  ↓                                  │
│         SQL Server - Banco de Dados                 │
│          (via pyodbc + ODBC Driver 18)              │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Instalação

### 1. Pré-requisitos

- **Python 3.11+**
- **ODBC Driver 18 for SQL Server**
  - Linux: `apt-get install msodbcsql18`
  - Docker: Já incluído no Dockerfile

### 2. Clonar e Configurar

```bash
# Criar diretório
mkdir sql-agent-openai && cd sql-agent-openai

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar .env

```bash
cp .env.example .env
nano .env  # ou vim, code, etc.
```

**Variáveis obrigatórias:**

```env
OPENAI_API_KEY=sk-proj-sua-chave-aqui
OPENAI_MODEL=gpt-4o

# MSSQL (opcional para auto-connect)
MSSQL_SERVER=localhost
MSSQL_DATABASE=your_database_name
MSSQL_USERNAME=sa
MSSQL_SA_PASSWORD=Str0ng!Passw0rd
DB_PORT=1433
```

---

## 📖 Uso

### Opção 1: Chainlit (Recomendado)

```bash
chainlit run app_openai_mcp.py -w
```

Acesse: **http://localhost:8000**

### Opção 2: Standalone (Terminal)

```bash
python example_connection.py
```

---

## 💬 Exemplos de Perguntas

### **Conexão**

```
"Conecta ao meu banco localhost, RealEstateDB, user sa, senha MyPass123"
```

### **Exploração**

```
"Lista todas as tabelas disponíveis"
```

```
"Descreve a tabela dbo.Properties"
```

```
"Quais são os relacionamentos entre as tabelas?"
```

### **Análise**

```
"Qual o total de propriedades?"
```

```
"Mostre as 10 propriedades mais caras"
```

```
"Qual a média de preço por tipo de imóvel?"
```

```
"Quantas propriedades temos em São Paulo?"
```

### **Busca**

```
"Busca por 'Apartamento' em todas as tabelas"
```

```
"Procura todas as propriedades com 'Jardim' no nome"
```

---

## ⚙️ Portas Configuradas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Chainlit | 8000 | Interface web |
| MSSQL | 1433 | SQL Server |
| PostgreSQL | 5435 | Chainlit persistence |

**Docker Compose:** Mapeia Chainlit para **8502**

---

## 🔧 Troubleshooting

### Erro: "ODBC Driver 18 not found"

**Solução:**
```bash
# Linux
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

### Erro: "Login failed for user"

**Verifique:**
- Credenciais corretas no `.env`
- SQL Server permitindo autenticação
- Firewall não bloqueando conexão

### Erro: "Your config file is outdated"

**Solução:**
```bash
# Remover config antigo e deixar Chainlit recriar
rm -rf .chainlit/config.toml
```

### Erro: "OPENAI_API_KEY not configured"

**Verifique:**
- Arquivo `.env` existe
- Variável `OPENAI_API_KEY` está configurada
- Não há espaços extras na chave

---

## 💰 Custos Estimados (OpenAI)

| Modelo | Input | Output | Custo/1M tokens |
|--------|-------|--------|-----------------|
| gpt-4o | $2.50 | $10.00 | Input: ~$0.0025/token |

**Exemplo:**
- Query simples: ~500 tokens → $0.00125
- 100 queries/dia: ~$0.12/dia
- 3000 queries/mês: ~$3.75/mês

---

## 🔐 Segurança e Limitações

### ✅ **Implementado**

- Apenas queries SELECT permitidas
- Blacklist de comandos perigosos
- Timeout de 30s
- Limite de 100 linhas
- Validação de SQL injection básica

### ⚠️ **Limitações**

- Não executa UPDATE/DELETE/INSERT
- Não cria/drop objetos
- Não executa stored procedures
- Limite de 100 linhas por query
- Timeout de 30s por operação

### 🚨 **Recomendações**

- Use usuário SQL com permissões **read-only**
- Configure firewall apropriadamente
- Monitore custos OpenAI
- Faça backup dos dados antes de análises extensivas
- Não exponha API keys publicamente

---

## 📁 Estrutura de Arquivos

```
sql-agent-openai/
│
├── mcp_sqlserver.py          # MCP Server - descoberta de schema
├── app_openai_mcp.py         # Chainlit App - interface web
├── example_connection.py     # Exemplo standalone terminal
├── requirements.txt          # Dependências
├── .env.example              # Template de configuração
├── .gitignore                # Git ignore
└── README.md                 # Esta documentação
```

---

## 🧪 Testes

### Teste 1: Conexão

```python
python -c "from mcp_sqlserver import SQLServerMCP; \
    mcp = SQLServerMCP(); \
    result = mcp.connect('localhost', 'master', 'sa', 'Str0ng!Passw0rd'); \
    print(result)"
```

### Teste 2: Chainlit

```bash
chainlit run app_openai_mcp.py
# Abrir browser em http://localhost:8000
# Digitar: "Lista tabelas"
```

### Teste 3: Standalone

```bash
python example_connection.py
# Digitar: "Qual o nome das tabelas disponíveis?"
```

---

## 🎯 Resultado Esperado

**Experiência do usuário:**

1. Abre **http://localhost:8000**
2. Vê mensagem de boas-vindas
3. Digita: "Conecta ao meu banco localhost, RealEstateDB, user sa"
4. Sistema conecta e descobre 25 tabelas automaticamente
5. Digita: "Qual o total de propriedades?"
6. GPT-4 gera: `SELECT COUNT(*) FROM dbo.Properties`
7. Executa e retorna: "150 propriedades"
8. Digita: "Mostre as 5 mais caras"
9. Sistema gera `SELECT TOP 5 ... ORDER BY price DESC`
10. Mostra tabela formatada

**Sem o usuário precisar escrever uma linha de SQL!** 🎉

---

## 📝 Notas

- **Português:** Todas as interações em PT-BR
- **Portas:** Chainlit 8000 (local), 8502 (Docker)
- **MCP:** Configurado mas usando Function Calling direto
- **Segurança:** Apenas SELECT, timeouts, validações

---

**Versão:** 1.0  
**Data:** 2025-10-30  
**Desenvolvido por:** ness.





