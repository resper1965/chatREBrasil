# ✏️ Como Editar Mensagens SEM Rebuild

## 🎯 Objetivo

Este sistema permite que você **edite todas as mensagens exibidas no chat** sem precisar fazer rebuild da aplicação Docker!

---

## 📁 Arquivo de Mensagens

Todas as mensagens editáveis estão em:

```
/home/user/chatREBrasil/messages.json
```

Este arquivo contém **TODAS** as mensagens que aparecem para o usuário:
- Mensagens de boas-vindas
- Mensagens de conexão (sucesso/erro)
- Mensagens do sistema (processando, analisando, etc.)
- Mensagens de MCP (conectado, desconectado)
- Mensagens de PostgreSQL
- E muito mais!

---

## 🚀 Como Editar (3 Passos Simples)

### **Passo 1: Editar o arquivo JSON**

Abra o arquivo `messages.json` com seu editor favorito:

```bash
nano messages.json
# ou
vim messages.json
# ou
code messages.json  # VS Code
```

### **Passo 2: Fazer suas alterações**

Por exemplo, altere a mensagem de boas-vindas:

**ANTES:**
```json
{
  "boas_vindas": {
    "saudacao": "Olá, {username}! 👋",
    "descricao": "Pronto para ajudar com suas análises imobiliárias."
  }
}
```

**DEPOIS:**
```json
{
  "boas_vindas": {
    "saudacao": "Bem-vindo, {username}! 🏢",
    "descricao": "Seu assistente de investimentos está pronto!"
  }
}
```

### **Passo 3: Reiniciar o container (NÃO rebuild!)**

```bash
docker-compose restart app-agent
```

✅ **Pronto!** Suas alterações já estão visíveis no chat!

---

## 📝 Estrutura do arquivo messages.json

### **1. Boas-Vindas**

```json
"boas_vindas": {
  "saudacao": "Olá, {username}! 👋",
  "descricao": "Pronto para ajudar com suas análises imobiliárias.",
  "titulo_opcoes": "Como posso ajudar?",
  "opcoes": [
    "Calcular ROI e rentabilidade",
    "Analisar riscos de investimento",
    "Consultar dados do banco",
    "Gerar relatórios"
  ]
}
```

**Placeholders disponíveis:**
- `{username}` - Nome do usuário logado

---

### **2. Botões de Ação**

```json
"botoes": {
  "conectar_banco": {
    "label": "🔌 Conectar Banco de Dados",
    "descricao": "Conecta ao banco principal"
  }
}
```

---

### **3. Conexão Bem-Sucedida**

```json
"conexao_sucesso": {
  "titulo": "✅ Conexão Bem-Sucedida!",
  "mensagem": "Conectado ao banco {database}. {tabelas_count} tabelas descobertas.",
  "agora_pode": "Agora você pode:",
  "opcoes": [
    "Listar tabelas: \"Quais tabelas existem?\"",
    "Consultar dados: \"Mostre os dados da tabela X\"",
    "Analisar estrutura: \"Qual a estrutura da tabela Y?\""
  ]
}
```

**Placeholders disponíveis:**
- `{database}` - Nome do banco conectado
- `{tabelas_count}` - Número de tabelas descobertas

---

### **4. Erros de Conexão**

```json
"conexao_erro": {
  "titulo": "❌ Erro ao Conectar",
  "mensagem": "{erro_detalhes}",
  "como_resolver": "Como resolver:",
  "passos": [
    "Verifique se o banco está rodando: docker-compose ps",
    "Veja os logs: docker-compose logs db-persist",
    "Reinicie: docker-compose restart app-agent"
  ]
}
```

**Placeholders disponíveis:**
- `{erro_detalhes}` - Mensagem de erro técnica

---

### **5. Mensagens do Sistema**

```json
"mensagens_sistema": {
  "analisando": "🤔 Analisando...",
  "processando": "⚙️ Processando sua solicitação...",
  "conectando": "🔄 Conectando ao banco de dados...",
  "erro_generico": "❌ Ocorreu um erro. Tente novamente."
}
```

---

### **6. MCP (Model Context Protocol)**

