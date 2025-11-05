# 💾 Persistência de Chats e Funcionalidades da Barra Lateral

## 📋 Resumo

Este documento explica como funciona a persistência de chats no ChatRE Brasil (Gabi.) e as funcionalidades disponíveis na barra lateral.

---

## 🕒 Quando o Chat é Persistido?

### **Persistência Automática em Tempo Real**

O Chainlit persiste os chats **automaticamente** nos seguintes momentos:

#### 1️⃣ **Ao Iniciar um Novo Chat**
```python
@cl.on_chat_start
async def start():
    # Quando você faz login e inicia uma nova conversa
    # Um novo thread (conversação) é criado no PostgreSQL
```
- ✅ **Thread criado** com ID único
- ✅ **Metadados salvos** (usuário, data/hora, perfil)
- ✅ **Sessão iniciada** no banco de dados

#### 2️⃣ **A Cada Mensagem Enviada**
```python
@cl.on_message
async def main(message: cl.Message):
    # Cada mensagem é persistida IMEDIATAMENTE
```
- ✅ **Mensagem do usuário** salva no banco
- ✅ **Resposta do agente** salva no banco
- ✅ **Elementos anexados** (imagens, arquivos, etc.) salvos
- ✅ **Metadados** (timestamp, autor, etc.) salvos

#### 3️⃣ **Ao Finalizar o Chat**
```python
@cl.on_chat_end
async def end():
    # Quando você fecha a aba ou faz logout
    # A thread é marcada como encerrada
```
- ✅ **Thread marcada como completa**
- ✅ **Recursos limpos** (conexões, cache, etc.)
- ✅ **Logs finalizados**

### **Onde os Dados São Salvos?**

```yaml
PostgreSQL:
  Host: db-persist:5432
  Database: chainlit
  Tabelas:
    - threads: Conversações/Threads
    - steps: Mensagens individuais
    - users: Usuários do sistema
    - elements: Arquivos anexados
    - feedbacks: Avaliações do usuário
```

### **Verificar Persistência no Banco**

Você pode consultar os chats salvos diretamente:

```bash
# Acessar o container PostgreSQL
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit

# Listar threads (conversas)
SELECT id, name, user_id, created_at FROM threads ORDER BY created_at DESC LIMIT 10;

# Listar mensagens de uma thread específica
SELECT id, name, type, output, created_at
FROM steps
WHERE thread_id = 'seu-thread-id-aqui'
ORDER BY created_at;

# Contar total de chats
SELECT COUNT(*) FROM threads;

# Ver últimos 5 chats
SELECT id, name, created_at, user_id FROM threads ORDER BY created_at DESC LIMIT 5;
```

---

## 🎛️ Funcionalidades da Barra Lateral

### **✅ Funcionalidades Disponíveis Nativamente**

A barra lateral do Chainlit já possui funcionalidades integradas:

#### 1️⃣ **Listar Conversas Anteriores**
- ✅ Clique no ícone de **histórico** (ou hamburger menu)
- ✅ Todas as suas conversas aparecem em ordem cronológica
- ✅ Mostra **nome da conversa** e **data/hora**

#### 2️⃣ **Retomar Conversa Anterior**
- ✅ Clique em qualquer conversa na lista
- ✅ O chat é restaurado **completamente**:
  - Todas as mensagens
  - Contexto dos agentes
  - Elementos anexados
  - Estado da sessão

```python
@cl.on_chat_resume
async def on_resume(thread):
    # Handler que restaura o estado completo da conversa
    agents = create_agents()
    cl.user_session.set("agents", agents)
    # Mensagens são restauradas automaticamente pelo Chainlit
```

#### 3️⃣ **Renomear Conversas** ✏️
**Status: DISPONÍVEL NATIVAMENTE**

- ✅ Passe o mouse sobre uma conversa na barra lateral
- ✅ Clique no ícone de **editar/lápis** (⋮ ou ...)
- ✅ Selecione **"Rename"** ou **"Renomear"**
- ✅ Digite o novo nome
- ✅ Pressione Enter

