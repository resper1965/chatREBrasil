"""
MCP Server PostgreSQL - stdio para Chainlit
Desenvolvido por ness.

Implementação nativa de MCP server via stdio para acesso ao PostgreSQL
"""

import sys
import json
import asyncio
from typing import Any, Sequence

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

import psycopg2
import psycopg2.extras
from datetime import datetime


# Configuração do servidor MCP
app = Server("postgres-mcp")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Lista todas as ferramentas disponíveis"""
    return [
        types.Tool(
            name="connect_database",
            description="Conecta a um PostgreSQL e descobre automaticamente a estrutura completa (tabelas, colunas, PKs, FKs)",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Endereço do servidor PostgreSQL"
                    },
                    "database": {
                        "type": "string",
                        "description": "Nome da base de dados"
                    },
                    "user": {
                        "type": "string",
                        "description": "Usuário PostgreSQL"
                    },
                    "password": {
                        "type": "string",
                        "description": "Senha"
                    },
                    "port": {
                        "type": "integer",
                        "description": "Porta (padrão: 5432)"
                    }
                },
                "required": ["host", "database", "user", "password"]
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
        self.host_name: str = ""
        self.database_name: str = ""

    def discover_schema(self):
        """Descobre schema completo do banco"""
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # 1. Descobrir tabelas
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
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
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, table))

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
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
              AND i.indisprimary
        """, (f"{schema}.{table}",))

        return [row[0] for row in cursor.fetchall()]

    def _get_foreign_keys(self, schema: str, table: str) -> list[dict]:
        """Descobre foreign keys"""
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_schema AS foreign_schema,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = %s
              AND tc.table_name = %s
        """, (schema, table))

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
            cursor.execute(f"""
                SELECT reltuples::bigint
                FROM pg_class
                WHERE oid = %s::regclass
            """, (f"{schema}.{table}",))

            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
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
            host = arguments.get("host")
            database = arguments.get("database")
            user = arguments.get("user")
            password = arguments.get("password")
            port = arguments.get("port", 5432)

            state.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                connect_timeout=30
            )

            state.host_name = host
            state.database_name = database
            state.discover_schema()

            tables_count = len(state.schema_cache.get("tables", []))

            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": f"Conectado a {host}/{database}",
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

            dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "CREATE"]
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

            cursor = state.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Adiciona LIMIT se não houver
            if "LIMIT" not in query_upper:
                query = f"{query.rstrip(';')} LIMIT {limit}"

            cursor.execute(query)
            rows = cursor.fetchall()

            # Converter para lista de dicts
            results = [dict(row) for row in rows]
            columns = list(results[0].keys()) if results else []

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
            schema = table_parts[0] if len(table_parts) > 1 else "public"
            table_name = table_parts[-1]

            cursor = state.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(f"""
                SELECT * FROM {schema}.{table_name}
                LIMIT %s
            """, (limit,))

            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            columns = list(results[0].keys()) if results else []

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
            schema = table_parts[0] if len(table_parts) > 1 else "public"
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

                text_types = ["character varying", "text", "character", "varchar", "char"]
                columns = [col["name"] for col in table_info["columns"]
                          if col["type"].lower() in text_types]

            if not columns:
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Nenhuma coluna de texto encontrada"
                        }, indent=2, ensure_ascii=False)
                    )
                ]

            like_clauses = [f"{col} ILIKE %s" for col in columns]
            where_clause = " OR ".join(like_clauses)
            params = [f"%{search_term}%"] * len(columns)

            cursor = state.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(f"""
                SELECT * FROM {schema}.{table_name}
                WHERE {where_clause}
                LIMIT 50
            """, params)

            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            columns_result = list(results[0].keys()) if results else []

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
                server_name="postgres-mcp",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