```json
"mcp": {
  "conectado": {
    "titulo": "✅ MCP Conectado",
    "mensagem": "**{connection_name}**\n📊 {tools_count} ferramentas disponíveis"
  },
  "desconectado": {
    "titulo": "🔌 MCP Desconectado",
    "mensagem": "{connection_name}"
  },
  "auto_conectado": {
    "mensagem": "✅ Conectei automaticamente ao banco de dados!"
  },
  "erros": {
    "nao_configurado": "❌ **Erro:** MCP não está configurado. Configure em 'My MCPs' primeiro!",
    "sessao_nao_encontrada": "❌ **Erro:** Sessão MCP SQL não encontrada.",
    "erro_conectar": "❌ **Erro ao conectar:** {erro_detalhes}"
  }
}
```

**Placeholders disponíveis:**
- `{connection_name}` - Nome da conexão MCP
- `{tools_count}` - Número de ferramentas disponíveis
- `{erro_detalhes}` - Detalhes do erro

---

### **7. PostgreSQL**

```json
"postgresql": {
  "conectando": "🔄 Conectando ao banco PostgreSQL default...",
  "conectado": {
    "titulo": "✅ Conectado ao PostgreSQL!",
    "mensagem": "Conectado ao banco **{database}** em {host}:{port}\n📊 {tabelas_count} tabelas disponíveis",
    "agora_pode": "Agora você pode:",
    "opcoes": [
      "Listar tabelas: \"Quais tabelas existem?\"",
      "Consultar dados: \"Mostre dados da tabela X\"",
      "Ver histórico: \"Mostre meus últimos chats\""
    ]
  },
  "erro": {
    "titulo": "❌ Erro ao Conectar ao PostgreSQL Default",
    "mensagem": "{erro_detalhes}",
    "como_resolver": "Como resolver:",
    "passos": [
      "Verifique se o PostgreSQL está rodando: docker-compose ps | grep db-persist",
      "Veja os logs: docker-compose logs db-persist",
      "Reinicie o banco: docker-compose restart db-persist",
      "Verifique as credenciais no arquivo .env"
    ]
  }
}
```

**Placeholders disponíveis:**
- `{database}` - Nome do banco
- `{host}` - Host do banco
- `{port}` - Porta do banco
- `{tabelas_count}` - Número de tabelas
- `{erro_detalhes}` - Detalhes do erro

---

## 💡 Dicas Importantes

### ✅ O que PODE ser editado:

- ✅ Textos de mensagens
- ✅ Emojis
- ✅ Títulos e descrições
- ✅ Listas de opções
- ✅ Passos de troubleshooting
- ✅ Placeholders (como `{username}`, `{database}`)

### ❌ O que NÃO deve ser alterado:

- ❌ A estrutura JSON (chaves, hierarquia)
- ❌ Os nomes dos placeholders (`{username}` deve permanecer exatamente assim)
- ❌ As linhas que começam com `_` (comentários técnicos)

---

## 🧪 Testando suas Alterações

### **1. Edite uma mensagem simples**

Vamos testar alterando a mensagem de boas-vindas:

```bash
# 1. Edite o arquivo
nano messages.json

# 2. Altere a linha:
"saudacao": "Olá, {username}! 👋",
# Para:
"saudacao": "Seja bem-vindo, {username}! 🚀",

# 3. Salve (Ctrl+O, Enter, Ctrl+X)

# 4. Reinicie
docker-compose restart app-agent

# 5. Aguarde ~10 segundos

# 6. Acesse http://localhost:8502

# 7. Faça login novamente

# ✅ Você verá: "Seja bem-vindo, Ricardo! 🚀"
```

---

## 🛠️ Troubleshooting

### **Problema: Alterações não aparecem**

**Solução:**
```bash
# 1. Verifique se salvou o arquivo corretamente
cat messages.json | grep "saudacao"

# 2. Reinicie novamente
docker-compose restart app-agent

# 3. Aguarde ~15 segundos
docker-compose logs app-agent | grep "ready"

# 4. Limpe o cache do navegador
# Chrome/Edge: Ctrl+Shift+Del → Cached images and files
# Firefox: Ctrl+Shift+Del → Cache

# 5. Faça logout e login novamente
```

