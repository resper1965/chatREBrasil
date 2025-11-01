# 🚀 Deploy SQL Agent

**Desenvolvido por:** ness.

---

## ⚡ Quick Start

### Opção 1: Local com venv (Já pronto!)

```bash
cd sql-agent-openai

# venv já criado e dependências instaladas
source venv/bin/activate

# Executar
chainlit run app_openai_mcp.py -w
```

Acesse: **http://localhost:8000**

### Opção 2: Docker (Recomendado para produção)

#### Criar Dockerfile

```dockerfile
FROM python:3.11-slim

# Instalar ODBC Driver
RUN apt-get update && apt-get install -y \
    curl apt-transport-https gnupg2 unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && sed -i "s|deb https://packages.microsoft.com|deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com|" /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["chainlit", "run", "app_openai_mcp.py", "--host", "0.0.0.0", "--port", "8000"]
```

#### Criar docker-compose.yml

```yaml
version: "3.9"

services:
  sql-agent:
    build:
      context: .
      dockerfile: Dockerfile
    env_file: .env
    ports:
      - "8503:8000"  # Porta diferente do projeto principal
    restart: unless-stopped
    volumes:
      - ./:/app
```

#### Build e Deploy

```bash
docker compose build
docker compose up -d
```

Acesse: **http://localhost:8503**

---

## 🔧 Configuração .env

Edite `.env` com suas credenciais:

```bash
# OpenAI (obrigatório)
OPENAI_API_KEY=sk-proj-sua-chave
OPENAI_MODEL=gpt-4o

# MSSQL (opcional - auto-connect)
MSSQL_SERVER=localhost
MSSQL_DATABASE=your_database_name
MSSQL_USERNAME=sa
MSSQL_SA_PASSWORD=Str0ng!Passw0rd
DB_PORT=1433
```

---

## 📊 Portas

| Serviço | Porta | URL |
|---------|-------|-----|
| **SQL Agent (local)** | 8000 | http://localhost:8000 |
| **SQL Agent (Docker)** | 8503 | http://localhost:8503 |
| **Projeto Principal** | 8502 | http://localhost:8502 |
| **MSSQL** | 1433 | localhost:1433 |

---

## ⚠️ Troubleshooting

### "ODBC Driver not found" (Local)

**WSL/Linux:**
```bash
# Instalar ODBC Driver 18
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/debian/12/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

**Ou use Docker** (já tem driver instalado)

### "OPENAI_API_KEY not found"

Verifique `.env` existe e tem a chave correta.

### "Login failed"

Verifique credenciais MSSQL no `.env`.

---

## ✅ Checklist

- [ ] `.env` configurado
- [ ] `OPENAI_API_KEY` válida
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] ODBC Driver instalado (ou usar Docker)
- [ ] Container rodando (se Docker)
- [ ] Acesso a http://localhost:8000 funcionando

---

**Pronto para usar!** 🚀

Mais detalhes: **README.md**





