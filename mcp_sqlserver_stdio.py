"""
MCP Server SQL Server - stdio para Chainlit
Desenvolvido por ness.

Implementação nativa de MCP server via stdio para acesso ao SQL Server
"""

import sys
import json
import asyncio
from typing import Any, Sequence

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

import pyodbc
from datetime import datetime


# Configuração do servidor MCP
app = Server("sql-server-mcp")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Lista todas as ferramentas disponíveis"""
    return [
        types.Tool(
            name="connect_database",
            description="Conecta a um SQL Server e descobre automaticamente a estrutura completa (tabelas, colunas, PKs, FKs)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Endereço do servidor SQL"
                    },
                    "database": {
                        "type": "string",
                        "description": "Nome da base de dados"
                    },
                    "username": {
                        "type": "string",
                        "description": "Usuário SQL"
                    },
                    "password": {
                        "type": "string",
                        "description": "Senha"
                    },
                    "port": {
                        "type": "integer",
                        "description": "Porta (padrão: 1433)"
                    }
                },
                "required": ["server", "database", "username", "password"]
            }
        ),
        types.Tool(
            name="get_database_schema",
            description="Retorna metadados completos do banco descoberto",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="execute_query",
            description="Executa query SQL SELECT de forma segura",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query SQL SELECT a executar"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Limite de resultados (padrão: 100)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="analyze_relationships",
            description="Analisa foreign keys e sugere JOINs entre tabelas",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="preview_table",
            description="Mostra primeiras linhas de uma tabela",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Nome completo da tabela (schema.table)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Quantidade de linhas (padrão: 10)"
                    }
                },
                "required": ["table"]
            }
        ),
        types.Tool(
            name="search_data",
            description="Busca termo específico em colunas de texto",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Nome completo da tabela"
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Termo a buscar"
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Colunas específicas (opcional)"
                    }
                },
                "required": ["table", "search_term"]
            }
        )
    ]


# Estado global do servidor
class MCPState:
    def __init__(self):
        self.connection: Any = None
        self.schema_cache: dict = {}
        self.server_name: str = ""
        self.database_name: str = ""
    
    def discover_schema(self):
        """Descobre schema completo do banco"""
        cursor = self.connection.cursor()
        
        # 1. Descobrir tabelas
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
              AND TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)
        
        tables = []
        for row in cursor.fetchall():
            schema, name = row
            table_info = {
                "schema": schema,
                "name": name,
                "full_name": f"{schema}.{name}"
            }
            tables.append(table_info)
        
        self.schema_cache["tables"] = tables
        
        # 2. Para cada tabela, descobrir colunas e relacionamentos
        for table in tables:
            # Colunas
            columns = self._get_columns(table['schema'], table['name'])
            table["columns"] = columns
            
            # Primary Keys
            pks = self._get_primary_keys(table['schema'], table['name'])
            table["primary_keys"] = pks
            
            # Foreign Keys
            fks = self._get_foreign_keys(table['schema'], table['name'])
            table["foreign_keys"] = fks
            
            # Contagem de linhas (aproximada)
            row_count = self._get_row_count(table['schema'], table['name'])
            table["approx_rows"] = row_count
        
        self.schema_cache["discovered_at"] = datetime.now().isoformat()
    
    def _get_columns(self, schema: str, table: str) -> list[dict]:
        """Descobre colunas de uma tabela"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, 
                   IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, schema, table)
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row[0],
                "type": row[1],
                "max_length": row[2],
                "nullable": row[3] == "YES",
                "default": row[4]
            })
        
        return columns
    
    def _get_primary_keys(self, schema: str, table: str) -> list[str]:
        """Descobre primary keys"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
              AND CONSTRAINT_NAME LIKE 'PK_%'
            ORDER BY ORDINAL_POSITION
        """, schema, table)
        
        return [row[0] for row in cursor.fetchall()]
    
    def _get_foreign_keys(self, schema: str, table: str) -> list[dict]:
        """Descobre foreign keys"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                COL_NAME(fc.parent_object_id, fc.parent_column_id) AS column_name,
                OBJECT_SCHEMA_NAME(fc.referenced_object_id) AS ref_schema,
                OBJECT_NAME(fc.referenced_object_id) AS ref_table,
                COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ref_column
            FROM sys.foreign_key_columns AS fc
            WHERE OBJECT_SCHEMA_NAME(fc.parent_object_id) = ?
              AND OBJECT_NAME(fc.parent_object_id) = ?
        """, schema, table)
        
        fks = []
        for row in cursor.fetchall():
            fks.append({
                "column": row[0],
                "references_schema": row[1],
                "references_table": row[2],
                "references_column": row[3]
            })
        
        return fks
    
    def _get_row_count(self, schema: str, table: str) -> int:
        """Obtém contagem aproximada de linhas"""
        try:
            cursor = self.connection.cursor()
            table_full = f"{schema}.{table}"
            cursor.execute(f"""
                SELECT SUM(rows) 
                FROM sys.partitions 
                WHERE object_id = OBJECT_ID(?)
                  AND index_id IN (0,1)
            """, table_full)
            
            result = cursor.fetchone()
            return result[0] if result[0] else 0
        except:
            return 0


