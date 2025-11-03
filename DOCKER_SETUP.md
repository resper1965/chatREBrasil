# 🐳 Configuração Docker Desktop para WSL

## Pré-requisitos

Para fazer build e deploy no Docker Desktop através do WSL, você precisa:

### 1. Iniciar o Docker Desktop

1. Abra o **Docker Desktop** no Windows
2. Aguarde até que o ícone do Docker apareça na bandeja do sistema (indicando que está rodando)

### 2. Habilitar Integração WSL

1. Abra o **Docker Desktop**
2. Vá em **Settings** (Configurações)
3. Clique em **Resources** > **WSL Integration**
4. Habilite a integração para sua distribuição WSL (Ubuntu)
5. Clique em **Apply & Restart**

### 3. Verificar Instalação

No terminal WSL, execute:

```bash
docker version
docker compose version
```

Se os comandos funcionarem, a integração está configurada corretamente!

## Build e Deploy

### Opção 1: Script Bash (WSL)

```bash
cd /home/resper/chatREBrasil
bash build-and-deploy.sh
```

### Opção 2: Script PowerShell (Windows)

1. Abra o **PowerShell** como Administrador
2. Execute:

```powershell
cd "\\wsl.localhost\Ubuntu\home\resper\chatREBrasil"
.\BUILD_POWERSHELL.ps1
```

### Opção 3: Comandos Manuais

```bash
# Parar containers existentes
docker compose down

# Build da imagem (pode demorar alguns minutos)
docker compose build --no-cache

# Iniciar containers
docker compose up -d

# Verificar status
docker compose ps

# Ver logs
docker compose logs -f app-agent
```

## Acesso

Após o deploy bem-sucedido:

- **URL**: http://localhost:8502
- **Login**: admin / 123

## Troubleshooting

### Erro: "Docker não encontrado no WSL"

**Solução**: 
1. Certifique-se de que o Docker Desktop está rodando no Windows
2. Habilite a integração WSL nas configurações do Docker Desktop
3. Reinicie o terminal WSL

### Erro: "Cannot connect to Docker daemon"

**Solução**:
1. Verifique se o Docker Desktop está rodando
2. Reinicie o Docker Desktop
3. Verifique se a integração WSL está habilitada

### Erro: "Port already in use"

**Solução**:
Pare os containers existentes:

```bash
docker compose down
```

Ou altere a porta no `docker-compose.yml` se necessário.

## Parar Serviços

```bash
docker compose down
```

Para remover também os volumes:

```bash
docker compose down -v
```

---

**Desenvolvido por ness.** 🚀