---

### **Problema: Erro de JSON inválido**

Se você ver erros no log:

```bash
docker-compose logs app-agent | grep "Erro ao carregar messages.json"
```

**Solução:**
```bash
# 1. Verifique a sintaxe JSON
cat messages.json

# Se houver erro, corrija:
# - Verifique se todas as chaves { } estão fechadas
# - Verifique se todas as vírgulas estão corretas
# - Não pode ter vírgula no último item de uma lista

# 2. Valide online (copie e cole o conteúdo):
# https://jsonlint.com/

# 3. Após corrigir, reinicie:
docker-compose restart app-agent
```

---

### **Problema: Placeholders não são substituídos**

Se você vê `{username}` ao invés do nome:

**Causa:** Placeholder escrito incorretamente

**Solução:**
```json
❌ ERRADO:
"saudacao": "Olá, {user_name}! 👋",  // underscore errado

✅ CORRETO:
"saudacao": "Olá, {username}! 👋",   // sem underscore
```

---

## 📋 Checklist de Edição

Antes de fazer restart, verifique:

- [ ] JSON válido (sem erros de sintaxe)
- [ ] Placeholders escritos exatamente como no original
- [ ] Emojis copiados corretamente (se aplicável)
- [ ] Listas com vírgulas corretas (sem vírgula no último item)
- [ ] Salvou o arquivo (Ctrl+O no nano, :wq no vim)

---

## 🔄 Processo Completo (Resumo)

```bash
# 1. EDITAR
nano messages.json

# 2. SALVAR
# (Ctrl+O, Enter, Ctrl+X no nano)

# 3. REINICIAR (não rebuild!)
docker-compose restart app-agent

# 4. AGUARDAR
# (~15 segundos)

# 5. TESTAR
# Acesse http://localhost:8502
```

---

## 🎓 Exemplos Práticos

### **Exemplo 1: Tornar mensagens mais informais**

**ANTES:**
```json
"saudacao": "Olá, {username}! 👋",
"descricao": "Pronto para ajudar com suas análises imobiliárias."
```

**DEPOIS:**
```json
"saudacao": "E aí, {username}! 😎",
"descricao": "Bora analisar uns imóveis?"
```

---

### **Exemplo 2: Remover emojis**

**ANTES:**
```json
"mensagens_sistema": {
  "analisando": "🤔 Analisando...",
  "processando": "⚙️ Processando sua solicitação..."
}
```

**DEPOIS:**
```json
"mensagens_sistema": {
  "analisando": "Analisando...",
  "processando": "Processando sua solicitação..."
}
```

---

### **Exemplo 3: Mensagens em inglês**

**ANTES:**
```json
"conexao_sucesso": {
  "titulo": "✅ Conexão Bem-Sucedida!",
  "agora_pode": "Agora você pode:"
}
```

**DEPOIS:**
```json
"conexao_sucesso": {
  "titulo": "✅ Connection Successful!",
  "agora_pode": "Now you can:"
}
```

---

## 📚 Mais Informações

- **Documentação do Chainlit:** https://docs.chainlit.io/
- **JSON Validator:** https://jsonlint.com/
- **Docker Compose Docs:** https://docs.docker.com/compose/

---

## 🆘 Suporte

Se você precisar de ajuda:

1. **Verifique os logs:**
   ```bash
   docker-compose logs app-agent | tail -50
   ```

2. **Restaure o backup original:**
   ```bash
   git checkout messages.json
   docker-compose restart app-agent
   ```

3. **Consulte a documentação:**
   - `MELHORIAS_IMPLEMENTADAS.md`
   - `PERSISTENCIA_E_BARRA_LATERAL.md`
   - `CONEXAO_DEFAULT_MCP.md`

---

**Atualizado:** 2025-11-05
**Versão:** Gabi. v1.0 com Sistema de Mensagens Editáveis

---

💡 **Lembre-se:** Você pode editar QUALQUER texto que aparece para o usuário, SEM rebuild! Basta editar `messages.json` e reiniciar o container. 🚀
