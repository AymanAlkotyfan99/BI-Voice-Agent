"""
ClickHouse Executor

Executes validated SQL queries on ClickHouse.
Returns results for visualization.
"""

import clickhouse_connect
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def sanitize_sql_for_http(sql: str) -> str:
    """
    Sanitize SQL for ClickHouse HTTP execution.
    
    Removes incompatible syntax:
    - FORMAT Native (not supported via HTTP)
    - Semicolons (causes multi-statement errors)
    - Extra whitespace
    
    Args:
        sql: Raw SQL string (possibly from LLM)
    
    Returns:
        Clean SQL safe for HTTP execution
    """
    if not sql:
        return ""
    
    # Remove FORMAT Native (case-insensitive)
    import re
    clean_sql = re.sub(r'\s+FORMAT\s+Native\s*', ' ', sql, flags=re.IGNORECASE)
    
    # Remove all semicolons
    clean_sql = clean_sql.replace(';', '')
    
    # Remove extra whitespace and trim
    clean_sql = ' '.join(clean_sql.split())
    clean_sql = clean_sql.strip()
    
    return clean_sql


class ClickHouseExecutor:
    """
    Execute SELECT queries on ClickHouse using HTTP protocol (port 8123).
    Returns results in format suitable for Metabase/visualization.
    """
    
    def __init__(self):
        """Initialize ClickHouse executor with environment configuration."""
        self.host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        self.port = int(os.getenv('CLICKHOUSE_PORT', '8123'))
        self.user = os.getenv('CLICKHOUSE_USER', 'etl_user')
        self.password = os.getenv('CLICKHOUSE_PASSWORD', 'etl_pass123')
        self.database = os.getenv('CLICKHOUSE_DATABASE', 'etl')
        
        # Validate port for HTTP protocol
        if self.port == 9000:
            logger.warning(
                "⚠️  CLICKHOUSE_PORT is set to 9000 (native protocol). "
                "HTTP interface requires port 8123. "
                "Update your .env file: CLICKHOUSE_PORT=8123"
            )
        
        # Create clickhouse-connect client
        self.client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            database=self.database
        )
    
    def execute_query(self, sql: str) -> Dict:
        """
        Execute SQL query on ClickHouse.
        
        Args:
            sql: SQL query (must be SELECT only)
        
        Returns:
            dict: {
                'success': bool,
                'rows': list of dicts (query results),
                'columns': list of column names,
                'row_count': int,
                'execution_time_ms': int,
                'error': str (if failed)
            }
        """
        try:
            import time
            start_time = time.time()
            
            # Sanitize SQL for HTTP execution (removes FORMAT Native, semicolons)
            clean_sql = sanitize_sql_for_http(sql)
            
            logger.info(f"Executing query on ClickHouse: {clean_sql[:100]}...")
            
            # Execute query using clickhouse-connect
            result = self.client.query(clean_sql)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Convert result to list of dicts
            rows = []
            columns = result.column_names
            
            for row in result.result_rows:
                row_dict = {}
                for i, col_name in enumerate(columns):
                    row_dict[col_name] = row[i]
                rows.append(row_dict)
            
            logger.info(f"Query successful: {len(rows)} rows in {execution_time_ms}ms")
            
            return {
                'success': True,
                'rows': rows,
                'columns': columns,
                'row_count': len(rows),
                'execution_time_ms': execution_time_ms
            }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"ClickHouse query error: {error_msg}")
            
            # Special handling for port misconfiguration
            if 'Port 9000 is for clickhouse-client' in error_msg or 'Connection refused' in error_msg:
                return {
                    'success': False,
                    'error': (
                        'ClickHouse connection error. '
                        'Ensure ClickHouse is running and CLICKHOUSE_PORT=8123 is set in .env file.'
                    )
                }
            
            return {
                'success': False,
                'error': f"Query execution failed: {error_msg[:200]}"
            }
    
    def test_connection(self) -> bool:
        """
        Test ClickHouse connection.
        
        Returns:
            bool: True if connected
        """
        try:
            result = self.execute_query("SELECT 1 as test")
            return result['success']
        except Exception:
            return False
    
    def get_tables(self, database: Optional[str] = None) -> List[str]:
        """
        Get list of tables in database.
        
        Args:
            database: Database name (uses default if not provided)
        
        Returns:
            list: Table names
        """
        db = database or self.database
        sql = f"SHOW TABLES FROM {db}"
        
        result = self.execute_query(sql)
        
        if result['success']:
            return [row['name'] for row in result['rows']]
        return []
    
    def get_table_schema(self, table_name: str, database: Optional[str] = None) -> Dict:
        """
        Get schema for a table.
        
        Args:
            table_name: Table name
            database: Database name
        
        Returns:
            dict: Schema information
        """
        db = database or self.database
        sql = f"DESCRIBE TABLE {db}.{table_name}"
        
        result = self.execute_query(sql)
        
        if result['success']:
            return {
                'columns': result['rows'],
                'column_names': [row['name'] for row in result['rows']],
                'column_types': {row['name']: row['type'] for row in result['rows']}
            }
        
        return {}


# Singleton instance
_clickhouse_executor = None

def get_clickhouse_executor() -> ClickHouseExecutor:
    """Get or create ClickHouse executor singleton."""
    global _clickhouse_executor
    if _clickhouse_executor is None:
        _clickhouse_executor = ClickHouseExecutor()
    return _clickhouse_executor

