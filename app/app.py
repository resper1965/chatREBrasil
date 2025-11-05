"""
Sistema Multi-Agente para Análise de Carteira Imobiliária

Versão: 1.0
Desenvolvido por: ness.
Tecnologias: OpenAI GPT-4, Chainlit, Python
"""

import chainlit as cl
from openai import OpenAI
import pyodbc
import json
import os
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

# MCP imports
from mcp import ClientSession

# Carregar variáveis de ambiente
load_dotenv()


# ==================== MENSAGENS EDITÁVEIS ====================

class Messages:
    """Carrega mensagens de um arquivo JSON editável - SEM REBUILD!"""

    _messages = None

    @classmethod
    def load(cls):
        """Carrega mensagens do arquivo JSON"""
        if cls._messages is None:
            try:
                messages_file = os.path.join(os.path.dirname(__file__), '..', 'messages.json')
                with open(messages_file, 'r', encoding='utf-8') as f:
                    cls._messages = json.load(f)
            except Exception as e:
                print(f"⚠️ Erro ao carregar messages.json: {e}")
                # Fallback para mensagens padrão
                cls._messages = {
                    "boas_vindas": {
                        "saudacao": "Olá, {username}! 👋",
                        "descricao": "Pronto para ajudar.",
                        "titulo_opcoes": "Como posso ajudar?",
                        "opcoes": []
                    },
                    "mensagens_sistema": {
                        "analisando": "🤔 Analisando...",
                        "conectando": "🔄 Conectando...",
                        "erro_generico": "❌ Erro."
                    }
                }
        return cls._messages

    @classmethod
    def get(cls, *keys, **kwargs):
        """Acessa uma mensagem do JSON

        Exemplo:
            Messages.get('boas_vindas', 'saudacao', username='João')
            -> "Olá, João! 👋"
        """
        msgs = cls.load()

        # Navegar pelos keys
        for key in keys:
            if isinstance(msgs, dict):
                msgs = msgs.get(key, "")
            else:
                return ""

        # Substituir placeholders
        if isinstance(msgs, str) and kwargs:
            try:
                return msgs.format(**kwargs)
            except:
                return msgs

        return msgs

    @classmethod
    def reload(cls):
        """Recarrega mensagens (útil para testes)"""
        cls._messages = None
        return cls.load()


# ==================== CONFIGURAÇÕES PERSONALIZÁVEIS ====================

class Config:
    """Configurações centralizadas do sistema"""
    
    # API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4o")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
    
    # Database
    DEFAULT_DB_PORT = int(os.getenv("DB_PORT", "1433"))
    QUERY_LIMIT = int(os.getenv("QUERY_LIMIT", "100"))

    # MSSQL Configuration
    MSSQL_SERVER = os.getenv("MSSQL_SERVER", "localhost")
    MSSQL_DATABASE = os.getenv("MSSQL_DATABASE")
    MSSQL_USERNAME = os.getenv("MSSQL_USERNAME", "sa")
    MSSQL_PASSWORD = os.getenv("MSSQL_SA_PASSWORD", "Str0ng!Passw0rd")

    # MSSQL Default Connection (para botão de conexão rápida)
    MSSQL_DEFAULT_ENABLED = os.getenv("MSSQL_DEFAULT_ENABLED", "true").lower() == "true"
    MSSQL_DEFAULT_SERVER = os.getenv("MSSQL_DEFAULT_SERVER", "mssql")
    MSSQL_DEFAULT_PORT = int(os.getenv("MSSQL_DEFAULT_PORT", "1433"))
    MSSQL_DEFAULT_DATABASE = os.getenv("MSSQL_DEFAULT_DATABASE", "REB_BI_IA")
    MSSQL_DEFAULT_USERNAME = os.getenv("MSSQL_DEFAULT_USERNAME", "sa")
    MSSQL_DEFAULT_PASSWORD = os.getenv("MSSQL_DEFAULT_PASSWORD", os.getenv("MSSQL_SA_PASSWORD", "Str0ng!Passw0rd"))

    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db-persist")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "chainlit")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "chainlit")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "chainlit")

    # PostgreSQL Default Connection (para botão de conexão rápida)
    POSTGRES_DEFAULT_ENABLED = os.getenv("POSTGRES_DEFAULT_ENABLED", "true").lower() == "true"
    POSTGRES_DEFAULT_HOST = os.getenv("POSTGRES_DEFAULT_HOST", "db-persist")
    POSTGRES_DEFAULT_PORT = int(os.getenv("POSTGRES_DEFAULT_PORT", "5432"))
    POSTGRES_DEFAULT_DATABASE = os.getenv("POSTGRES_DEFAULT_DATABASE", "chainlit")
    POSTGRES_DEFAULT_USERNAME = os.getenv("POSTGRES_DEFAULT_USERNAME", "chainlit")
    POSTGRES_DEFAULT_PASSWORD = os.getenv("POSTGRES_DEFAULT_PASSWORD", "chainlit")
    
    # Sistema
    ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    LOG_FILE = os.getenv("LOG_FILE", "agent_logs.txt")
    
    # Personalização de Agentes
    AGENT_LANGUAGE = os.getenv("AGENT_LANGUAGE", "pt")  # pt, en, es
    INCLUDE_EMOJIS = os.getenv("INCLUDE_EMOJIS", "true").lower() == "true"
    
    # Análise Financeira - Thresholds Personalizáveis
    ROI_EXCELLENT_THRESHOLD = float(os.getenv("ROI_EXCELLENT", "12"))
    ROI_GOOD_THRESHOLD = float(os.getenv("ROI_GOOD", "8"))
    CAP_RATE_EXCELLENT_THRESHOLD = float(os.getenv("CAP_RATE_EXCELLENT", "8"))
    CAP_RATE_GOOD_THRESHOLD = float(os.getenv("CAP_RATE_GOOD", "5"))
    RISK_HIGH_THRESHOLD = int(os.getenv("RISK_HIGH", "50"))
    RISK_MEDIUM_THRESHOLD = int(os.getenv("RISK_MEDIUM", "25"))


# Inicializar cliente OpenAI
client = OpenAI(api_key=Config.OPENAI_API_KEY)

# Storage de conexões SQL (por sessão)
connections_store: Dict[str, Dict[str, Any]] = {}


# ==================== LOGGING ====================

