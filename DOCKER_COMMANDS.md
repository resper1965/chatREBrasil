# 🐳 Comandos Docker - ness.

**Desenvolvido por:** ness.

---

## ⚠️ Importante: WSL Integration

Se Docker não está funcionando no WSL, configure no Docker Desktop:

1. Abra Docker Desktop
2. Settings > Resources > WSL Integration
3. Enable para sua distro (Ubuntu)
4. Apply & Restart
5. Teste: `docker version`

---

## 🚀 Build & Deploy

### Opção 1: PowerShell (Windows)

```powershell
# Navegar para o projeto
cd \\wsl.localhost\Ubuntu\home\resper\chatREBrasil

# Build
docker compose build --no-cache

# Deploy
docker compose up -d

# Status
docker compose ps

# Logs
docker compose logs -f app-agent
```

### Opção 2: Bash (WSL - após configurar Integration)

```bash
cd /home/resper/chatREBrasil

# Build automático
./build-and-deploy.sh

# Ou manual:
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose ps
```

### Opção 3: Docker Desktop GUI

1. Abra Docker Desktop
2. File > Open > Selecione pasta `chatREBrasil`
3. CLI no terminal integrado: execute comandos acima

---

## 📦 Comandos Úteis

### Build & Deploy

```bash
# Build completo (sem cache)
docker compose build --no-cache

# Build rápido (com cache)
docker compose build

# Iniciar em background
docker compose up -d

# Iniciar e ver logs
docker compose up

# Parar containers
docker compose down

# Parar e remover volumes
docker compose down -v
```

### Status & Logs

```bash
# Ver containers rodando
docker compose ps

# Logs em tempo real
docker compose logs -f

# Logs de um serviço específico
docker compose logs -f app-agent
docker compose logs -f db-persist
docker compose logs -f mssql

# Últimas 100 linhas
docker compose logs --tail=100 app-agent
```

### Debug

```bash
# Entrar no container
docker compose exec app-agent bash

# Ver processos
docker compose top

# Inspecionar configuração
docker compose config

# Ver uso de recursos
docker stats
```

---

## 🔄 Restart

```bash
# Restart um serviço
docker compose restart app-agent

# Restart todos
docker compose restart

# Rebuild e restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 🧹 Limpeza

```bash
# Parar e remover containers
docker compose down

# Remover volumes também (CUIDADO - apaga dados)
docker compose down -v

# Limpar imagens antigas
docker image prune -a

# Limpar tudo (CUIDADO)
docker system prune -a --volumes
```

---

## 🔍 Verificar

```bash
# Ver imagem criada
docker images | grep chatrebrasil

# Ver volumes
docker volume ls

# Ver networks
docker network ls

# Inspect container
docker inspect chatrebrasil-app-agent-1
```

---

## 📊 Portas

| Serviço | Porta Externa | Porta Interna |
|---------|---------------|---------------|
| app-agent | 8502 | 8000 |
| db-persist | 5435 | 5432 |
| mssql | 1433 | 1433 |

### Verificar portas em uso

```bash
# Windows PowerShell
netstat -ano | findstr 8502

# WSL/Linux
sudo lsof -i :8502
sudo ss -tlnp | grep 8502
```

---

## 🔧 Troubleshooting

### Erro: "Cannot connect to Docker daemon"

```bash
# Verificar se Docker Desktop está rodando
# Reiniciar WSL: wsl --shutdown no PowerShell
```

### Erro: "Port already in use"

```bash
# Alterar porta no docker-compose.yml
ports:
  - "8503:8000"  # Nova porta
```

### Erro: "Permission denied"

```bash
# Ajustar permissões WSL
sudo chown -R $USER:$USER data/

# Ou usar sudo (não recomendado)
sudo docker compose up -d
```

### Container não inicia

```bash
# Ver logs detalhados
docker compose logs app-agent

# Ver últimos eventos
docker events

# Verificar healthcheck
docker compose ps
```

### Rebuild limpo

```bash
# Remover tudo e rebuildar
docker compose down -v
docker system prune -a
docker compose build --no-cache
docker compose up -d
```

---

## 🎯 Quick Reference

```bash
# Tudo em um comando
cd /home/resper/chatREBrasil && \
docker compose down && \
docker compose build --no-cache && \
docker compose up -d && \
docker compose logs -f app-agent
```

---

**Versão:** 1.0  
**Data:** 2025-10-30  
**Desenvolvido por:** ness.





