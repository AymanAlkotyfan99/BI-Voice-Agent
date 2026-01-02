"""
ClickHouse Executor

Executes validated SQL queries on ClickHouse.
Returns results for visualization.
"""

import requests
import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ClickHouseExecutor:
    """
    Execute SELECT queries on ClickHouse.
    Returns results in format suitable for Metabase/visualization.
    """
    
    def __init__(self):
        """Initialize ClickHouse executor with environment configuration."""
        self.host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        self.port = os.getenv('CLICKHOUSE_PORT', '8123')
        self.user = os.getenv('CLICKHOUSE_USER', 'etl_user')
        self.password = os.getenv('CLICKHOUSE_PASSWORD', 'etl_pass123')
        self.database = os.getenv('CLICKHOUSE_DATABASE', 'etl')
        
        # Validate port for HTTP protocol
        if self.port == '9000':
            logger.warning(
                "⚠️  CLICKHOUSE_PORT is set to 9000 (native protocol). "
                "HTTP interface requires port 8123. "
                "Update your .env file: CLICKHOUSE_PORT=8123"
            )
        
        self.base_url = f'http://{self.host}:{self.port}'
    
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
            
            logger.info(f"Executing query on ClickHouse: {sql[:100]}...")
            
            # Build request parameters
            params = {
                'query': sql,
                'database': self.database,
                'default_format': 'JSONEachRow'
            }
            
            if self.user:
                params['user'] = self.user
            if self.password:
                params['password'] = self.password
            
            # Execute query
            response = requests.post(
                self.base_url,
                params=params,
                timeout=30
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"ClickHouse error: {response.status_code} - {error_text}")
                
                # Special handling for port misconfiguration
                if 'Port 9000 is for clickhouse-client' in error_text:
                    return {
                        'success': False,
                        'error': (
                            'ClickHouse port misconfiguration detected. '
                            'Port 9000 is for native protocol (clickhouse-client). '
                            'HTTP queries require port 8123. '
                            'Please update CLICKHOUSE_PORT=8123 in your .env file and restart the server.'
                        )
                    }
                
                return {
                    'success': False,
                    'error': f"ClickHouse error: {error_text[:200]}"
                }
            
            # Parse results
            rows = []
            columns = set()
            
            for line in response.text.strip().split('\n'):
                if line:
                    row = json.loads(line)
                    rows.append(row)
                    columns.update(row.keys())
            
            columns = list(columns)
            
            logger.info(f"Query successful: {len(rows)} rows in {execution_time_ms}ms")
            
            return {
                'success': True,
                'rows': rows,
                'columns': columns,
                'row_count': len(rows),
                'execution_time_ms': execution_time_ms
            }
        
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to ClickHouse")
            return {
                'success': False,
                'error': 'ClickHouse is not reachable. Please ensure it is running.'
            }
        
        except requests.exceptions.Timeout:
            logger.error("ClickHouse query timed out")
            return {
                'success': False,
                'error': 'Query timeout. Try simplifying the query.'
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ClickHouse response: {e}")
            return {
                'success': False,
                'error': 'Invalid response from ClickHouse'
            }
        
        except Exception as e:
            logger.error(f"Error executing query: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Execution error: {str(e)}"
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

