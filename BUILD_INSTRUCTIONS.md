# 🚀 Instruções de Build Garantido - chatREBrasil

## ⚠️ Problema Identificado

As alterações nos arquivos não estavam sendo aplicadas após o build porque:
1. ❌ JavaScript customizado não estava sendo carregado pelo Chainlit
2. ❌ Cache do Docker estava mantendo versão antiga
3. ❌ Faltava configuração no `config.toml` para carregar `custom.js`

---

## ✅ Solução Implementada

### 1. Configuração do Chainlit

**Arquivo:** `.chainlit/config.toml`

Adicionadas as seguintes linhas na seção `[UI]`:

```toml
[UI]
# Custom CSS path (relative to public directory)
custom_css = "/public/custom.css"

# Custom JavaScript path (relative to public directory)
custom_js = "/public/custom.js"
```

---

## 🔧 Como Usar o Build Garantido

### Script Automático (Recomendado)

```bash
cd /caminho/para/chatREBrasil
./build-garantido.sh
```

### Manual (Passo a Passo)

```bash
# 1. Parar containers
docker compose down

# 2. Remover imagem antiga
docker rmi chatrebrasil-app-agent:latest

# 3. Build sem cache (IMPORTANTE!)
docker compose build --no-cache app-agent

# 4. Iniciar containers
docker compose up -d

# 5. Aguardar e verificar logs
sleep 30
docker compose logs -f app-agent
```

---

## ✅ Checklist de Validação

### No Servidor
- [ ] Arquivos existem: `docker compose exec app-agent ls /app/public/custom.js`
- [ ] Config correto: `docker compose exec app-agent grep "custom_js" /app/.chainlit/config.toml`

### No Navegador
- [ ] Limpar cache (Ctrl+Shift+Del)
- [ ] Hard reload (Ctrl+Shift+R)
- [ ] Console mostra: "🤖 Gabi. - Custom JS loaded"
- [ ] Logo do Chainlit NÃO aparece no login
- [ ] UI "My MCPs" visível na sidebar

**Desenvolvido por:** ness.
