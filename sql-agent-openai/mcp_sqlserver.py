"""
MCP Server para Descoberta Dinâmica de Schema SQL Server

Funcionalidades:
- Descoberta automática de tabelas, colunas, PKs, FKs
- Cache de metadados em memória
- Execução segura de queries SELECT
- Análise de relacionamentos
"""

import pyodbc
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class SQLServerMCP:
    """MCP Server para operações SQL Server"""
    
    def __init__(self):
        self.connection: Optional[pyodbc.Connection] = None
        self.schema_cache: Dict[str, Any] = {}
        self.server_name = ""
        self.database_name = ""
        
    def connect(self, server: str, database: str, username: str, password: str, port: int = 1433) -> Dict[str, Any]:
        """Conecta ao SQL Server e descobre schema"""
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
            
            self.connection = pyodbc.connect(conn_str, timeout=30)
            self.server_name = server
            self.database_name = database
            
            # Descobrir schema completo
            self._discover_schema()
            
            return {
                "success": True,
                "message": f"Conectado a {server}/{database}",
                "tables_discovered": len(self.schema_cache.get("tables", []))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _discover_schema(self):
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
            table_key = f"{table['schema']}.{table['name']}"
            
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
    
    def _get_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
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
    
    def _get_primary_keys(self, schema: str, table: str) -> List[str]:
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
    
    def _get_foreign_keys(self, schema: str, table: str) -> List[Dict[str, Any]]:
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
    
    def get_schema(self) -> Dict[str, Any]:
        """Retorna schema completo descoberto"""
        return self.schema_cache
    
    def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Executa query SELECT de forma segura"""
        try:
            # Validação de segurança
            query_upper = query.strip().upper()
            
            # Apenas SELECT permitido
            if not query_upper.startswith("SELECT"):
                return {
                    "success": False,
                    "error": "Apenas queries SELECT são permitidas"
                }
            
            # Blacklist de comandos perigosos
            dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "EXEC", "XP_CMDSHELL", "SP_"]
            for cmd in dangerous:
                if cmd in query_upper:
                    return {
                        "success": False,
                        "error": f"Comando '{cmd}' não permitido por segurança"
                    }
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(limit)
            
            results = [dict(zip(columns, row)) for row in rows]
            
            return {
                "success": True,
                "columns": columns,
                "rows": results,
                "count": len(results),
                "limited": len(results) == limit
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_relationships(self) -> Dict[str, Any]:
        """Analisa relacionamentos entre tabelas"""
        if not self.schema_cache or "tables" not in self.schema_cache:
            return {"error": "Schema não descoberto"}
        
        relationships = []
        for table in self.schema_cache["tables"]:
            if table.get("foreign_keys"):
                for fk in table["foreign_keys"]:
                    relationships.append({
                        "from_table": f"{table['schema']}.{table['name']}",
                        "from_column": fk["column"],
                        "to_table": f"{fk['references_schema']}.{fk['references_table']}",
                        "to_column": fk["references_column"],
                        "join_suggestion": f"JOIN {fk['references_schema']}.{fk['references_table']} ON {table['schema']}.{table['name']}.{fk['column']} = {fk['references_schema']}.{fk['references_table']}.{fk['references_column']}"
                    })
        
        return {
            "total_relationships": len(relationships),
            "relationships": relationships
        }
    
    def preview_table(self, schema: str, table: str, limit: int = 10) -> Dict[str, Any]:
        """Mostra primeiras linhas de uma tabela"""
        query = f"SELECT TOP {limit} * FROM {schema}.{table}"
        return self.execute_query(query)
    
    def search_data(self, table_schema: str, table_name: str, search_term: str, columns: List[str] = None) -> Dict[str, Any]:
        """Busca termo em colunas de texto"""
        # Descobrir colunas de texto se não especificadas
        if not columns:
            table = next((t for t in self.schema_cache.get("tables", []) 
                         if t["schema"] == table_schema and t["name"] == table_name), None)
            if not table:
                return {"error": "Tabela não encontrada"}
            
            # Filtrar apenas colunas de texto
            text_types = ["VARCHAR", "NVARCHAR", "TEXT", "NTEXT", "CHAR", "NCHAR"]
            columns = [col["name"] for col in table["columns"] 
                      if col["type"].upper() in text_types]
        
        if not columns:
            return {"error": "Nenhuma coluna de texto encontrada"}
        
        # Construir query com LIKE
        like_clauses = [f"{col} LIKE '%{search_term}%'" for col in columns]
        where_clause = " OR ".join(like_clauses)
        
        query = f"SELECT TOP 50 * FROM {table_schema}.{table_name} WHERE {where_clause}"
        return self.execute_query(query, limit=50)


# Tools MCP (definições)
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "connect_database",
            "description": "Conecta a um SQL Server e descobre automaticamente a estrutura completa (tabelas, colunas, PKs, FKs)",
            "parameters": {
                "type": "object",
                "properties": {
                    "server": {"type": "string", "description": "Endereço do servidor SQL"},
                    "database": {"type": "string", "description": "Nome da base de dados"},
                    "username": {"type": "string", "description": "Usuário SQL"},
                    "password": {"type": "string", "description": "Senha"},
                    "port": {"type": "integer", "description": "Porta (padrão: 1433)"}
                },
                "required": ["server", "database", "username", "password"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_database_schema",
            "description": "Retorna metadados completos do banco descoberto",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_query",
            "description": "Executa query SQL SELECT de forma segura",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query SQL SELECT a executar"},
                    "limit": {"type": "integer", "description": "Limite de resultados (padrão: 100)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_relationships",
            "description": "Analisa foreign keys e sugere JOINs entre tabelas",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "preview_table",
            "description": "Mostra primeiras linhas de uma tabela",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "Nome completo da tabela (schema.table)"},
                    "limit": {"type": "integer", "description": "Quantidade de linhas (padrão: 10)"}
                },
                "required": ["table"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_data",
            "description": "Busca termo específico em colunas de texto",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "Nome completo da tabela"},
                    "search_term": {"type": "string", "description": "Termo a buscar"},
                    "columns": {"type": "array", "items": {"type": "string"}, "description": "Colunas específicas (opcional)"}
                },
                "required": ["table", "search_term"]
            }
        }
    }
]


# Instância global
mcp_server = SQLServerMCP()


def execute_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Executa ferramenta MCP"""
    if tool_name == "connect_database":
        return mcp_server.connect(**arguments)
    
    elif tool_name == "get_database_schema":
        return mcp_server.get_schema()
    
    elif tool_name == "execute_query":
        return mcp_server.execute_query(
            arguments.get("query"),
            arguments.get("limit", 100)
        )
    
    elif tool_name == "analyze_relationships":
        return mcp_server.analyze_relationships()
    
    elif tool_name == "preview_table":
        table_parts = arguments["table"].split(".")
        return mcp_server.preview_table(
            table_parts[0] if len(table_parts) > 1 else "dbo",
            table_parts[-1],
            arguments.get("limit", 10)
        )
    
    elif tool_name == "search_data":
        table_parts = arguments["table"].split(".")
        return mcp_server.search_data(
            table_parts[0] if len(table_parts) > 1 else "dbo",
            table_parts[-1],
            arguments["search_term"],
            arguments.get("columns")
        )
    
    else:
        return {"error": f"Ferramenta '{tool_name}' não reconhecida"}


if __name__ == "__main__":
    print("🔧 SQL Server MCP Server")
    print("=" * 50)
    print("\nEste arquivo implementa as ferramentas MCP.")
    print("Use via app_openai_mcp.py ou integração HTTP.")
    print("\n✅ Ferramentas disponíveis:", len(MCP_TOOLS))
    for tool in MCP_TOOLS:
        print(f"  • {tool['function']['name']}")





