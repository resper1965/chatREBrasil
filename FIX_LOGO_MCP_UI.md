# Fix: Logo de Login e UI do MCP

## Data: 2025-11-05
## Branch: claude/fix-mcp-connect-tool-011CUqRwKWfz2PbA7XP62kfC

---

## 🐛 Problemas Identificados

### 1. Logo do Chainlit ainda aparecia na tela de login
**Problema:** CSS muito agressivo estava bloqueando TODAS as imagens, incluindo funcionais

**Causa:** Seletores CSS globais como:
```css
.MuiDialog-root img,
.MuiModal-root img,
form img
```

### 2. UI "My MCPs" não aparecia na sidebar
**Problema:** Servidores MCP pré-configurados impediam a UI de adição manual

**Causa:** Seção `[mcp.servers]` no config.toml configurava servidores automaticamente

---

## ✅ Soluções Implementadas

### 1. CSS Seletivo para Remoção de Logos

**Arquivo:** `public/custom.css`

**Estratégia:** Mudar de modo AGRESSIVO para modo SELETIVO

**Antes (problemático):**
```css
/* Bloqueava TODAS as imagens */
.MuiDialog-root img,
.MuiModal-root img,
form img {
    display: none !important;
}
```

**Depois (seletivo):**
```css
/* Bloqueia APENAS logos do Chainlit */
form > div:first-child img,
img[alt="Chainlit logo"],
img[alt="chainlit logo"],
.MuiBox-root > img[alt*="logo"]:first-child
```

**Resultado:**
- ✅ Remove logo do Chainlit na tela de login
- ✅ Mantém ícones funcionais (MCP, etc.)
- ✅ Não afeta elementos da UI

---

### 2. JavaScript para Remoção Dinâmica

**Arquivo:** `public/custom.js` (NOVO)

**Funcionalidades:**

1. **Remoção dinâmica do logo de login:**
```javascript
function removeChailitLoginLogo() {
    const selectors = [
        'img[alt*="Chainlit"]',
        'img[alt*="chainlit"]',
        'form img[src*="logo"]'
    ];
    // Remove apenas se src/alt contém "chainlit"
}
```

2. **Observer de mutações:**
```javascript
const observer = new MutationObserver(function(mutations) {
    // Remove logos quando DOM é modificado
    removeChailitLoginLogo();
});
```

3. **Proteção de elementos MCP:**
```javascript
const mcpObserver = new MutationObserver(function(mutations) {
    // Garante que elementos [data-mcp] permaneçam visíveis
});
```

**Resultado:**
- ✅ Remoção automática de logos ao carregar
- ✅ Remoção automática quando login é recarregado
- ✅ Proteção de elementos funcionais MCP

---

### 3. UI "My MCPs" Habilitada

**Arquivo:** `.chainlit/config.toml`

**Mudanças:**

1. **Sidebar aberta por padrão:**
```toml
# Antes:
# default_sidebar_state = "open"

# Depois:
default_sidebar_state = "open"  # Sidebar aberta para mostrar MCP UI
```

2. **Servidores pré-configurados comentados:**
```toml
# Antes:
[mcp]

[mcp.servers.mssql]
command = "python"
args = ["/app/mcp_sqlserver_stdio.py"]

# Depois:
# [mcp]
#
# [mcp.servers.mssql]
# command = "python"
# args = ["/app/mcp_sqlserver_stdio.py"]
```

**Motivo:**
- Servidores pré-configurados impedem UI "My MCPs" de aparecer
- Usuário deve adicionar MCPs manualmente via interface
- Permite visualizar e gerenciar conexões MCP

**Resultado:**
- ✅ Sidebar aberta ao iniciar
- ✅ Botão "My MCPs" visível na sidebar
- ✅ Usuário pode adicionar servidores MCP manualmente

---

## 📁 Arquivos Modificados

1. **`public/custom.css`**
   - CSS seletivo ao invés de agressivo
   - Seletores específicos para logo de login

2. **`public/custom.js`** (NOVO)
   - JavaScript para remoção dinâmica de logos
   - Observer de mutações DOM
   - Proteção de elementos MCP

3. **`.chainlit/config.toml`**
   - Sidebar aberta por padrão
   - Servidores MCP pré-configurados comentados

---

## 🧪 Como Testar

### 1. Testar Remoção de Logo

```bash
# Rebuild e restart
docker-compose build app-agent
docker-compose up -d app-agent

# 1. Fazer logout
# 2. Limpar cache do navegador (Ctrl+Shift+Del)
# 3. Recarregar página (Ctrl+Shift+R)
# 4. Verificar tela de login:
#    - ❌ Nenhum logo do Chainlit visível
#    - ✅ Formulário de login funcional
```

### 2. Testar UI do MCP

```bash
# 1. Fazer login
# 2. Verificar sidebar (deve estar aberta)
# 3. Procurar por seção "My MCPs" ou "MCP"
# 4. Deve haver botão "+" ou "Add MCP"
# 5. Clicar e adicionar servidor MCP manualmente:

Connection name: mssql
Client type: stdio
Command: python
Arguments: /app/mcp_sqlserver_stdio.py

Connection name: postgres
Client type: stdio
Command: python
Arguments: /app/mcp_postgres_stdio.py
```

### 3. Verificar JavaScript Carregado

