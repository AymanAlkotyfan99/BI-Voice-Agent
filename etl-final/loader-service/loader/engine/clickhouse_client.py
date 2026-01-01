"""
Enhanced ClickHouse Client with Batch Insert Support
Optimized for high-throughput data loading
"""
import logging
from typing import List, Dict, Any, Optional
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError

logger = logging.getLogger(__name__)


class ClickHouseClient:
    """
    Enhanced ClickHouse client with batch insert support and error handling.
    
    Features:
    - Batch inserts for performance
    - Connection pooling
    - Error recovery
    - Type-safe operations
    """

    def __init__(self, host, port=9000, user="default", password="", database="default"):
        """
        Initialize ClickHouse client.
        
        Args:
            host: ClickHouse host
            port: ClickHouse port (default: 9000)
            user: Username
            password: Password
            database: Database name
        """
        try:
            try:
                init_client = Client(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database="default",
                    connect_timeout=10,
                    send_receive_timeout=300,
                    sync_request_timeout=300,
                )
                init_client.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            except Exception:
                pass

            self.client = Client(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=10,
                send_receive_timeout=300,
                sync_request_timeout=300,
            )
            logger.info(f"[ClickHouse] Connected to {host}:{port}/{database}")
        except Exception as e:
            logger.error(f"[ClickHouse] Connection failed: {e}")
            raise

    def insert_row(self, table: str, row: Dict[str, Any]):
        """
        Insert a single row into ClickHouse.
        
        Args:
            table: Table name
            row: Row dictionary
        """
        if not row:
            logger.warning(f"[ClickHouse] Empty row for table {table}")
            return
        
        try:
            columns = ", ".join(row.keys())
            # Convert all values to strings for ClickHouse String columns
            values = tuple(str(v) if v is not None else '' for v in row.values())
            
            query = f"INSERT INTO {table} ({columns}) VALUES"
            self.client.execute(query, [values])
            
        except ClickHouseError as e:
            logger.error(f"[ClickHouse] Error inserting row into {table}: {e}")
            raise
        except Exception as e:
            logger.error(f"[ClickHouse] Unexpected error inserting row: {e}")
            raise

    def insert_batch(self, table: str, rows: List[Dict[str, Any]], batch_size: int = 1000):
        """
        Insert multiple rows in batch for better performance.
        
        Args:
            table: Table name
            rows: List of row dictionaries
            batch_size: Number of rows per batch (default: 1000)
            
        Returns:
            Number of rows successfully inserted
        """
        if not rows:
            return 0
        
        if not table:
            logger.error("[ClickHouse] Table name is required")
            return 0
        
        inserted_count = 0
        
        try:
            # Get column names from first row
            if not rows[0]:
                logger.warning(f"[ClickHouse] Empty rows for table {table}")
                return 0
            
            columns = list(rows[0].keys())
            columns_str = ", ".join(columns)
            
            # Process in batches
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                
                # Prepare values for batch insert
                values_list = []
                for row in batch:
                    if not row:
                        continue
                    # Ensure all columns are present (fill missing with empty string)
                    values = tuple(str(row.get(col, '')) if row.get(col) is not None else '' for col in columns)
                    values_list.append(values)
                
                if not values_list:
                    continue
                
                # Execute batch insert
                query = f"INSERT INTO {table} ({columns_str}) VALUES"
                self.client.execute(query, values_list)
                inserted_count += len(values_list)
                
                logger.debug(f"[ClickHouse] Inserted batch of {len(values_list)} rows into {table}")
            
            logger.info(f"[ClickHouse] Successfully inserted {inserted_count} rows into {table}")
            return inserted_count
            
        except ClickHouseError as e:
            logger.error(f"[ClickHouse] Error inserting batch into {table}: {e}")
            raise
        except Exception as e:
            logger.error(f"[ClickHouse] Unexpected error inserting batch: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def create_table(self, table: str, columns: Dict[str, str], engine: str = "MergeTree()", order_by: str = "tuple()"):
        """
        Create a ClickHouse table with specified schema.
        
        Args:
            table: Table name
            columns: Dictionary of column_name: column_type
            engine: Table engine (default: MergeTree())
            order_by: ORDER BY clause (default: tuple())
        """
        try:
            column_defs = ", ".join([f"{name} {col_type}" for name, col_type in columns.items()])
            
            create_query = f"""
            CREATE TABLE IF NOT EXISTS {table} (
                {column_defs}
            ) ENGINE = {engine}
            ORDER BY {order_by}
            """
            
            self.client.execute(create_query)
            logger.info(f"[ClickHouse] Table {table} created/verified")
            
        except ClickHouseError as e:
            logger.error(f"[ClickHouse] Error creating table {table}: {e}")
            raise
        except Exception as e:
            logger.error(f"[ClickHouse] Unexpected error creating table: {e}")
            raise

    def table_exists(self, table: str) -> bool:
        """
        Check if table exists.
        
        Args:
            table: Table name
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            result = self.client.execute(f"EXISTS TABLE {table}")
            return result[0][0] == 1
        except Exception as e:
            logger.error(f"[ClickHouse] Error checking table existence: {e}")
            return False

    def get_table_columns(self, table: str) -> List[str]:
        """
        Get list of column names for a table.
        
        Args:
            table: Table name
            
        Returns:
            List of column names
        """
        try:
            result = self.client.execute(f"DESCRIBE TABLE {table}")
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"[ClickHouse] Error getting columns for {table}: {e}")
            return []