def log_message(level: str, message: str, user_id: str = "system"):
    """Sistema de logging customizável"""
    if not Config.ENABLE_LOGGING:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [{user_id}] {message}\n"
    
    try:
        with open(Config.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Erro ao gravar log: {e}")


# ==================== ENUMS ====================

class AgentType(Enum):
    COORDINATOR = "coordinator"
    FINANCIAL_EXPERT = "financial_expert"
    DATA_ANALYST = "data_analyst"


# ==================== FERRAMENTAS SQL ====================

SQL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "connect_database",
            "description": "Conecta a uma base de dados MS SQL Server",
            "parameters": {
                "type": "object",
                "properties": {
                    "server": {"type": "string", "description": "Endereço do servidor SQL"},
                    "database": {"type": "string", "description": "Nome da base de dados"},
                    "username": {"type": "string", "description": "Usuário SQL"},
                    "password": {"type": "string", "description": "Senha"},
                    "port": {"type": "integer", "description": f"Porta (padrão: {Config.DEFAULT_DB_PORT})"}
                },
                "required": ["server", "database", "username", "password"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_query",
            "description": "Executa query SQL SELECT para análise de dados",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query SQL a executar"},
                    "limit": {"type": "integer", "description": f"Limite de resultados (padrão: {Config.QUERY_LIMIT})"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tables",
            "description": "Lista todas as tabelas disponíveis na base de dados",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "describe_table",
            "description": "Descreve a estrutura de uma tabela (colunas, tipos, etc)",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Nome da tabela"}
                },
                "required": ["table_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_portfolio_summary",
            "description": "Retorna resumo consolidado da carteira imobiliária",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


# ==================== FERRAMENTAS FINANCEIRAS ====================

FINANCIAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_roi",
            "description": "Calcula ROI (Return on Investment) de um imóvel ou carteira",
            "parameters": {
                "type": "object",
                "properties": {
                    "initial_investment": {"type": "number", "description": "Investimento inicial"},
                    "current_value": {"type": "number", "description": "Valor atual"},
                    "period_months": {"type": "number", "description": "Período em meses"}
                },
                "required": ["initial_investment", "current_value", "period_months"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_cap_rate",
            "description": "Calcula taxa de capitalização (Cap Rate) de um imóvel",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_noi": {"type": "number", "description": "NOI anual (Net Operating Income)"},
                    "property_value": {"type": "number", "description": "Valor do imóvel"}
                },
                "required": ["annual_noi", "property_value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_cash_on_cash",
            "description": "Calcula retorno Cash-on-Cash",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_cash_flow": {"type": "number", "description": "Fluxo de caixa anual"},
                    "total_cash_invested": {"type": "number", "description": "Total investido em cash"}
                },
                "required": ["annual_cash_flow", "total_cash_invested"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "diversification_analysis",
            "description": "Analisa diversificação da carteira",
            "parameters": {
                "type": "object",
                "properties": {
                    "portfolio_data": {"type": "string", "description": "Dados da carteira em JSON"}
                },
                "required": ["portfolio_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "risk_assessment",
            "description": "Avalia risco de um imóvel ou carteira",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_type": {"type": "string", "description": "Tipo de propriedade"},
                    "location": {"type": "string", "description": "Localização"},
                    "occupancy_rate": {"type": "number", "description": "Taxa de ocupação (0-100)"},
                    "debt_ratio": {"type": "number", "description": "Ratio de dívida (0-1)"}
                },
                "required": ["property_type", "location", "occupancy_rate"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "valuation_analysis",
            "description": "Análise de valuation e potencial de valorização",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_details": {"type": "string", "description": "Detalhes do imóvel em JSON"}
                },
                "required": ["property_details"]
            }
        }
    }
]


# ==================== EXECUÇÃO DE FERRAMENTAS SQL ====================

def execute_sql_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Executa ferramentas SQL"""
    session_id = cl.user_session.get("id", "default")
    
    if session_id not in connections_store:
        connections_store[session_id] = {"connections": {}, "current": None}
    
    session_data = connections_store[session_id]
    
    try:
        if tool_name == "connect_database":
            server = tool_input.get("server")
            database = tool_input.get("database")
            username = tool_input.get("username")
            password = tool_input.get("password")
            port = tool_input.get("port", Config.DEFAULT_DB_PORT)
            
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
            
            log_message("INFO", f"Conectando a {server}/{database}", session_id)
            
            conn = pyodbc.connect(conn_str, timeout=10)
            session_data["connections"]["main"] = {
                "connection": conn,
                "server": server,
                "database": database
            }
            session_data["current"] = "main"
            
            log_message("SUCCESS", f"Conectado com sucesso a {server}/{database}", session_id)
            return f"✅ Conectado à base {database} no servidor {server}"
        
        # Verificar conexão ativa
        if not session_data["current"]:
            return "❌ Nenhuma conexão ativa. Use connect_database primeiro."
        
        conn = session_data["connections"][session_data["current"]]["connection"]
        cursor = conn.cursor()
        
        if tool_name == "execute_query":
            query = tool_input.get("query")
            limit = tool_input.get("limit", Config.QUERY_LIMIT)
            
            if not query.strip().upper().startswith("SELECT"):
                return "❌ Apenas queries SELECT são permitidas nesta ferramenta"
            
            log_message("INFO", f"Executando query: {query[:100]}...", session_id)
            
            cursor.execute(query)
            rows = cursor.fetchmany(limit)
            columns = [desc[0] for desc in cursor.description]
            
            result = {
                "columns": columns,
                "rows": [dict(zip(columns, row)) for row in rows],
                "count": len(rows),
                "limited": len(rows) == limit
            }
            
            return json.dumps(result, indent=2, default=str)
        
        elif tool_name == "list_tables":
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            tables = [{"schema": row[0], "name": row[1]} for row in cursor.fetchall()]
            return json.dumps(tables, indent=2)
        
        elif tool_name == "describe_table":
            table = tool_input.get("table_name")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
            """, table)
            cols = [{
                "name": r[0],
                "type": r[1],
                "max_length": r[2],
                "nullable": r[3]
            } for r in cursor.fetchall()]
            return json.dumps(cols, indent=2)
        
        elif tool_name == "get_portfolio_summary":
            # Query customizável - adapte ao seu schema
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_properties,
                    SUM(purchase_price) as total_invested,
                    SUM(current_value) as current_value,
                    AVG(rental_yield) as avg_yield
                FROM properties
                WHERE status = 'Ativo'
            """)
            row = cursor.fetchone()
            
            if row:
                return json.dumps({
                    "total_properties": row[0] or 0,
                    "total_invested": float(row[1]) if row[1] else 0,
                    "current_value": float(row[2]) if row[2] else 0,
                    "avg_yield": float(row[3]) if row[3] else 0
                }, indent=2)
            else:
                return json.dumps({"error": "Nenhum dado encontrado"})
        
    except Exception as e:
        log_message("ERROR", f"Erro SQL: {str(e)}", session_id)
        return f"❌ Erro: {str(e)}"


# ==================== EXECUÇÃO DE FERRAMENTAS FINANCEIRAS ====================

def execute_financial_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Executa ferramentas financeiras com thresholds personalizáveis"""
    try:
        if tool_name == "calculate_roi":
            initial = tool_input.get("initial_investment")
            current = tool_input.get("current_value")
            months = tool_input.get("period_months")
            
            roi = ((current - initial) / initial) * 100
            annual_roi = (roi / months) * 12
            
            # Interpretação baseada em thresholds configuráveis
            if annual_roi > Config.ROI_EXCELLENT_THRESHOLD:
                interpretation = "Excelente"
            elif annual_roi > Config.ROI_GOOD_THRESHOLD:
                interpretation = "Bom"
            else:
                interpretation = "Regular"
            
            return json.dumps({
                "roi_percentage": round(roi, 2),
                "annual_roi": round(annual_roi, 2),
                "absolute_gain": round(current - initial, 2),
                "interpretation": interpretation,
                "benchmarks": {
                    "excellent": f">{Config.ROI_EXCELLENT_THRESHOLD}%",
                    "good": f">{Config.ROI_GOOD_THRESHOLD}%"
                }
            }, indent=2)
        
        elif tool_name == "calculate_cap_rate":
            noi = tool_input.get("annual_noi")
            value = tool_input.get("property_value")
            
            cap_rate = (noi / value) * 100
            
            if cap_rate > Config.CAP_RATE_EXCELLENT_THRESHOLD:
                interpretation = "Excelente"
            elif cap_rate > Config.CAP_RATE_GOOD_THRESHOLD:
                interpretation = "Bom"
            else:
                interpretation = "Baixo"
            
            return json.dumps({
                "cap_rate": round(cap_rate, 2),
                "interpretation": interpretation,
                "annual_noi": noi,
                "property_value": value
            }, indent=2)
        
        elif tool_name == "calculate_cash_on_cash":
            cash_flow = tool_input.get("annual_cash_flow")
            invested = tool_input.get("total_cash_invested")
            
            coc = (cash_flow / invested) * 100
            
            interpretation = "Excelente" if coc > 10 else "Bom" if coc > 6 else "Regular"
            
            return json.dumps({
                "cash_on_cash": round(coc, 2),
                "interpretation": interpretation,
                "annual_cash_flow": cash_flow,
                "total_invested": invested
            }, indent=2)
        
        elif tool_name == "risk_assessment":
            prop_type = tool_input.get("property_type")
            location = tool_input.get("location")
            occupancy = tool_input.get("occupancy_rate")
            debt = tool_input.get("debt_ratio", 0)
            
            risk_score = 0
            factors = {}
            
            # Fatores de risco personalizáveis
            if occupancy < 80:
                risk_score += 30
                factors["occupancy"] = "Risco - Taxa abaixo de 80%"
            else:
                factors["occupancy"] = "OK"
            
            if debt > 0.7:
                risk_score += 25
                factors["debt"] = "Alto - Alavancagem acima de 70%"
            else:
                factors["debt"] = "OK"
            
            if prop_type.lower() in ["comercial", "retail", "commercial"]:
                risk_score += 15
                factors["type"] = "Risco elevado - Setor comercial"
            else:
                factors["type"] = "OK"
            
            # Interpretação baseada em thresholds
            if risk_score > Config.RISK_HIGH_THRESHOLD:
                risk_level = "Alto"
                recommendation = "Considerar venda ou reestruturação"
            elif risk_score > Config.RISK_MEDIUM_THRESHOLD:
                risk_level = "Médio"
                recommendation = "Monitorar de perto e avaliar melhorias"
            else:
                risk_level = "Baixo"
                recommendation = "Manter"
            
            return json.dumps({
                "risk_score": risk_score,
                "risk_level": risk_level,
                "factors": factors,
                "recommendation": recommendation,
                "details": {
                    "property_type": prop_type,
                    "location": location,
                    "occupancy_rate": occupancy,
                    "debt_ratio": debt
                }
            }, indent=2)
        
        elif tool_name == "diversification_analysis":
            portfolio = json.loads(tool_input.get("portfolio_data"))
            
            types = {}
            locations = {}
            total_value = 0
            
            for prop in portfolio:
                prop_type = prop.get("type", "Unknown")
                prop_loc = prop.get("location", "Unknown")
                prop_value = prop.get("value", 0)
                
                types[prop_type] = types.get(prop_type, 0) + 1
                locations[prop_loc] = locations.get(prop_loc, 0) + 1
                total_value += prop_value
            
            diversification_score = len(types) * 10 + len(locations) * 5
            
            recommendation = "Bem diversificada" if len(types) >= 3 and len(locations) >= 3 else "Considerar diversificar"
            
            return json.dumps({
                "by_type": types,
                "by_location": locations,
                "total_properties": len(portfolio),
                "total_value": total_value,
                "diversification_score": diversification_score,
                "recommendation": recommendation
            }, indent=2)
        
        elif tool_name == "valuation_analysis":
            details = json.loads(tool_input.get("property_details"))
            
            # Análise simplificada - pode ser expandida
            return json.dumps({
                "valuation_status": "Em análise",
                "market_comparison": "Dados comparativos em processamento",
                "appreciation_potential": "Médio-Alto",
                "factors": {
                    "location_score": 8,
                    "condition_score": 7,
                    "market_trend": "Positivo"
                },
                "property_details": details
            }, indent=2)
        
    except Exception as e:
        return f"❌ Erro na análise financeira: {str(e)}"


# ==================== CLASSE AGENT ====================

class Agent:
    """Classe base para agentes especializados"""
    
    def __init__(self, agent_type: AgentType, name: str, system_prompt: str, tools: List[Dict] = None):
        self.type = agent_type
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.message_history = [{"role": "system", "content": self.system_prompt}]
    
    async def process(self, user_message: str, context: Dict = None, agents_ref: Dict = None) -> str:
        """Processa mensagem e retorna resposta"""
        if context:
            user_message = f"CONTEXTO: {json.dumps(context, indent=2, ensure_ascii=False)}\n\nPERGUNTA: {user_message}"
        
        self.message_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Loop de tool calling
        while True:
            try:
                response = client.chat.completions.create(
                    model=Config.MODEL,
                    messages=self.message_history,
                    tools=self.tools if self.tools else None,
                    tool_choice="auto",
                    max_tokens=Config.MAX_TOKENS,
                    temperature=0.7
                )
                
                message = response.choices[0].message
                self.message_history.append(message.model_dump())
                
                # Verifica se há tool calls
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Executa a função
                        if self.type == AgentType.COORDINATOR:
                            # Coordinator usa delegação
                            result = await execute_coordinator_tool(function_name, function_args, agents_ref or {})
                        elif self.type == AgentType.DATA_ANALYST:
                            result = execute_sql_tool(function_name, function_args)
                        elif self.type == AgentType.FINANCIAL_EXPERT:
                            result = execute_financial_tool(function_name, function_args)
                        else:
                            result = "Tool execution not implemented"
                        
                        # Adiciona resultado ao histórico
                        self.message_history.append({
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    continue
                
                # Retorna resposta final
                return message.content
                
            except Exception as e:
                log_message("ERROR", f"Erro ao processar: {str(e)}", "agent")
                return f"❌ Erro: {str(e)}"
    
    def clear_history(self):
        """Limpa histórico de mensagens"""
        self.message_history = [{"role": "system", "content": self.system_prompt}]


# ==================== ORQUESTRAÇÃO ====================

# Storage global de agentes para delegação
agents_registry: Dict[str, Any] = {}

def create_delegation_tools() -> List[Dict]:
    """Cria tools de delegação para o Coordinator"""
    return [
        {
            "type": "function",
            "function": {
                "name": "delegate_to_data_analyst",
                "description": "Delega pergunta para o Analista de Dados quando precisa consultar SQL, listar tabelas, extrair dados ou fazer queries em banco de dados. Use quando a pergunta envolve: listar tabelas, contar registros, buscar dados, consultar SQL, ver estrutura de tabelas.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "A pergunta específica para o Analista de Dados"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delegate_to_financial_expert",
                "description": "Delega pergunta para o Especialista Financeiro quando precisa calcular métricas financeiras, avaliar riscos, analisar estratégias ou fazer valuation. Use quando a pergunta envolve: calcular ROI, Cap Rate, Cash-on-Cash, avaliar risco, diversificação, valuation, estratégias de investimento.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "A pergunta específica para o Especialista Financeiro"}
                    },
                    "required": ["query"]
                }
            }
        }
    ]

async def execute_coordinator_tool(tool_name: str, tool_input: Dict[str, Any], agents: Dict[str, Any]) -> str:
    """Executa tools de delegação do Coordinator"""
    try:
        if tool_name == "delegate_to_data_analyst":
            query = tool_input.get("query", "")
            log_message("DELEGATION", f"Coordinator → Data Analyst: {query}", "coordinator")
            result = await agents["data_analyst"].process(query)
            return result
            
        elif tool_name == "delegate_to_financial_expert":
            query = tool_input.get("query", "")
            log_message("DELEGATION", f"Coordinator → Financial Expert: {query}", "coordinator")
            result = await agents["financial_expert"].process(query)
            return result
        else:
            return f"Tool desconhecida: {tool_name}"
    except Exception as e:
        log_message("ERROR", f"Erro ao delegar: {str(e)}", "coordinator")
        return f"❌ Erro na delegação: {str(e)}"


# ==================== CRIAÇÃO DE AGENTES ====================

def create_agents():
    """Factory de agentes com prompts personalizáveis"""
    
    # Prompts podem ser customizados via arquivo externo
    coordinator = Agent(
        AgentType.COORDINATOR,
        "Gabi.",
        """Você é Gabi., uma assistente inteligente especializada em análise de carteiras imobiliárias e acesso a bases de dados.

Você é um Orquestrador Multi-Agente que coordena especialistas para fornecer as melhores análises.

FUNÇÃO PRINCIPAL:
Como orquestrador central, você deve:
1. Analisar a intenção do usuário automaticamente
2. Decidir dinamicamente qual agente especializado é mais apropriado
3. Coordenar múltiplos agentes quando a pergunta exigir diferentes expertises
4. Consolidar e apresentar respostas de forma clara e profissional
5. Gerenciar conexões MCP com bancos de dados (PostgreSQL e MS SQL Server)

AGENTES ESPECIALIZADOS DISPONÍVEIS:
- **Analista de Dados** (delegate_to_data_analyst):
  • Consultas SQL em PostgreSQL e MS SQL Server
  • Listagem de tabelas e schemas
  • Extração e análise de dados estruturados
  • Exploração de relacionamentos entre tabelas
  • Consultas ao histórico de chats persistidos

- **Especialista Financeiro** (delegate_to_financial_expert):
  • Cálculos de ROI, Cap Rate, Cash-on-Cash
  • Análise de risco de carteiras imobiliárias
  • Estratégias de diversificação de investimentos
  • Valuation e recomendações de investimento
  • Análise de performance financeira

DECISÃO DINÂMICA DE DELEGAÇÃO:
Você deve analisar automaticamente cada pergunta e decidir:
- Se menciona SQL, banco, tabelas, consulta, dados → delegate_to_data_analyst
- Se menciona ROI, risco, investimento, cálculos → delegate_to_financial_expert
- Se combina ambos → delegue sequencialmente para ambos os agentes

SISTEMAS DE BANCO DE DADOS:
- PostgreSQL (db-persist:5432) - Armazena histórico de chats e sessões
- MS SQL Server (mssql:1433) - Base REB_BI_IA com dados de negócio

IMPORTANTE: Sempre responda em português de forma profissional e objetiva.""",
        create_delegation_tools()  # Tools de delegação
    )
    
    financial_expert = Agent(
        AgentType.FINANCIAL_EXPERT,
        "Especialista Financeiro",
        f"""Você é um Especialista Financeiro com expertise em investimentos imobiliários.

EXPERTISE:
- ROI, Cap Rate, Cash-on-Cash
- Avaliação de risco
- Estratégias de diversificação
- Valuation

THRESHOLDS CONFIGURADOS:
- ROI Excelente: >{Config.ROI_EXCELLENT_THRESHOLD}%
- ROI Bom: >{Config.ROI_GOOD_THRESHOLD}%
- Cap Rate Excelente: >{Config.CAP_RATE_EXCELLENT_THRESHOLD}%

Forneça análises baseadas em dados concretos e recomendações acionáveis.""",
        FINANCIAL_TOOLS
    )
    
    data_analyst = Agent(
        AgentType.DATA_ANALYST,
        "Analista de Dados",
        f"""Você é um Analista de Dados especializado em SQL e carteiras imobiliárias.

LIMITE DE QUERY: {Config.QUERY_LIMIT} registros

Sempre:
1. Valide conexão antes de consultar
2. Use queries eficientes
3. Apresente dados estruturados
4. Identifique padrões relevantes""",
        SQL_TOOLS
    )
    
    return {
        "coordinator": coordinator,
        "financial_expert": financial_expert,
        "data_analyst": data_analyst
    }


# ==================== CHAINLIT HANDLERS ====================

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """Autenticação por senha - Chainlit v2+"""
    # Carregar credenciais do .env
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "123")
    
    if username == admin_username and password == admin_password:
        return cl.User(
            identifier=username, 
            metadata={"role": "admin", "provider": "credentials"}
        )
    
    log_message("WARNING", f"Tentativa de login falhou para: {username}", "auth")
    return None


# ==================== STARTERS ====================

@cl.set_starters
async def set_starters():
    """Starters customizados com conexões MCP automáticas"""
    emoji = "✅" if Config.INCLUDE_EMOJIS else ""

    return [
        cl.Starter(
            label="🔌 Conectar PostgreSQL (Chat DB)",
            message="Conectar ao banco PostgreSQL de persistência (db-persist:5432, database: chainlit, user: chainlit) e listar as tabelas disponíveis",
            icon="🔌",
        ),
        cl.Starter(
            label="📊 Conectar MS SQL Server",
            message="Conectar ao SQL Server (mssql:1433, database: REB_BI_IA, user: sa, senha: Str0ng!Passw0rd) e explorar o schema",
            icon="📊",
        ),
        cl.Starter(
            label="💾 Ver Histórico de Chats",
            message="Consultar o banco PostgreSQL e mostrar os últimos 10 chats salvos, incluindo quando foram criados e quantas mensagens cada um tem",
            icon="💾",
        ),
        cl.Starter(
            label="💰 Análise de ROI",
            message="Analise o ROI de um imóvel comprado por R$ 200.000, agora avaliado em R$ 250.000, comprado há 18 meses atrás",
            icon="💰",
        ),
        cl.Starter(
            label="📈 Cap Rate e Valuation",
            message="Calcule o Cap Rate de um imóvel que gera R$ 3.000/mês de renda líquida e foi adquirido por R$ 450.000. Avalie se é um bom investimento.",
            icon="📈",
        ),
        cl.Starter(
            label="🎯 Avaliação de Risco",
            message="Analise o risco de uma carteira imobiliária com 60% residencial, 30% comercial e 10% industrial. Considere localização geográfica e perfil de inquilinos.",
            icon="🎯",
        ),
    ]


# ==================== CHAT PROFILES ====================
# DESABILITADO: Sistema agora usa orquestrador dinâmico automático
# Os agentes são selecionados automaticamente pelo coordenador baseado no contexto


# ==================== MCP HANDLERS ====================

@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    """Handler MCP nativo - Discovery automático de tools"""
    try:
        # Listar ferramentas disponíveis
        result = await session.list_tools()
        
        # Processar metadados das tools
        tools = [{
            "name": t.name,
            "description": t.description,
            "input_schema": t.inputSchema,
        } for t in result.tools]
        
        # Armazenar tools para uso posterior
        mcp_tools = cl.user_session.get("mcp_tools", {})
        mcp_tools[connection.name] = tools
        cl.user_session.set("mcp_tools", mcp_tools)
        
        session_id = cl.user_session.get("id", "unknown")
        log_message("SUCCESS", f"MCP conectado: {connection.name} ({len(tools)} tools)", session_id)

        # Mensagem do arquivo JSON (editável sem rebuild!)
        titulo = Messages.get('mcp', 'conectado', 'titulo')
        mensagem = Messages.get('mcp', 'conectado', 'mensagem', connection_name=connection.name, tools_count=len(tools))
        await cl.Message(content=f"{titulo}\n{mensagem}").send()
        
    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro no MCP connect: {str(e)}", session_id)


@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session: ClientSession):
    """Handler MCP nativo - Cleanup ao desconectar"""
    try:
        # Remover tools da sessão
        mcp_tools = cl.user_session.get("mcp_tools", {})
        if name in mcp_tools:
            del mcp_tools[name]
            cl.user_session.set("mcp_tools", mcp_tools)
        
        session_id = cl.user_session.get("id", "unknown")
        log_message("INFO", f"MCP desconectado: {name}", session_id)

        # Mensagem do arquivo JSON (editável sem rebuild!)
        titulo = Messages.get('mcp', 'desconectado', 'titulo')
        mensagem = Messages.get('mcp', 'desconectado', 'mensagem', connection_name=name)
        await cl.Message(content=f"{titulo}: {mensagem}").send()
        
    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro no MCP disconnect: {str(e)}", session_id)


