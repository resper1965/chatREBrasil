# 🏢 Sistema Multi-Agente para Análise de Carteira Imobiliária

Sistema de análise financeira imobiliária baseado em **Agentes IA** com suporte a conexões SQL Server e análises avançadas.

Desenvolvido por **ness.**

![Status](https://img.shields.io/badge/status-operational-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Chainlit](https://img.shields.io/badge/chainlit-1.0+-orange)

---

## 🚀 Quick Start

### 1. Configure a chave API

```bash
cp .env.example .env
nano .env  # Adicione sua OPENAI_API_KEY e configure autenticação
```

**Login padrão:**
- Username: `admin`
- Password: `123`

⚠️ **IMPORTANTE**: Altere a senha padrão em `.env` antes de usar em produção!

### 2. Instale dependências

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Execute o sistema

```bash
chainlit run app/app.py -w
```

### 4. Acesse

**URL**: http://localhost:8000

---

## 📦 Deploy com Docker

### Opção 1: Docker Compose (Recomendado)

```bash
docker compose up -d
```

Acesse: http://localhost:8502

### Opção 2: Docker Standalone

```bash
docker build -t real-estate-agent .
docker run -d -p 8000:8000 --env-file .env --name agent real-estate-agent
```

---

## 🎯 Agentes Disponíveis

### 👔 **Especialista Financeiro**
- Cálculo de ROI, Cap Rate, Cash-on-Cash
- Avaliação de risco personalizável
- Estratégias de diversificação
- Análise de valuation

### 📊 **Analista de Dados**
- Consultas SQL Server
- Extração de métricas
- Análise de performance
- Relatórios consolidados

---

## ⚙️ Configuração Personalizável

Todas as configurações estão em `.env`:

### Thresholds Financeiros

```bash
# Mercado conservador (EUA/Europa)
ROI_EXCELLENT=10
ROI_GOOD=7
CAP_RATE_EXCELLENT=7

# Mercado agressivo (Brasil)
ROI_EXCELLENT=15
ROI_GOOD=12
CAP_RATE_EXCELLENT=10
```

### Conexão SQL Server

```bash
DB_PORT=1433
QUERY_LIMIT=100
```

### Personalização

```bash
AGENT_LANGUAGE=pt  # pt, en, es
INCLUDE_EMOJIS=true
ENABLE_LOGGING=true
LOG_FILE=agent_logs.txt
```

---

## 📊 Exemplos de Uso

### Análise de ROI

```
"Analise ROI de imóvel comprado por 200k, valendo 250k, há 18 meses"
```

### Conexão SQL

```
"Conecta ao servidor localhost, base ImobiliariaDB, user sa, senha MinhaSenha123"
```

### Análise de Risco

```
"Qual o risco de carteira comercial em Lisboa com 75% ocupação?"
```

### Diversificação

```
"Avalie diversificação da minha carteira"
```

---

## 🛠️ Tecnologias

- **Interface**: Chainlit 1.0+
- **Backend**: Python 3.11
- **IA**: OpenAI GPT-4
- **Bancos**: MS SQL Server 2022
- **Conexões**: pyodbc (ODBC Driver 18)
- **Containerização**: Docker & Docker Compose

---

## 📚 Estrutura do Projeto

```
chatREBrasil/
├── app/
│   └── app.py                    # Sistema multi-agente
├── assets/                       # Logos e ícones
├── bmad/                         # BMAD bundles
├── data/                         # Bancos de dados
├── .backup/                      # Backup do projeto
├── Dockerfile                    # Imagem Docker
├── docker-compose.yml            # Orquestração
├── requirements.txt              # Dependências Python
├── README.md                     # Documentação
└── .env                          # Configurações (criar)
```

---

## 🔒 Segurança

- ✅ `.env` não commitado (ver `.gitignore`)
- ✅ Chaves API via variáveis de ambiente
- ✅ **Autenticação** habilitada (username/password)
- ✅ `CHAINLIT_AUTH_SECRET` para assinatura de tokens
- ✅ Logs auditáveis de tentativas de acesso
- ✅ MSSQL com TrustServerCertificate (local)
- ⚠️ **PRODUÇÃO**: Configure senhas fortes e considere OAuth

---

## 🧪 Testes

### Testar Conexão SQL

```bash
python -c "import pyodbc; conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;UID=sa;PWD=test;TrustServerCertificate=yes'); print('✅ OK!')"
```

### Testar API Anthropic

```bash
python -c "from anthropic import Anthropic; import os; from dotenv import load_dotenv; load_dotenv(); client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')); print('✅ OK!')"
```

---

## 📊 Logs e Monitoramento

```bash
# Ver logs em tempo real
tail -f agent_logs.txt

# Estatísticas de uso
grep USER_MESSAGE agent_logs.txt | wc -l
```

---

## 🐛 Troubleshooting

### Erro: "API Key inválida"
```bash
# Verificar .env
cat .env | grep ANTHROPIC_API_KEY
```

### Erro: "ODBC Driver não encontrado"
```bash
# Instalar driver (Linux)
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

### Erro: "Porta 8000 em uso"
```bash
# Usar outra porta
chainlit run app/app.py --port 8080
```

---

## 📖 Documentação Completa

Para documentação detalhada, consulte os artigos do Claude Artifacts:

- **Guia de Implementação**: Análise completa e passo a passo
- **Configuração Avançada**: Personalização de prompts e thresholds
- **Deploy em Produção**: Docker, Cloud, Servidor dedicado

---

## 🎓 Próximos Passos

✅ Implementar sistema básico  
📊 Conectar base de dados real  
🎨 Personalizar thresholds e prompts  
🧪 Testar com dados reais  
🚀 Deploy em produção  
📈 Adicionar visualizações  
🔔 Configurar alertas  

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Versão**: 1.0.0  
**Data**: 2025-10-30  
**Desenvolvido por**: ness.  
**Tecnologias**: ❤️ + 🤖 + OpenAI GPT-4