# Estado global
state = MCPState()


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """Executa ferramentas"""
    
    if name == "connect_database":
        try:
            server = arguments.get("server")
            database = arguments.get("database")
            username = arguments.get("username")
            password = arguments.get("password")
            port = arguments.get("port", 1433)
            
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
            
            state.connection = pyodbc.connect(conn_str, timeout=30)
            state.server_name = server
            state.database_name = database
            state.discover_schema()
            
            tables_count = len(state.schema_cache.get("tables", []))
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": f"Conectado a {server}/{database}",
                        "tables_discovered": tables_count
                    }, indent=2, ensure_ascii=False)
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    }, indent=2, ensure_ascii=False)
                )
            ]
    
    elif name == "get_database_schema":
        return [
            types.TextContent(
                type="text",
                text=json.dumps(state.schema_cache, indent=2, ensure_ascii=False, default=str)
            )
        ]
    
    elif name == "execute_query":
        try:
            query = arguments.get("query")
            limit = arguments.get("limit", 100)
            
            # Validação de segurança
            query_upper = query.strip().upper()
            
            if not query_upper.startswith("SELECT"):
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": "Apenas queries SELECT são permitidas"
                        }, indent=2, ensure_ascii=False)
                    )
                ]
            
            dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "EXEC", "XP_CMDSHELL", "SP_"]
            for cmd in dangerous:
                if cmd in query_upper:
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "error": f"Comando '{cmd}' não permitido por segurança"
                            }, indent=2, ensure_ascii=False)
                        )
                    ]
            
            cursor = state.connection.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(limit)
            
            results = [dict(zip(columns, row)) for row in rows]
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "columns": columns,
                        "rows": results,
                        "count": len(results),
                        "limited": len(results) == limit
                    }, indent=2, ensure_ascii=False, default=str)
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    }, indent=2, ensure_ascii=False)
                )
            ]
    
    elif name == "analyze_relationships":
        try:
            if not state.schema_cache or "tables" not in state.schema_cache:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Schema não descoberto"
                        }, indent=2, ensure_ascii=False)
                    )
                ]
            
            relationships = []
            for table in state.schema_cache["tables"]:
                if table.get("foreign_keys"):
                    for fk in table["foreign_keys"]:
                        relationships.append({
                            "from_table": f"{table['schema']}.{table['name']}",
                            "from_column": fk["column"],
                            "to_table": f"{fk['references_schema']}.{fk['references_table']}",
                            "to_column": fk["references_column"],
                            "join_suggestion": f"JOIN {fk['references_schema']}.{fk['references_table']} ON {table['schema']}.{table['name']}.{fk['column']} = {fk['references_schema']}.{fk['references_table']}.{fk['references_column']}"
                        })
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "total_relationships": len(relationships),
                        "relationships": relationships
                    }, indent=2, ensure_ascii=False, default=str)
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e)
                    }, indent=2, ensure_ascii=False)
                )
            ]
    
    elif name == "preview_table":
        try:
            table = arguments.get("table")
            limit = arguments.get("limit", 10)
            
            table_parts = table.split(".")
            schema = table_parts[0] if len(table_parts) > 1 else "dbo"
            table_name = table_parts[-1]
            
            query = f"SELECT TOP {limit} * FROM {schema}.{table_name}"
            query_upper = query.strip().upper()
            
            cursor = state.connection.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(limit)
            
            results = [dict(zip(columns, row)) for row in rows]
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "columns": columns,
                        "rows": results,
                        "count": len(results),
                        "limited": len(results) == limit
                    }, indent=2, ensure_ascii=False, default=str)
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    }, indent=2, ensure_ascii=False)
                )
            ]
    
    elif name == "search_data":
        try:
            table = arguments.get("table")
            search_term = arguments.get("search_term")
            columns = arguments.get("columns")
            
            table_parts = table.split(".")
            schema = table_parts[0] if len(table_parts) > 1 else "dbo"
            table_name = table_parts[-1]
            
            if not columns:
                table_info = next((t for t in state.schema_cache.get("tables", []) 
                                 if t["schema"] == schema and t["name"] == table_name), None)
                if not table_info:
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "error": "Tabela não encontrada"
                            }, indent=2, ensure_ascii=False)
                        )
                    ]
                
                text_types = ["VARCHAR", "NVARCHAR", "TEXT", "NTEXT", "CHAR", "NCHAR"]
                columns = [col["name"] for col in table_info["columns"] 
                          if col["type"].upper() in text_types]
            
            if not columns:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Nenhuma coluna de texto encontrada"
                        }, indent=2, ensure_ascii=False)
                    )
                ]
            
            like_clauses = [f"{col} LIKE '%{search_term}%'" for col in columns]
            where_clause = " OR ".join(like_clauses)
            
            query = f"SELECT TOP 50 * FROM {schema}.{table_name} WHERE {where_clause}"
            
            cursor = state.connection.cursor()
            cursor.execute(query)
            
            columns_result = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(50)
            
            results = [dict(zip(columns_result, row)) for row in rows]
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "columns": columns_result,
                        "rows": results,
                        "count": len(results),
                        "limited": len(results) == 50
                    }, indent=2, ensure_ascii=False, default=str)
                )
            ]
            
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    }, indent=2, ensure_ascii=False)
                )
            ]
    
    else:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Tool '{name}' não reconhecida"
                }, indent=2, ensure_ascii=False)
            )
        ]


async def main():
    """Main entry point do MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sql-server-mcp",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())