@cl.step(type="tool")
async def call_tool(tool_use):
    """Handler MCP nativo - Execução de tools"""
    tool_name = tool_use.name
    tool_input = tool_use.input
    
    try:
        # Obter sessões MCP ativas
        mcp_sessions = cl.context.session.mcp_sessions
        
        # Encontrar qual MCP connection possui esta tool
        mcp_name = None
        for name, (session, _) in mcp_sessions.items():
            tools = cl.user_session.get("mcp_tools", {}).get(name, [])
            if any(t["name"] == tool_name for t in tools):
                mcp_name = name
                break
        
        if not mcp_name:
            return {"error": f"Tool '{tool_name}' não encontrada em nenhuma connection MCP"}
        
        # Obter a sessão MCP
        mcp_session, _ = mcp_sessions.get(mcp_name)
        
        # Chamar a tool
        result = await mcp_session.call_tool(tool_name, tool_input)
        
        session_id = cl.user_session.get("id", "unknown")
        log_message("INFO", f"Tool {tool_name} executada via MCP {mcp_name}", session_id)
        
        return result
        
    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro ao executar tool {tool_name}: {str(e)}", session_id)
        return {"error": str(e)}


@cl.on_chat_resume
async def on_resume(thread):
    """Resume conversation com histórico persistido - Chainlit v2+"""
    # Chainlit automaticamente restaura:
    # - Todas as mensagens anteriores
    # - Elementos anexados
    # - User session (campos JSON-serializáveis)
    
    # Recriar agentes (não serializáveis, precisam ser recriados)
    agents = create_agents()
    cl.user_session.set("agents", agents)
    
    # Restaurar conversation_count se existir no user_session
    # (persistido automaticamente se for JSON-serializável)
    
    app_user = cl.user_session.get("user")
    user_name = app_user.identifier if app_user else "Usuário"
    
    # Restaurar perfil selecionado
    selected_profile = cl.user_session.get("chat_profile", "Completo")
    
    thread_name = thread.get("name", "Conversação anterior")
    log_message("INFO", f"Conversação retomada para {user_name}: {thread_name} (Perfil: {selected_profile})", app_user.identifier if app_user else "unknown")

    # Mensagem do arquivo JSON (editável sem rebuild!)
    titulo = Messages.get('chat_retomado', 'titulo')
    mensagem = Messages.get('chat_retomado', 'mensagem')
    await cl.Message(content=f"{titulo}\n{mensagem}").send()


