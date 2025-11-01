# 🚀 Quick Start - SQL Agent

**Desenvolvido por:** ness.

---

## ⚡ Início Rápido (5 minutos)

### 1. Setup

```bash
cd sql-agent-openai

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar
pip install -r requirements.txt
```

### 2. Configurar

```bash
# Editar .env com suas credenciais
nano .env

# Mínimo necessário:
OPENAI_API_KEY=sk-proj-SUA-CHAVE
MSSQL_DATABASE=nome_do_seu_banco
```

### 3. Executar

```bash
# Modo Chainlit (recomendado)
chainlit run app_openai_mcp.py -w

# OU modo terminal
python example_connection.py
```

### 4. Acessar

```
http://localhost:8000
```

---

## 🎯 Teste Rápido

### Conecte ao banco:
```
Conecta ao meu banco localhost, nome_do_banco, user sa, senha SuaSenha123
```

### Explore:
```
Lista todas as tabelas
```

### Analise:
```
Qual o total de registros?
```

---

## 📊 Portas Usadas

| Serviço | Porta | URL |
|---------|-------|-----|
| **Chainlit** | 8000 | http://localhost:8000 |
| **MSSQL** | 1433 | localhost:1433 |
| **Docker** | 8502 | http://localhost:8502 |

---

## ⚠️ Problemas?

### "ODBC Driver not found"
```bash
# Linux
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

### "OPENAI_API_KEY not found"
Verifique `.env` existe e tem a chave correta.

### "Login failed"
Verifique credenciais SQL Server no `.env`.

---

**Pronto para começar!** 🚀

Mais detalhes em **README.md**





