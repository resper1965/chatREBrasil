"""
Exemplo Standalone - SQL Server + OpenAI sem MCP

Teste rápido via terminal sem Chainlit
"""

import pyodbc
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()


# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY não configurada no .env")
    exit(1)


# Configurações MSSQL
SERVER = os.getenv("MSSQL_SERVER", "localhost")
DATABASE = os.getenv("MSSQL_DATABASE")
USERNAME = os.getenv("MSSQL_USERNAME", "sa")
PASSWORD = os.getenv("MSSQL_SA_PASSWORD", "Str0ng!Passw0rd")
PORT = int(os.getenv("DB_PORT", "1433"))


class SimpleSQLAgent:
    """Agente SQL simplificado para testes"""
    
    def __init__(self):
        self.connection = None
        self.tables = []
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def connect(self):
        """Conecta ao SQL Server"""
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={SERVER},{PORT};"
                f"DATABASE={DATABASE};"
                f"UID={USERNAME};"
                f"PWD={PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
            
            print(f"🔗 Conectando a {SERVER}/{DATABASE}...")
            self.connection = pyodbc.connect(conn_str, timeout=30)
            
            # Descobrir tabelas
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                  AND TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            
            self.tables = [f"{row[0]}.{row[1]}" for row in cursor.fetchall()]
            
            print(f"✅ Conectado! {len(self.tables)} tabelas descobertas.")
            for table in self.tables[:5]:
                print(f"   • {table}")
            if len(self.tables) > 5:
                print(f"   ... e mais {len(self.tables) - 5}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def get_tools(self):
        """Retorna ferramentas disponíveis"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_sql_query",
                    "description": "Executa query SQL SELECT",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_table_info",
                    "description": "Obtém estrutura de uma tabela",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string"}
                        },
                        "required": ["table_name"]
                    }
                }
            }
        ]
    
    def execute_sql_query(self, query: str):
        """Executa query SQL"""
        if not self.connection:
            return {"error": "Não conectado"}
        
        try:
            if not query.strip().upper().startswith("SELECT"):
                return {"error": "Apenas SELECT permitido"}
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(100)
            
            return {
                "columns": columns,
                "rows": [dict(zip(columns, row)) for row in rows],
                "count": len(rows)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_table_info(self, table_name: str):
        """Obtém informação de uma tabela"""
        if table_name not in self.tables:
            return {"error": f"Tabela '{table_name}' não encontrada"}
        
        try:
            schema, name = table_name.split(".")
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
            """, schema, name)
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2]
                })
            
            return {"table": table_name, "columns": columns}
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self):
        """Loop de chat"""
        print("\n" + "="*60)
        print("💬 Agente SQL Simples - Digite 'sair' para encerrar")
        print("="*60 + "\n")
        
        messages = [
            {
                "role": "system",
                "content": f"""Você é um assistente especializado em análise de dados SQL Server.

TABELAS DISPONÍVEIS: {', '.join(self.tables)}

Você pode:
- Executar queries SQL SELECT
- Descrever estruturas de tabelas
- Analisar dados e gerar insights

Sempre responda em português de forma clara e útil."""
            }
        ]
        
        while True:
            user_input = input("\n👤 Você: ").strip()
            
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\n👋 Até logo!")
                break
            
            if not user_input:
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            try:
                # Chamada OpenAI
                response = self.client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=self.get_tools(),
                    tool_choice="auto"
                )
                
                message = response.choices[0].message
                messages.append(message.model_dump())
                
                # Processar tool calls
                while message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        print(f"🔧 Executando: {function_name}")
                        
                        if function_name == "execute_sql_query":
                            result = self.execute_sql_query(function_args["query"])
                        elif function_name == "get_table_info":
                            result = self.get_table_info(function_args["table_name"])
                        else:
                            result = {"error": "Tool não implementada"}
                        
                        print(f"📊 Resultado: {json.dumps(result, indent=2, default=str)[:200]}...")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(result, default=str)
                        })
                    
                    # Nova chamada com resultados
                    response = self.client.chat.completions.create(
                        model=MODEL,
                        messages=messages,
                        tools=self.get_tools()
                    )
                    message = response.choices[0].message
                    messages.append(message.model_dump())
                
                # Resposta final
                print(f"\n🤖 Assistente: {message.content}")
                
            except Exception as e:
                print(f"❌ Erro: {e}")


def main():
    """Função principal"""
    print("🔧 Exemplo Standalone - SQL Agent\n")
    
    if not DATABASE:
        print("⚠️ MSSQL_DATABASE não configurado no .env")
        print("Configurando para 'master' (banco padrão)...")
        database_to_use = "master"
    else:
        database_to_use = DATABASE
    
    agent = SimpleSQLAgent()
    
    # Sobrescrever DATABASE temporariamente
    import sql_agent_openai.example_connection as mod
    mod.DATABASE = database_to_use
    
    if agent.connect():
        agent.chat()
        agent.connection.close()
        print("\n✅ Conexão encerrada.")


if __name__ == "__main__":
    main()