@cl.on_chat_start
async def start():
    """Inicializa novo chat"""
    agents = create_agents()
    cl.user_session.set("agents", agents)
    cl.user_session.set("conversation_count", 0)
    
    session_id = cl.user_session.get("id")
    app_user = cl.user_session.get("user")
    user_name = app_user.identifier if app_user else "Usuário"
    
    # Obter perfil selecionado
    selected_profile = cl.user_session.get("chat_profile", "Completo")
    
    log_message("INFO", f"Nova sessão iniciada para {user_name} - Perfil: {selected_profile}", session_id)
    
    emoji_prefix = "🏢 " if Config.INCLUDE_EMOJIS else ""
    
    # Mensagens customizadas por perfil
    profile_messages = {
        "👔 Financeiro": """
Você está usando o perfil **Financeiro**.
Focado em análise de ROI, Cap Rate, avaliação de risco e estratégias de investimento.""",
        "📊 Dados": """
Você está usando o perfil **Dados**.
Especializado em consultas SQL, relatórios e extração de insights.""",
        "🎯 Completo": """
Você está usando o perfil **Completo**.
Acesso total aos especialistas Financeiro e Dados."""
    }
    
    profile_msg = profile_messages.get(selected_profile, "")
    
    # Criar Actions simplificadas para usuário final
    btn_config = Messages.get('botoes', 'conectar_banco')
    actions = [
        cl.Action(
            name="conectar_default_mssql",
            payload={"action": "conectar_default_mssql"},
            label=btn_config.get('label', '🔌 Conectar Banco de Dados'),
            description=btn_config.get('descricao', 'Conecta ao banco principal')
        )
    ]

    # Mensagem de boas-vindas do arquivo JSON (editável sem rebuild!)
    saudacao = Messages.get('boas_vindas', 'saudacao', username=user_name)
    descricao = Messages.get('boas_vindas', 'descricao')
    titulo_opcoes = Messages.get('boas_vindas', 'titulo_opcoes')
    opcoes = Messages.get('boas_vindas', 'opcoes')

    # Montar mensagem
    welcome_msg = f"""{saudacao}

{descricao}

**{titulo_opcoes}**"""

    # Adicionar opções
    for opcao in opcoes:
        welcome_msg += f"\n• {opcao}"
    
    await cl.Message(content=welcome_msg, actions=actions).send()


