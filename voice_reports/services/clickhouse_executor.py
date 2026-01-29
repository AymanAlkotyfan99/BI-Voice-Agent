"""
ClickHouse Executor

Executes validated SQL queries on ClickHouse.
Returns results for visualization.
"""

import clickhouse_connect
import os
import logging
import math
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


def _normalize_invalid_casts(sql: str) -> str:
    """
    Global fix: Replace invalid ClickHouse functions with valid ones.
    toFloat64OrNullOrNull / toInt64OrNullOrNull do NOT exist in ClickHouse.
    Applied at execution time so ALL queries (including those bypassing the compiler) are safe.
    """
    if not sql:
        return sql
    sql = sql.replace("toFloat64OrNullOrNull(", "toFloat64OrNull(")
    sql = sql.replace("toInt64OrNullOrNull(", "toInt64OrNull(")
    return sql


def sanitize_sql_for_http(sql: str) -> str:
    """
    Sanitize SQL for ClickHouse HTTP execution.
    
    Removes incompatible syntax:
    - FORMAT Native (not supported via HTTP)
    - Semicolons (causes multi-statement errors)
    - Invalid cast functions (toFloat64OrNullOrNull → toFloat64OrNull)
    - Extra whitespace
    
    Args:
        sql: Raw SQL string (possibly from LLM)
    
    Returns:
        Clean SQL safe for HTTP execution
    """
    if not sql:
        return ""

    # Global fix: normalize invalid ClickHouse cast functions
    sql = _normalize_invalid_casts(sql)

    # Remove FORMAT Native (case-insensitive)
    import re
    clean_sql = re.sub(r'\s+FORMAT\s+Native\s*', ' ', sql, flags=re.IGNORECASE)

    # Remove all semicolons
    clean_sql = clean_sql.replace(';', '')

    # Remove extra whitespace and trim
    clean_sql = ' '.join(clean_sql.split())
    clean_sql = clean_sql.strip()

    return clean_sql


def sanitize_numeric_value(value: Any) -> Any:
    """
    🔒 NaN-SAFE: Sanitize a single numeric value to ensure JSON compatibility.
    
    Replaces NaN, Infinity, and -Infinity with 0 (or None for NULL).
    This ensures values can be safely stored in PostgreSQL JSON/JSONB fields
    and serialized to JSON without errors.
    
    Handles all numeric types including:
    - Python float, int
    - Decimal (from ClickHouse Decimal types)
    - numpy.float64, numpy.float32 (if numpy is used)
    - Any other numeric type that can be converted to float
    
    Args:
        value: Any value (numeric, string, None, etc.)
    
    Returns:
        Sanitized value (NaN/Infinity → 0, None → None, other values unchanged)
    """
    # Handle None/NULL
    if value is None:
        return None
    
    # Handle Python int - never NaN/Infinity, return as-is
    if isinstance(value, int):
        return value
    
    # Handle float types (NaN, Infinity) - direct check
    if isinstance(value, float):
        if math.isnan(value):
            return 0  # Replace NaN with 0
        elif math.isinf(value):
            return 0  # Replace Infinity/-Infinity with 0
        return value
    
    # Handle Decimal types (ClickHouse returns Decimal for Decimal/Float64 columns)
    # Decimal types can be converted to float for NaN/Infinity checking
    try:
        from decimal import Decimal
        if isinstance(value, Decimal):
            # Convert Decimal to float to check for NaN/Infinity
            # Decimal('NaN') and Decimal('Infinity') exist but are rare
            # Converting to float is the safest way to detect them
            try:
                float_val = float(value)
                if math.isnan(float_val):
                    return 0  # Replace NaN with 0
                elif math.isinf(float_val):
                    return 0  # Replace Infinity/-Infinity with 0
                # Return as float for JSON compatibility (Decimal isn't JSON serializable)
                return float_val
            except (ValueError, OverflowError, TypeError):
                # If conversion fails, return 0 as fallback
                return 0
    except ImportError:
        # Decimal not available, skip this check
        pass
    
    # Handle numpy types (if numpy is installed and used by clickhouse-connect)
    try:
        import numpy as np
        if isinstance(value, (np.floating, np.integer)):
            # Convert numpy numeric types to Python float for NaN/Infinity checking
            float_val = float(value)
            if math.isnan(float_val):
                return 0  # Replace NaN with 0
            elif math.isinf(float_val):
                return 0  # Replace Infinity/-Infinity with 0
            # Convert numpy types to Python native types for JSON serialization
            if isinstance(value, np.integer):
                return int(value)
            return float_val
    except (ImportError, ValueError, OverflowError, TypeError):
        # numpy not available or conversion failed, continue to generic check
        pass
    
    # Generic fallback: Try to convert any numeric-like value to float
    # This catches edge cases where ClickHouse returns unusual numeric types
    try:
        # Only attempt conversion if value looks numeric (not strings, lists, etc.)
        if not isinstance(value, (str, bytes, list, dict, tuple, bool)):
            float_val = float(value)
            if math.isnan(float_val):
                return 0  # Replace NaN with 0
            elif math.isinf(float_val):
                return 0  # Replace Infinity/-Infinity with 0
            # If conversion succeeded and no NaN/Infinity, return original value
            # (to preserve type if it's JSON-serializable)
    except (ValueError, TypeError, OverflowError):
        # Conversion failed - value is not numeric, return as-is
        pass
    
    # For non-numeric types (strings, lists, dicts, etc.), return as-is
    return value


def sanitize_query_results(rows: List[Dict]) -> List[Dict]:
    """
    🔒 NaN-SAFE: Sanitize query results to ensure JSON compatibility.
    
    Recursively sanitizes all numeric values in result rows, replacing
    NaN, Infinity, and -Infinity with 0. This ensures results can be:
    - Safely serialized to JSON
    - Stored in PostgreSQL JSON/JSONB fields
    - Sent to frontend/Metabase without errors
    
    Args:
        rows: List of dictionaries representing query result rows
    
    Returns:
        Sanitized list of dictionaries with all NaN/Infinity values replaced
    """
    sanitized_rows = []
    
    for row in rows:
        sanitized_row = {}
        for key, value in row.items():
            # Recursively sanitize nested structures
            if isinstance(value, dict):
                sanitized_row[key] = sanitize_query_results([value])[0] if value else {}
            elif isinstance(value, list):
                sanitized_row[key] = [sanitize_numeric_value(item) for item in value]
            else:
                sanitized_row[key] = sanitize_numeric_value(value)
        sanitized_rows.append(sanitized_row)
    
    return sanitized_rows


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
            
            # 🔍 FINAL SQL BOUNDARY LOGGING (MANDATORY)
            # This logs the EXACT query sent to ClickHouse
            logger.error("🚨 FINAL SQL SENT TO CLICKHOUSE:")
            logger.error("="*80)
            logger.error(clean_sql)
            logger.error("="*80)
            
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
            
            # 🔒 NaN-SAFE: Sanitize results to remove NaN/Infinity values
            # This ensures JSON compatibility and PostgreSQL storage safety
            sanitized_rows = sanitize_query_results(rows)
            
            logger.info(f"Query successful: {len(sanitized_rows)} rows in {execution_time_ms}ms")
            
            return {
                'success': True,
                'rows': sanitized_rows,
                'columns': columns,
                'row_count': len(sanitized_rows),
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