**Como funciona:**
```
Interface do Chainlit → API interna → data_layer.update_thread(thread_id, name=novo_nome) → PostgreSQL
```

#### 4️⃣ **Deletar Conversas** 🗑️
**Status: DISPONÍVEL NATIVAMENTE**

- ✅ Passe o mouse sobre uma conversa na barra lateral
- ✅ Clique no ícone de **menu** (⋮ ou ...)
- ✅ Selecione **"Delete"** ou **"Excluir"**
- ✅ Confirme a exclusão
- ✅ A conversa é **permanentemente removida** do banco

**Como funciona:**
```
Interface do Chainlit → API interna → data_layer.delete_thread(thread_id) → PostgreSQL (DELETE)
```

⚠️ **ATENÇÃO:** A exclusão é **permanente** e não pode ser desfeita!

#### 5️⃣ **Buscar Conversas** 🔍
- ✅ Digite no campo de busca da barra lateral
- ✅ Filtra conversas por:
  - Nome da conversa
  - Conteúdo de mensagens
  - Data

#### 6️⃣ **Iniciar Nova Conversa** ➕
- ✅ Clique no botão **"New Chat"** ou **"Nova Conversa"**
- ✅ Uma nova thread é criada
- ✅ Estado limpo (sem contexto anterior)

---

## 🎨 Visualização da Barra Lateral

```
┌─────────────────────────────┐
│ Gabi.                   [≡] │ ← Header
├─────────────────────────────┤
│ 🔍 Buscar conversas...      │ ← Campo de busca
├─────────────────────────────┤
│ ➕ Nova Conversa            │ ← Botão para novo chat
├─────────────────────────────┤
│ 📂 Conversas Recentes       │
│                             │
│ 📄 Análise de ROI          │ ← Conversas
│    Hoje às 14:30       [⋮] │   salvas
│                             │
│ 📄 Conectar PostgreSQL     │
│    Ontem às 09:15      [⋮] │
│                             │
│ 📄 Avaliação de Risco      │
│    2 dias atrás        [⋮] │
│                             │
└─────────────────────────────┘

Ao clicar em [⋮]:
┌─────────────────┐
│ ✏️ Renomear     │
│ 🗑️ Deletar      │
└─────────────────┘
```

---

## 🔧 Customização Avançada (Opcional)

Se você quiser adicionar comportamentos customizados ao renomear ou deletar (como logs específicos, validações, ou limpeza de recursos), você precisa implementar um **Custom Data Layer**.

### **Exemplo: Custom Data Layer**

```python
from chainlit.data import BaseDataLayer, ThreadDict
import chainlit as cl

class CustomDataLayer(BaseDataLayer):

    async def delete_thread(self, thread_id: str):
        """Customiza comportamento ao deletar thread"""
        # 1. Log customizado
        print(f"🗑️ Deletando thread: {thread_id}")

        # 2. Limpeza de recursos externos (se houver)
        # Por exemplo: deletar arquivos, fechar conexões, etc.

        # 3. Chamar o método padrão para deletar do banco
        await super().delete_thread(thread_id)

        print(f"✅ Thread {thread_id} deletada com sucesso")

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ):
        """Customiza comportamento ao renomear/atualizar thread"""
        if name:
            print(f"✏️ Renomeando thread {thread_id} para: {name}")

        # Chamar o método padrão
        await super().update_thread(thread_id, name, user_id, metadata, tags)

        print(f"✅ Thread {thread_id} atualizada")

# Configurar no app
cl_data = CustomDataLayer()
```

**Para habilitar:**
```python
# No app.py
import chainlit as cl
from chainlit.data import cl_data

# Definir custom data layer
cl_data = CustomDataLayer()
```

---

## 📊 Testando a Persistência

### **Teste 1: Criar e Recuperar Chat**