@cl.on_message
async def main(message: cl.Message):
    """Processa mensagens com orquestrador dinâmico automático"""
    agents = cl.user_session.get("agents")
    session_id = cl.user_session.get("id")
    count = cl.user_session.get("conversation_count", 0) + 1
    cl.user_session.set("conversation_count", count)

    log_message("USER_MESSAGE", message.content, session_id)

    # Mensagem de "processando" do arquivo JSON
    msg_analisando = Messages.get('mensagens_sistema', 'analisando')
    msg = await cl.Message(content=msg_analisando).send()

    try:
        content_lower = message.content.lower()

        # AUTO-CONECTAR MCP SE NECESSÁRIO
        data_keywords_for_auto_connect = ["query", "sql", "tabela", "conecta", "banco",
                                          "database", "lista", "mostra", "extrai",
                                          "schema", "consulta", "quantos", "postgres", "mssql"]
        if any(kw in content_lower for kw in data_keywords_for_auto_connect):
            # Tentar auto-conectar se não estiver conectado
            mcp_tools = cl.user_session.get("mcp_tools", {})
            if not mcp_tools:
                auto_connected = await auto_connect_mssql_mcp()
                if auto_connected:
                    # Mensagem do arquivo JSON (editável sem rebuild!)
                    msg_auto_conectado = Messages.get('mcp', 'auto_conectado', 'mensagem')
                    await cl.Message(content=msg_auto_conectado).send()

        # ORQUESTRADOR DINÂMICO
        # Sempre usa o Coordinator que decide automaticamente qual agente usar
        # baseado no contexto da mensagem via OpenAI Function Calling
        agent = agents["coordinator"]
        emoji = "🎯" if Config.INCLUDE_EMOJIS else ""

        # Processa com o coordenador (orquestrador)
        # O Coordinator automaticamente delega para o agente apropriado
        response = await agent.process(message.content, agents_ref=agents)

        # Formata resposta
        formatted_response = f"{emoji} **{agent.name}**\n\n{response}"
        msg.content = formatted_response
        await msg.update()

        log_message("AGENT_RESPONSE", f"Coordinator (orchestrator), Length: {len(response)}", session_id)

    except Exception as e:
        # Mensagem de erro do arquivo JSON
        msg_erro = Messages.get('mensagens_sistema', 'erro_generico')
        error_msg = f"{msg_erro}\n\nDetalhes: {str(e)}"
        msg.content = error_msg
        await msg.update()
        log_message("ERROR", str(e), session_id)


