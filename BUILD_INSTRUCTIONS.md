# 🚀 Instruções de Build - ness.

**Desenvolvido por:** ness.

---

## 📦 Docker Desktop

Execute os seguintes comandos no terminal onde o Docker Desktop está rodando:

### Build Completo

```bash
cd /home/resper/chatREBrasil
docker compose build
```

### Build e Iniciar

```bash
docker compose up -d
```

### Ver Logs

```bash
docker compose logs -f app-agent
```

### Parar Containers

```bash
docker compose down
```

---

## ✅ Arquivos Prontos

### Docker Compose
- ✅ `docker-compose.yml` - 3 serviços (app, PostgreSQL, MSSQL)
- ✅ `Dockerfile` - Python 3.11 + ODBC 18 + PostgreSQL
- ✅ `.env` - Configurações (OPENAI_API_KEY, CHAINLIT_AUTH_SECRET, etc.)

### Aplicação
- ✅ `app/app.py` (846 linhas) - Sistema multi-agente
- ✅ `requirements.txt` - Dependências Python
- ✅ `.chainlit/config.toml` - Configuração UI + favicon

### Assets Visuais
- ✅ `public/logo-dark.png` - Logo ness. (tema escuro)
- ✅ `public/logo-light.png` - Logo ness. (tema claro)
- ✅ `public/favicon.png` - Favicon Gabi
- ✅ `public/icon.png` - Ícone sistema
- ✅ `public/favicon.js` - Injection script
- ✅ `public/theme-logos.css` - CSS dual-theme

### Dados
- ✅ `data/` - Volumes para persistência
- ✅ `.backup/` - Backup completo (7.7 GB)

---

## 🎯 Serviços Configurados

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **app-agent** | 8502 | Chainlit UI + Multi-Agent System |
| **db-persist** | 5435 | PostgreSQL (chat history) |
| **mssql** | 1433 | MS SQL Server (dados cliente) |

---

## 🔧 Variáveis de Ambiente

Edite `.env` antes do build:

```bash
# API OpenAI
OPENAI_API_KEY=sk-proj-...

# Autenticação
CHAINLIT_AUTH_SECRET=eloeQ8g1ZQD1VORODmJtHnTUTWlWSnGzB1jJg670XZA
ADMIN_USERNAME=admin
ADMIN_PASSWORD=123

# Database
CHAINLIT_DATABASE_URL=postgresql://chainlit:chainlit@db-persist:5432/chainlit

# MSSQL
MSSQL_SA_PASSWORD=Str0ng!Passw0rd
```

---

## 🚀 Deploy

### Opção 1: Docker Compose (Recomendado)

```bash
docker compose up -d
```

**Acesse:** http://localhost:8502  
**Login:** admin / 123

### Opção 2: Local (venv)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chainlit run app/app.py -w
```

**Acesse:** http://localhost:8000

---

## 📊 Recursos Implementados

✅ **Chainlit 2.8.4** - UI moderna  
✅ **Autenticação** - Password auth  
✅ **Persistência** - PostgreSQL + @on_chat_resume  
✅ **OpenAI GPT-4** - Function calling  
✅ **Multi-Agente** - Financeiro + Dados  
✅ **SQL Server** - Conexão dinâmica  
✅ **Assets ness.** - Logos dual-theme, favicon, icon  
✅ **MCP** - Configurado  
✅ **Logging** - Completo  

---

## 🐛 Troubleshooting

### Erro: "Cannot connect to Docker daemon"

```bash
# Verificar se Docker Desktop está rodando
# Iniciar Docker Desktop
```

### Erro: "Port 8502 already in use"

```bash
# Alterar porta no docker-compose.yml
ports:
  - "8503:8000"  # Nova porta
```

### Erro: "Permission denied"

```bash
# WSL: Ajustar permissões
sudo chown -R $USER:$USER data/
```

---

## 📝 Build Manual (Teste)

Se Docker não disponível, teste localmente:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/app.py
```

---

**Versão:** 1.0  
**Data:** 2025-10-30  
**Desenvolvido por:** ness.