```bash
# Abrir DevTools (F12)
# Console deve mostrar:
🤖 Gabi. - Custom JS loaded
✅ Gabi. - Logo removal active
🚀 Gabi. by ness. - Custom branding loaded
```

---

## 🔧 Configuração Manual vs Automática

### Opção A: Usuário Adiciona Manualmente (Atual)

**Vantagens:**
- ✅ UI "My MCPs" visível na sidebar
- ✅ Usuário controla quais servidores conectar
- ✅ Gerenciamento visual de conexões

**Como usar:**
1. Clicar em "My MCPs" na sidebar
2. Clicar em "+" ou "Add MCP"
3. Preencher form com comando e argumentos
4. Conectar

### Opção B: Servidores Pré-Configurados (Desabilitado)

**Vantagens:**
- ✅ Servidores conectam automaticamente ao iniciar
- ✅ Zero configuração manual necessária

**Como habilitar:**
Descomentar no `.chainlit/config.toml`:
```toml
[mcp]

[mcp.servers.mssql]
command = "python"
args = ["/app/mcp_sqlserver_stdio.py"]
env = {}

[mcp.servers.postgres]
command = "python"
args = ["/app/mcp_postgres_stdio.py"]
env = {}
```

**Nota:** Quando habilitado, UI "My MCPs" pode não aparecer.

---

## 📚 Referências Técnicas

### Seletores CSS Utilizados

| Seletor | Propósito |
|---------|-----------|
| `form > div:first-child img` | Logo no topo do formulário de login |
| `img[alt="Chainlit logo"]` | Imagem com alt específico |
| `.MuiBox-root > img[alt*="logo"]:first-child` | Primeiro logo em MuiBox |
| `:not([data-mcp])` | Excluir elementos MCP |

### JavaScript APIs Utilizadas

| API | Uso |
|-----|-----|
| `MutationObserver` | Observar mudanças no DOM |
| `querySelectorAll` | Selecionar múltiplos elementos |
| `dataset` | Verificar atributos data-* |

### Chainlit Config

| Opção | Valor | Efeito |
|-------|-------|--------|
| `[features.mcp] enabled` | `true` | Habilita MCP |
| `default_sidebar_state` | `"open"` | Sidebar aberta |
| `[mcp.servers.*]` | comentado | UI manual visível |

---

## 🔍 Troubleshooting

### Logo ainda aparece na tela de login

**Solução:**
1. Limpar cache do navegador (Ctrl+Shift+Del)
2. Hard reload (Ctrl+Shift+R)
3. Abrir DevTools (F12) → Console
4. Verificar se há mensagens de erro
5. Verificar se custom.js foi carregado:
   ```javascript
   // Deve aparecer no console:
   🤖 Gabi. - Custom JS loaded
   ```

### UI "My MCPs" não aparece

**Causa 1:** Servidores pré-configurados
```toml
# Verificar se está comentado:
# [mcp]
# [mcp.servers.*]
```

**Causa 2:** Sidebar fechada
```toml
# Verificar se está configurado:
default_sidebar_state = "open"
```

**Causa 3:** MCP não habilitado
```toml
# Verificar:
[features.mcp]
    enabled = true
```

**Causa 4:** CSS escondendo elemento
```javascript
// No console do navegador, executar:
document.querySelectorAll('[data-mcp], [class*="mcp"], [id*="mcp"]').forEach(el => {
    console.log('MCP element:', el);
    el.style.display = 'block';
    el.style.visibility = 'visible';
});
```

### Custom.js não carrega

**Solução:**
1. Verificar se arquivo existe: `/home/user/chatREBrasil/public/custom.js`
2. Verificar permissões:
   ```bash
   ls -la /home/user/chatREBrasil/public/custom.js
   ```
3. Rebuild da imagem:
   ```bash
   docker-compose build app-agent
   docker-compose up -d app-agent
   ```

---

## ✅ Checklist de Validação

- [ ] Logo do Chainlit NÃO aparece na tela de login
- [ ] Formulário de login funciona normalmente
- [ ] Sidebar abre automaticamente ao fazer login
- [ ] UI "My MCPs" visível na sidebar
- [ ] Botão "Add MCP" ou "+" disponível
- [ ] Console mostra mensagens do custom.js
- [ ] Elementos funcionais (ícones, botões) permanecem visíveis
- [ ] MCP pode ser adicionado manualmente via UI

---

## 📝 Próximos Passos

### Para Reverter para Servidores Automáticos

Se preferir servidores MCP automáticos (sem UI):

1. Descomentar seção `[mcp.servers]` no config.toml
2. Restart: `docker-compose restart app-agent`
3. Servidores conectarão automaticamente ao iniciar

### Para Melhorar Ainda Mais

1. **Adicionar logo customizado na tela de login:**
   - Criar componente React customizado
   - Substituir logo padrão por logo Gabi./ness.

2. **Melhorar feedback visual do MCP:**
   - Toast notifications ao conectar
   - Status indicators para cada servidor

3. **Documentação para usuário final:**
   - Tutorial in-app de como adicionar MCPs
   - Tooltips explicativos

---

**Desenvolvido por:** ness.
**Assistente:** Gabi.
**Tecnologia:** Chainlit + OpenAI + MCP + PostgreSQL