@cl.on_chat_end
async def end():
    """Limpa recursos ao encerrar"""
    session_id = cl.user_session.get("id")
    log_message("INFO", "Sessão encerrada", session_id)
    
    if session_id in connections_store:
        for conn_info in connections_store[session_id]["connections"].values():
            try:
                conn_info["connection"].close()
            except:
                pass
        del connections_store[session_id]


# ==================== ACTION CALLBACKS ====================

async def auto_connect_mssql_mcp():
    """Tenta conectar ao MCP MSSQL automaticamente se houver credenciais no .env"""
    try:
        # Verificar se MCP já está conectado
        mcp_tools = cl.user_session.get("mcp_tools", {})
        if mcp_tools:
            return True  # Já conectado
        
        # Verificar se há credenciais SQL configuradas
        if not Config.MSSQL_SERVER or Config.MSSQL_SERVER == "localhost":
            return False  # Sem configuração
        
        # Tentar obter sessão MCP ativa
        mcp_sessions = cl.context.session.mcp_sessions
        if not mcp_sessions:
            return False  # MCP não configurado na sidebar
        
        # Procurar sessão SQL Server
        for name, (session, _) in mcp_sessions.items():
            if "sql" in name.lower() or "mssql" in name.lower():
                # Tentar conectar ao database se tiver credenciais completas
                if Config.MSSQL_DATABASE:
                    connection_params = {
                        "server": Config.MSSQL_SERVER,
                        "database": Config.MSSQL_DATABASE,
                        "username": Config.MSSQL_USERNAME,
                        "password": Config.MSSQL_PASSWORD,
                        "port": Config.DEFAULT_DB_PORT
                    }
                    
                    # Chamar connect_database via MCP
                    result = await session.call_tool("connect_database", connection_params)
                    
                    session_id = cl.user_session.get("id", "unknown")
                    log_message("SUCCESS", f"Auto-conectado ao MCP SQL: {name}", session_id)
                    return True
        
        return False
        
    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro ao auto-conectar MCP: {str(e)}", session_id)
        return False


@cl.action_callback("conectar_mcp_mssql")
async def on_conectar_mcp_mssql(action):
    """Callback para Action de conexão MCP"""
    
    # Tentar auto-conectar primeiro
    auto_connected = await auto_connect_mssql_mcp()
    
    if auto_connected:
        success_msg = """✅ **Conexão MCP Automática Bem-Sucedida!**

O sistema conectou automaticamente ao SQL Server usando as credenciais configuradas.

📋 **Ferramentas disponíveis:**
- `get_database_schema` - Ver estrutura completa
- `execute_query` - Executar SELECT seguro
- `analyze_relationships` - Ver JOINs sugeridos
- `preview_table` - Ver primeiras linhas
- `search_data` - Buscar em colunas de texto

💡 **Agora você pode fazer perguntas sobre os dados diretamente!**
Exemplo: "Quantas tabelas existem no banco?" ou "Liste os imóveis disponíveis"."""
        
        await cl.Message(content=success_msg).send()
        await action.remove()
        return
    
    # Se auto-connect falhou, mostrar instruções manuais
    instruction_msg = """🔌 **Como Conectar ao SQL Server via MCP**

**Passo 1:** Abra a barra lateral e clique em **"My MCPs"**

**Passo 2:** Clique em **"Add MCP"** ou **"+"**

**Passo 3:** Configure:
- **Connection name:** `sql-server`
- **Client type:** `stdio`
- **Command:** `python mcp_sqlserver_stdio.py`

**Passo 4:** Clique em **"Connect"**

**Passo 5:** Quando solicitado, use a ferramenta `connect_database` com suas credenciais:
```json
{
  "server": "localhost",
  "database": "seu_banco",
  "username": "sa",
  "password": "SuaSenha123",
  "port": 1433
}
```

✅ **Pronto!** O sistema descobrirá automaticamente todas as tabelas, colunas e relacionamentos.

📋 **Ferramentas disponíveis após conexão:**
- `get_database_schema` - Ver estrutura completa
- `execute_query` - Executar SELECT seguro
- `analyze_relationships` - Ver JOINs sugeridos
- `preview_table` - Ver primeiras linhas
- `search_data` - Buscar em colunas de texto

💡 **Dica:** O LLM usará essas ferramentas automaticamente quando você fizer perguntas sobre os dados!"""
    
    await cl.Message(content=instruction_msg).send()
    await action.remove()


@cl.action_callback("conectar_mcp_automatico")
async def on_conectar_mcp_automatico(action):
    """Callback para Action de conexão automática"""
    try:
        # Obter sessões MCP ativas
        mcp_sessions = cl.context.session.mcp_sessions
        if not mcp_sessions:
            # Mensagem do arquivo JSON (editável sem rebuild!)
            msg_erro = Messages.get('mcp', 'erros', 'nao_configurado')
            await cl.Message(content=msg_erro).send()
            await action.remove()
            return
        
        # Procurar sessão SQL Server
        session = None
        for name, (s, _) in mcp_sessions.items():
            if "sql" in name.lower() or "mssql" in name.lower():
                session = s
                break
        
        if not session:
            # Mensagem do arquivo JSON (editável sem rebuild!)
            msg_erro = Messages.get('mcp', 'erros', 'sessao_nao_encontrada')
            await cl.Message(content=msg_erro).send()
            await action.remove()
            return
        
        # Parâmetros de conexão com servidor correto (mssql ao invés de localhost)
        connection_params = {
            "server": "mssql",  # Nome do serviço Docker
            "database": "REB_BI_IA",
            "username": "sa",
            "password": "Str0ng!Passw0rd",
            "port": 1433
        }
        
        # Mostrar mensagem de processamento (do arquivo JSON - editável sem rebuild!)
        msg_conectando = Messages.get('mensagens_sistema', 'conectando')
        msg = await cl.Message(content=msg_conectando).send()
        
        # Chamar connect_database via MCP
        result = await session.call_tool("connect_database", connection_params)
        
        # Atualizar mensagem com sucesso
        success_msg = f"""✅ **Conexão bem-sucedida!**

{result.get('message', 'Conectado ao REB_BI_IA')}
• {result.get('tables_discovered', 0)} tabelas descobertas

📋 **Agora você pode:**
• Listar tabelas do banco
• Consultar dados
• Analisar relacionamentos
• Fazer queries SQL

💡 **Exemplo:** "Quantas tabelas existem no banco?" ou "Liste os dados da tabela REBr_AgingDiario"."""
        
        msg.content = success_msg
        await msg.update()
        await action.remove()
        
    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro ao conectar via action: {str(e)}", session_id)
        # Mensagem do arquivo JSON (editável sem rebuild!)
        msg_erro = Messages.get('mcp', 'erros', 'erro_conectar', erro_detalhes=str(e))
        await cl.Message(content=msg_erro).send()
        await action.remove()


