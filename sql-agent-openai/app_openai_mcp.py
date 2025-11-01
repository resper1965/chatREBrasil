"""
Chainlit App - Agente SQL Server com OpenAI GPT-4 + MCP

Interface conversacional para análise de dados SQL Server
usando OpenAI Function Calling com ferramentas MCP.
"""

import chainlit as cl
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from typing import Dict, List, Any, Optional
from mcp_sqlserver import MCP_TOOLS, mcp_server, execute_mcp_tool

load_dotenv()


# Configurações
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não configurada no .env")


# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


@cl.on_chat_start
async def start():
    """Inicializa novo chat"""
    
    # Conectar MSSQL automaticamente se configurado
    mssql_server = os.getenv("MSSQL_SERVER")
    mssql_database = os.getenv("MSSQL_DATABASE")
    mssql_username = os.getenv("MSSQL_USERNAME", "sa")
    mssql_password = os.getenv("MSSQL_SA_PASSWORD", "Str0ng!Passw0rd")
    db_port = int(os.getenv("DB_PORT", "1433"))
    
    db_status = ""
    if mssql_database:
        try:
            result = execute_mcp_tool("connect_database", {
                "server": mssql_server or "localhost",
                "database": mssql_database,
                "username": mssql_username,
                "password": mssql_password,
                "port": db_port
            })
            
            if result.get("success"):
                tables_count = result.get("tables_discovered", 0)
                db_status = f"\n✅ **MSSQL Conectado:** {mssql_server}/{mssql_database} ({tables_count} tabelas)"
            else:
                db_status = f"\n⚠️ **Erro na conexão:** {result.get('error')}"
        except Exception as e:
            db_status = f"\n⚠️ **Erro:** {str(e)}"
    else:
        db_status = "\n💡 Configure MSSQL_DATABASE no .env para auto-conectar"
    
    # Armazenar histórico de conversa
    cl.user_session.set("history", [])
    
    # Mensagem de boas-vindas
    welcome_msg = f"""# 🔍 Agente SQL Server com GPT-4 + MCP

Olá! Sou um agente inteligente que ajuda você a analisar dados SQL Server através de **conversação natural**.

## 🎯 Capacidades

📊 **Descoberta Automática de Schema**
- Tabelas, colunas, tipos de dados
- Primary Keys e Foreign Keys
- Relacionamentos entre tabelas

🔍 **Análise Inteligente**
- Queries SQL geradas automaticamente
- JOINs sugeridos automaticamente
- Busca em dados textuais

🔒 **Execução Segura**
- Apenas SELECT permitido
- Validação de segurança
- Timeout de 30s

## ⚙️ Configuração Atual

• **Model:** {MODEL}
• **Portas:** 
  - Chainlit: 8000 (local)
  - MSSQL: {db_port}
{db_status}

## 📝 Exemplos de Perguntas

• *"Conecta ao meu banco localhost, RealEstateDB, user sa"*
• *"Lista todas as tabelas disponíveis"*
• *"Qual o total de propriedades?"*
• *"Mostre as 10 propriedades mais caras"*
• *"Analisa os relacionamentos entre as tabelas"*
• *"Busca por 'São Paulo' em todas as tabelas"*

**Pronto para ajudar!** Digite sua pergunta. 🚀
"""
    
    await cl.Message(content=welcome_msg).send()


@cl.on_message
async def main(message: cl.Message):
    """Processa mensagens com OpenAI Function Calling"""
    
    # Obter histórico
    history = cl.user_session.get("history", [])
    
    # Adicionar mensagem do usuário
    history.append({
        "role": "user",
        "content": message.content
    })
    
    # Indicador de processamento
    response_msg = await cl.Message(content="🤔 Analisando...").send()
    
    try:
        # Loop de function calling
        while True:
            # Chamada OpenAI
            response = client.chat.completions.create(
                model=MODEL,
                messages=history,
                tools=MCP_TOOLS if MCP_TOOLS else None,
                tool_choice="auto",
                temperature=0.7
            )
            
            message_response = response.choices[0].message
            history.append(message_response.model_dump())
            
            # Se não há tool calls, retornar resposta final
            if not message_response.tool_calls:
                final_response = message_response.content
                break
            
            # Executar cada tool call
            tool_results = []
            for tool_call in message_response.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except:
                    function_args = {}
                
                # Mostrar execução da tool
                step = await cl.Step(
                    name=function_name,
                    type="tool",
                    parent_id=response_msg.id
                )
                
                # Executar tool via MCP
                result = execute_mcp_tool(function_name, function_args)
                
                # Formatar resultado
                if isinstance(result, dict):
                    result_str = json.dumps(result, indent=2, ensure_ascii=False, default=str)
                else:
                    result_str = str(result)
                
                # Se sucesso, extrair informações importantes
                if function_name == "connect_database" and result.get("success"):
                    tables_count = result.get("tables_discovered", 0)
                    result_str = f"✅ {result['message']}\n📊 Tabelas descobertas: {tables_count}"
                elif function_name == "execute_query" and result.get("success"):
                    rows_count = result.get("count", 0)
                    columns = result.get("columns", [])
                    result_str = f"✅ Query executada com sucesso!\n📊 {rows_count} linhas, {len(columns)} colunas"
                elif function_name == "get_database_schema" and result.get("tables"):
                    tables_count = len(result["tables"])
                    table_names = "\n".join([f"  • {t['full_name']}" for t in result["tables"][:10]])
                    if tables_count > 10:
                        table_names += f"\n  ... e mais {tables_count - 10} tabelas"
                    result_str = f"📊 Schema completo:\n**{tables_count} tabelas descobertas:**\n{table_names}"
                
                await step.end(output=result_str)
                
                # Adicionar ao histórico como resposta da tool
                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False, default=str)
                })
            
            # Continuar loop para nova chamada
            
        # Atualizar histórico
        cl.user_session.set("history", history)
        
        # Atualizar mensagem com resposta final
        response_msg.content = f"**Resposta:**\n\n{final_response}"
        await response_msg.update()
        
    except Exception as e:
        error_msg = f"❌ Erro: {str(e)}"
        response_msg.content = error_msg
        await response_msg.update()


if __name__ == "__main__":
    # Executar Chainlit
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)





