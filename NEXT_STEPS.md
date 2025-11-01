# 🚀 Próximos Passos - ness.

**Desenvolvido por:** ness.

---

## ⚙️ Configuração Docker Desktop

### 1. Habilitar WSL Integration

1. Abra **Docker Desktop**
2. Clique em **Settings** (ícone de engrenagem)
3. Vá em **Resources > WSL Integration**
4. Ative o toggle **"Enable integration with my default WSL distro"**
5. Ative especificamente para **Ubuntu**
6. Clique em **Apply & Restart**
7. Aguarde o restart do Docker Desktop

### 2. Verificar Instalação

Abra um terminal WSL e execute:

```bash
docker --version
docker compose version
```

Se funcionar, você verá:
```
Docker version 27.x.x
Docker Compose version v2.x.x
```

---

## 🏗️ Build & Deploy

### Opção A: Bash Script (Recomendado)

```bash
cd /home/resper/chatREBrasil
./build-and-deploy.sh
```

### Opção B: PowerShell

```powershell
cd \\wsl.localhost\Ubuntu\home\resper\chatREBrasil
.\BUILD_POWERSHELL.ps1
```

### Opção C: Manual

```bash
cd /home/resper/chatREBrasil

# Build
docker compose build --no-cache

# Deploy
docker compose up -d

# Ver logs
docker compose logs -f app-agent
```

---

## ✅ Verificar Instalação

Após o build, execute:

```bash
# Ver containers rodando
docker compose ps

# Verificar logs
docker compose logs app-agent | head -50

# Verificar se as portas estão abertas
# WSL:
sudo ss -tlnp | grep -E '8502|5435|1433'

# Windows PowerShell:
netstat -ano | findstr "8502 5435 1433"
```

---

## 🔗 Acessar Aplicação

1. Abra o navegador
2. Acesse: **http://localhost:8502**
3. Login:
   - **Usuário:** `admin`
   - **Senha:** `123` ⚠️ (altere no `.env` para produção!)

---

## 🧪 Testar Funcionalidades

### 1. Interface

- ✅ Verifique logo ness. (tema escuro/claro)
- ✅ Verifique favicon na aba do navegador
- ✅ Navegue pela interface

### 2. Autenticação

- ✅ Faça logout e login novamente
- ✅ Teste com credenciais incorretas

### 3. Chat Persistência

- ✅ Inicie uma conversa
- ✅ Feche o navegador
- ✅ Reabra e verifique histórico

### 4. Multi-Agente

- ✅ Faça perguntas financeiras
- ✅ Solicite análises de dados
- ✅ Teste function calling

---

## 🔧 Troubleshooting

### Docker não funciona no WSL

**Sintoma:** `docker: command not found`

**Solução:**
1. Verifique WSL Integration no Docker Desktop
2. Reinicie WSL: `wsl --shutdown` (PowerShell) e reabra terminal
3. Reinicie Docker Desktop

### Porta 8502 já em uso

**Sintoma:** `port is already allocated`

**Solução:**
```bash
# Ver o que está usando a porta
sudo lsof -i :8502

# Ou alterar porta no docker-compose.yml
ports:
  - "8503:8000"
```

### Containers não iniciam

**Sintoma:** Containers param imediatamente

**Solução:**
```bash
# Ver logs detalhados
docker compose logs app-agent
docker compose logs db-persist

# Verificar se banco subiu
docker compose ps
```

### Erro de permissão

**Sintoma:** `Permission denied`

**Solução:**
```bash
# Ajustar permissões
sudo chown -R $USER:$USER data/
sudo chmod -R 755 data/
```

---

## 📚 Documentação

| Arquivo | Descrição |
|---------|-----------|
| `BUILD_INSTRUCTIONS.md` | Guia de build e configuração |
| `DOCKER_COMMANDS.md` | Comandos Docker úteis |
| `README.md` | Documentação principal |
| `DOCKER_COMMANDS.md` | Comandos Docker |

---

## 🎯 Checklist Final

- [ ] Docker Desktop instalado e rodando
- [ ] WSL Integration habilitada
- [ ] `docker --version` funciona
- [ ] Build executado com sucesso
- [ ] Containers rodando (`docker compose ps`)
- [ ] Aplicação acessível em http://localhost:8502
- [ ] Login funciona
- [ ] Logo ness. visível (dark/light)
- [ ] Favicon aparecendo
- [ ] Chat persistência testada

---

## 🔐 Segurança (Produção)

Antes de deployar em produção:

1. **Altere senha do admin** no `.env`:
   ```bash
   ADMIN_PASSWORD=suasenhasegura123
   ```

2. **Gere novo AUTH_SECRET**:
   ```bash
   openssl rand -base64 32
   ```
   Adicione no `.env`:
   ```bash
   CHAINLIT_AUTH_SECRET=<novo_secret>
   ```

3. **Configure HTTPS** (reverse proxy com nginx/traefik)

4. **Backup regular**:
   ```bash
   docker compose exec db-persist pg_dump -U chainlit chainlit > backup.sql
   ```

---

## 📞 Suporte

- 📖 Documentação: Ver arquivos `.md` no projeto
- 🐳 Docker: Ver `DOCKER_COMMANDS.md`
- 🔧 Troubleshooting: Ver `NEXT_STEPS.md` (este arquivo)

---

**Versão:** 1.0  
**Data:** 2025-10-30  
**Desenvolvido por:** ness.