@cl.action_callback("exemplo_consulta_mcp")
async def on_exemplo_consulta_mcp(action):
    """Callback para Action de exemplo de consulta"""
    example_msg = """📊 **Exemplo Prático de Uso com MCP**

Após conectar ao SQL Server via MCP, você pode fazer perguntas em português natural:

**Exemplo 1 - Consulta Simples:**
*"Quantos imóveis existem na tabela Properties?"*

**Exemplo 2 - Análise Exploratória:**
*"Mostre as primeiras 10 propriedades da tabela Properties"*

**Exemplo 3 - Schema Discovery:**
*"Quais tabelas existem no banco de dados?"*

**Exemplo 4 - Relacionamentos:**
*"Quais são as foreign keys da tabela Transactions?"*

**Exemplo 5 - Query Complexa:**
*"Quais são os 5 imóveis mais caros por m²?"*

**Exemplo 6 - Busca de Dados:**
*"Busque imóveis na zona sul do Rio de Janeiro"*

---

🤖 **Como Funciona:**
1. Você faz uma pergunta em português
2. O LLM interpreta e decide qual ferramenta usar
3. A ferramenta é executada automaticamente
4. Os resultados são retornados e apresentados de forma clara

🔒 **Segurança:**
- Apenas queries SELECT são permitidas
- Comandos DML (INSERT, UPDATE, DELETE) são bloqueados
- Admin commands (DROP, EXEC) são bloqueados
- Limite padrão de 100 resultados

💡 **Dica:** Seja específico nas perguntas para obter melhores resultados!"""
    
    await cl.Message(content=example_msg).send()
    await action.remove()


# ==================== CONEXÃO DEFAULT ====================

async def connect_to_default_mssql():
    """Conecta ao banco MS SQL Server configurado como default no .env"""
    try:
        if not Config.MSSQL_DEFAULT_ENABLED:
            return False, "Conexão default MSSQL desabilitada no .env"

        # Obter sessões MCP ativas
        mcp_sessions = cl.context.session.mcp_sessions
        if not mcp_sessions:
            return False, "MCP não configurado"

        # Procurar sessão MSSQL
        session = None
        for name, (s, _) in mcp_sessions.items():
            if "mssql" in name.lower() or "sql" in name.lower():
                session = s
                break

        if not session:
            return False, "Sessão MCP MSSQL não encontrada"

        # Parâmetros de conexão do default
        connection_params = {
            "server": Config.MSSQL_DEFAULT_SERVER,
            "database": Config.MSSQL_DEFAULT_DATABASE,
            "username": Config.MSSQL_DEFAULT_USERNAME,
            "password": Config.MSSQL_DEFAULT_PASSWORD,
            "port": Config.MSSQL_DEFAULT_PORT
        }

        # Conectar
        result = await session.call_tool("connect_database", connection_params)

        # Processar resultado
        if isinstance(result, list) and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result_data = json.loads(content) if isinstance(content, str) else content

            if result_data.get("success"):
                tables_count = result_data.get("tables_discovered", 0)
                return True, f"Conectado a {Config.MSSQL_DEFAULT_SERVER}/{Config.MSSQL_DEFAULT_DATABASE} ({tables_count} tabelas)"

        return False, "Erro ao processar resposta da conexão"

    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro ao conectar MSSQL default: {str(e)}", session_id)
        return False, f"Erro: {str(e)}"


async def connect_to_default_postgres():
    """Conecta ao banco PostgreSQL configurado como default no .env"""
    try:
        if not Config.POSTGRES_DEFAULT_ENABLED:
            return False, "Conexão default PostgreSQL desabilitada no .env"

        # Obter sessões MCP ativas
        mcp_sessions = cl.context.session.mcp_sessions
        if not mcp_sessions:
            return False, "MCP não configurado"

        # Procurar sessão PostgreSQL
        session = None
        for name, (s, _) in mcp_sessions.items():
            if "postgres" in name.lower() or "pg" in name.lower():
                session = s
                break

        if not session:
            return False, "Sessão MCP PostgreSQL não encontrada"

        # Parâmetros de conexão do default
        connection_params = {
            "host": Config.POSTGRES_DEFAULT_HOST,
            "database": Config.POSTGRES_DEFAULT_DATABASE,
            "user": Config.POSTGRES_DEFAULT_USERNAME,
            "password": Config.POSTGRES_DEFAULT_PASSWORD,
            "port": Config.POSTGRES_DEFAULT_PORT
        }

        # Conectar
        result = await session.call_tool("connect_database", connection_params)

        # Processar resultado
        if isinstance(result, list) and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            result_data = json.loads(content) if isinstance(content, str) else content

            if result_data.get("success"):
                tables_count = result_data.get("tables_discovered", 0)
                return True, f"Conectado a {Config.POSTGRES_DEFAULT_HOST}/{Config.POSTGRES_DEFAULT_DATABASE} ({tables_count} tabelas)"

        return False, "Erro ao processar resposta da conexão"

    except Exception as e:
        session_id = cl.user_session.get("id", "unknown")
        log_message("ERROR", f"Erro ao conectar PostgreSQL default: {str(e)}", session_id)
        return False, f"Erro: {str(e)}"


@cl.action_callback("conectar_default_mssql")
async def on_conectar_default_mssql(action):
    """Conecta ao banco MSSQL configurado como default"""
    msg_conectando = Messages.get('mensagens_sistema', 'conectando')
    msg = await cl.Message(content=msg_conectando).send()

    success, message = await connect_to_default_mssql()

    if success:
        # Mensagem de sucesso do arquivo JSON (editável!)
        titulo = Messages.get('conexao_sucesso', 'titulo')
        agora_pode = Messages.get('conexao_sucesso', 'agora_pode')
        opcoes = Messages.get('conexao_sucesso', 'opcoes')

        success_msg = f"""{titulo}

{message}

**{agora_pode}**"""

        # Adicionar opções
        for opcao in opcoes:
            success_msg += f"\n• {opcao}"

        msg.content = success_msg
    else:
        # Mensagem de erro do arquivo JSON (editável!)
        titulo_erro = Messages.get('conexao_erro', 'titulo')
        como_resolver = Messages.get('conexao_erro', 'como_resolver')
        passos = Messages.get('conexao_erro', 'passos')

        error_msg = f"""{titulo_erro}

{message}

**{como_resolver}**"""

        # Adicionar passos
        for i, passo in enumerate(passos, 1):
            error_msg += f"\n{i}. {passo}"

        msg.content = error_msg

    await msg.update()
    await action.remove()


@cl.action_callback("conectar_default_postgres")
async def on_conectar_default_postgres(action):
    """Conecta ao banco PostgreSQL configurado como default"""
    # Mensagem do arquivo JSON (editável sem rebuild!)
    msg_conectando = Messages.get('postgresql', 'conectando')
    msg = await cl.Message(content=msg_conectando).send()

    success, message = await connect_to_default_postgres()

    if success:
        # Mensagem de sucesso do arquivo JSON (editável sem rebuild!)
        titulo = Messages.get('postgresql', 'conectado', 'titulo')
        agora_pode = Messages.get('postgresql', 'conectado', 'agora_pode')
        opcoes = Messages.get('postgresql', 'conectado', 'opcoes')

        success_msg = f"""{titulo}

{message}

**{agora_pode}**"""

        # Adicionar opções
        for opcao in opcoes:
            success_msg += f"\n• {opcao}"

        msg.content = success_msg
    else:
        # Mensagem de erro do arquivo JSON (editável sem rebuild!)
        titulo_erro = Messages.get('postgresql', 'erro', 'titulo')
        como_resolver = Messages.get('postgresql', 'erro', 'como_resolver')
        passos = Messages.get('postgresql', 'erro', 'passos')

        error_msg = f"""{titulo_erro}

{message}

**{como_resolver}**"""

        # Adicionar passos
        for i, passo in enumerate(passos, 1):
            error_msg += f"\n{i}. {passo}"

        msg.content = error_msg

    await msg.update()
    await action.remove()


