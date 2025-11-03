# 🚀 Quick Deploy - Docker Desktop

## ⚡ Passos Rápidos

### 1. Iniciar Docker Desktop

- Abra o **Docker Desktop** no Windows
- Aguarde até aparecer o ícone na bandeja do sistema

### 2. Habilitar Integração WSL (se ainda não estiver)

1. Abra **Docker Desktop**
2. Clique em **Settings** ⚙️
3. Vá em **Resources** > **WSL Integration**
4. Habilite para sua distribuição WSL (Ubuntu)
5. Clique em **Apply & Restart**

### 3. Executar Build e Deploy

No terminal WSL, execute:

```bash
cd /home/resper/chatREBrasil
bash build-and-deploy.sh
```

**OU** execute os comandos manualmente:

```bash
cd /home/resper/chatREBrasil

# Parar containers existentes
docker compose down

# Build da imagem (primeira vez pode demorar ~5-10 minutos)
docker compose build --no-cache

# Iniciar containers
docker compose up -d

# Aguardar serviços iniciarem
sleep 30

# Verificar status
docker compose ps
```

### 4. Acessar Aplicação

Após o deploy:

- **URL**: http://localhost:8502
- **Login**: admin / 123

### 5. Ver Logs

```bash
docker compose logs -f app-agent
```

### 6. Parar Serviços

```bash
docker compose down
```

---

## 🔍 Verificação

Teste se Docker está funcionando:

```bash
docker version
docker compose version
```

Se funcionar, está tudo pronto! 🎉

---

**Desenvolvido por ness.** 🚀