```bash
# 1. Inicie a aplicação
docker-compose up -d

# 2. Acesse http://localhost:8502
# 3. Faça login
# 4. Envie algumas mensagens
# 5. Feche a aba do navegador
# 6. Abra novamente e faça login
# 7. Clique na barra lateral
# ✅ Sua conversa deve estar lá!
```

### **Teste 2: Renomear Chat**

```bash
# 1. Na barra lateral, passe o mouse sobre uma conversa
# 2. Clique no menu [⋮]
# 3. Selecione "Rename"
# 4. Digite "Meu Teste de Análise"
# 5. Pressione Enter
# ✅ O nome deve mudar imediatamente
```

### **Teste 3: Deletar Chat**

```bash
# 1. Na barra lateral, passe o mouse sobre uma conversa
# 2. Clique no menu [⋮]
# 3. Selecione "Delete"
# 4. Confirme
# ✅ A conversa deve desaparecer da lista
```

### **Teste 4: Verificar no Banco**

```bash
# Antes de deletar
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "SELECT COUNT(*) FROM threads;"
# Resultado: 5 threads

# Depois de deletar uma conversa
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "SELECT COUNT(*) FROM threads;"
# Resultado: 4 threads ✅
```

---

## 🛠️ Troubleshooting

### **Problema: Não vejo a barra lateral**

**Solução:**
```bash
# 1. Verifique se a persistência está habilitada
cat .chainlit/config.toml | grep -A 2 "\[persistence\]"
# Deve mostrar: enabled = true

# 2. Verifique a URL do banco
echo $CHAINLIT_DATABASE_URL
# Deve ser: postgresql://chainlit:chainlit@db-persist:5432/chainlit

# 3. Reinicie o container
docker-compose restart app-agent
```

### **Problema: Conversas não aparecem na barra lateral**

**Solução:**
```bash
# 1. Verifique se o PostgreSQL está rodando
docker-compose ps | grep db-persist
# Deve estar "Up"

# 2. Teste conexão ao banco
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "SELECT 1;"
# Deve retornar: 1

# 3. Verifique se há threads no banco
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "SELECT COUNT(*) FROM threads;"
# Se for 0, crie uma nova conversa
```

### **Problema: Erro ao deletar/renomear**

**Solução:**
```bash
# 1. Veja os logs do app
docker-compose logs app-agent | grep -i "error"

# 2. Verifique permissões no banco
docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit -c "
SELECT grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_name='threads';
"
# Deve ter SELECT, INSERT, UPDATE, DELETE

# 3. Reinicie tudo
docker-compose down
docker-compose up -d
```

---

## 📋 Resumo Final

| **Funcionalidade** | **Status** | **Como Usar** |
|-------------------|-----------|---------------|
| **Persistência automática** | ✅ Ativa | Acontece automaticamente a cada mensagem |
| **Listar conversas** | ✅ Disponível | Clique no ícone de menu/histórico |
| **Retomar conversa** | ✅ Disponível | Clique em qualquer conversa da lista |
| **Renomear conversa** | ✅ Disponível | Menu [⋮] → Rename |
| **Deletar conversa** | ✅ Disponível | Menu [⋮] → Delete |
| **Buscar conversas** | ✅ Disponível | Campo de busca na barra lateral |
| **Nova conversa** | ✅ Disponível | Botão "New Chat" |
| **Backup automático** | ✅ Ativo | Dados no volume `postgres_data` |

---

## 🎓 Dicas de Uso

1. **Nomeie suas conversas:** Use nomes descritivos para facilitar a busca
2. **Delete conversas antigas:** Mantenha sua barra lateral organizada
3. **Use o starter "Ver Histórico":** Consulte seus chats via SQL
4. **Backup regular:** O volume Docker `postgres_data` contém tudo

---

## 📚 Referências

- [Chainlit Data Persistence](https://docs.chainlit.io/api-reference/data-persistence/overview)
- [Custom Data Layer](https://docs.chainlit.io/api-reference/data-persistence/custom-data-layer)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Atualizado:** 2025-11-05
**Versão:** Gabi. v1.0 com PostgreSQL