@cl.action_callback("help_mcp")
async def on_help_mcp(action):
    """Mostra tutorial completo sobre MCP"""
    help_msg = """# 📚 Help: Conexão via MCP (Model Context Protocol)

## 🎯 O que é MCP?

**MCP (Model Context Protocol)** é um protocolo que permite que Gabi. se conecte diretamente a bancos de dados e execute operações de forma segura e automática.

---

## 🔌 Bancos Disponíveis

### 1️⃣ **MS SQL Server**
**Propósito:** Dados de negócio (imóveis, análises, etc.)
**Servidor Default:** `{mssql_server}:{mssql_port}`
**Database Default:** `{mssql_db}`

### 2️⃣ **PostgreSQL**
**Propósito:** Histórico de conversas e persistência do Chainlit
**Host Default:** `{pg_host}:{pg_port}`
**Database Default:** `{pg_db}`

---

## 🚀 Como Conectar (3 Formas)

### **Forma 1: Botão "Conectar Banco Default"** ⭐ RECOMENDADO
1. Clique no botão "🔌 Conectar MSSQL Default" ou "🔌 Conectar PostgreSQL Default"
2. Pronto! Conectado automaticamente

**Vantagem:** Mais rápido e fácil!

### **Forma 2: Starter Pré-Configurado**
1. Clique em um dos starters:
   - 🔌 Conectar PostgreSQL (Chat DB)
   - 📊 Conectar MS SQL Server
2. Gabi. conectará automaticamente

### **Forma 3: Pergunta Direta**
Digite: *"Conectar ao banco PostgreSQL de persistência"*
Gabi. entenderá e conectará automaticamente!

---

## 🔧 Configurar Banco Default

Os bancos default são configurados no arquivo `.env`:

### **MS SQL Server Default:**
```bash
MSSQL_DEFAULT_ENABLED=true
MSSQL_DEFAULT_SERVER=mssql        # Altere para seu servidor
MSSQL_DEFAULT_PORT=1433
MSSQL_DEFAULT_DATABASE=REB_BI_IA  # Altere para sua database
MSSQL_DEFAULT_USERNAME=sa
MSSQL_DEFAULT_PASSWORD=sua-senha  # Altere a senha
```

### **PostgreSQL Default:**
```bash
POSTGRES_DEFAULT_ENABLED=true
POSTGRES_DEFAULT_HOST=db-persist   # Altere para seu host
POSTGRES_DEFAULT_PORT=5432
POSTGRES_DEFAULT_DATABASE=chainlit # Altere para sua database
POSTGRES_DEFAULT_USERNAME=chainlit
POSTGRES_DEFAULT_PASSWORD=sua-senha  # Altere a senha
```

**Após editar:** Reinicie a aplicação com `docker-compose restart app-agent`

---

## 💡 Exemplos de Uso

### **Após conectar ao MSSQL:**
```
"Quais tabelas existem no banco?"
"Mostre as primeiras 10 linhas da tabela Properties"
"Quantos imóveis temos cadastrados?"
"Liste imóveis com valor acima de R$ 500.000"
"Qual a estrutura da tabela Transactions?"
```

### **Após conectar ao PostgreSQL:**
```
"Mostre meus últimos 10 chats"
"Quantas mensagens enviei hoje?"
"Quais tabelas o Chainlit usa?"
"Liste todas as threads (conversas) salvas"
```

---

## 🛡️ Segurança

✅ **Permitido:**
- SELECT (consultas)
- Schema discovery
- Preview de tabelas

❌ **Bloqueado:**
- INSERT, UPDATE, DELETE
- DROP, TRUNCATE, ALTER
- EXEC, xp_cmdshell
- Qualquer comando destrutivo

**Limite:** 100 resultados por query (configurável em `.env`)

---

## 🔍 Ferramentas MCP Disponíveis

Após conectar, você tem acesso a 6 ferramentas automáticas:

| Ferramenta | Descrição |
|-----------|-----------|
| `connect_database` | Conecta e descobre schema |
| `get_database_schema` | Retorna metadados completos |
| `execute_query` | Executa SELECT seguro |
| `analyze_relationships` | Analisa FKs e sugere JOINs |
| `preview_table` | Mostra primeiras linhas |
| `search_data` | Busca em colunas de texto |

**Você não precisa chamar essas ferramentas!** Gabi. as usa automaticamente quando você faz perguntas.

---

## 🆘 Troubleshooting

### **Erro: "MCP não configurado"**
**Solução:** O MCP está configurado automaticamente no Docker. Se ver este erro:
1. Verifique se `.chainlit/config.toml` tem a seção `[mcp]`
2. Reinicie: `docker-compose restart app-agent`

### **Erro: "Sessão MCP não encontrada"**
**Solução:**
1. Verifique os logs: `docker-compose logs app-agent`
2. Certifique-se que o container está rodando: `docker-compose ps`

### **Erro: "Falha ao conectar ao banco"**
**Solução:**
1. Verifique as credenciais no `.env`
2. Teste conexão manual:
   ```bash
   # MSSQL
   docker exec -it chatrebrasil-mssql-1 /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'sua-senha' -C

   # PostgreSQL
   docker exec -it chatrebrasil-db-persist-1 psql -U chainlit -d chainlit
   ```
3. Veja se os containers estão rodando: `docker-compose ps`

### **Como desabilitar banco default?**
No `.env`, altere:
```bash
MSSQL_DEFAULT_ENABLED=false
POSTGRES_DEFAULT_ENABLED=false
```

---

## 📖 Documentação Completa

Para mais detalhes, consulte:
- `PERSISTENCIA_E_BARRA_LATERAL.md` - Sobre PostgreSQL e persistência
- `MCP_SETUP.md` - Setup avançado de MCP
- `MELHORIAS_IMPLEMENTADAS.md` - Todas as features

---

**Dúvidas?** Pergunte diretamente: *"Como faço para X?"*

Gabi. está aqui para ajudar! 🤖""".format(
        mssql_server=Config.MSSQL_DEFAULT_SERVER,
        mssql_port=Config.MSSQL_DEFAULT_PORT,
        mssql_db=Config.MSSQL_DEFAULT_DATABASE,
        pg_host=Config.POSTGRES_DEFAULT_HOST,
        pg_port=Config.POSTGRES_DEFAULT_PORT,
        pg_db=Config.POSTGRES_DEFAULT_DATABASE
    )

    await cl.Message(content=help_msg).send()
    await action.remove()


# ==================== INICIALIZAÇÃO ====================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════╗
    ║   Sistema Multi-Agente - Carteira Imobiliária     ║
    ║                                                    ║
    ║   Desenvolvido por ness.                          ║
    ║                                                    ║
    ║   Execute: chainlit run app.py -w                 ║
    ║   Acesse: http://localhost:8000                   ║
    ╚════════════════════════════════════════════════════╝
    """)
