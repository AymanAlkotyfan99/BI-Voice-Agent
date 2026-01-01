"""
Loader Logic for ClickHouse Operations
Provides high-level interface for data loading operations
"""
import logging
from typing import List, Dict, Any
from .clickhouse_client import ClickHouseClient

logger = logging.getLogger(__name__)


class LoaderLogic:
    """
    High-level loader logic for ClickHouse operations.
    
    Features:
    - Single row inserts
    - Batch inserts
    - Table management
    - Error handling
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize loader logic.
        
        Args:
            config: Configuration dictionary with ClickHouse connection details
        """
        self.client = ClickHouseClient(
            host=config.get("host", "clickhouse"),
            port=config.get("port", 9000),
            user=config.get("user", "default"),
            password=config.get("password", ""),
            database=config.get("database", "default"),
        )

    def load_row(self, table: str, row: Dict[str, Any]):
        """
        Load a single row into ClickHouse.
        
        Args:
            table: Table name
            row: Row dictionary
        """
        self.client.insert_row(table, row)

    def load_batch(self, table: str, rows: List[Dict[str, Any]], batch_size: int = 1000) -> int:
        """
        Load multiple rows in batch.
        
        Args:
            table: Table name
            rows: List of row dictionaries
            batch_size: Batch size for inserts
            
        Returns:
            Number of rows successfully inserted
        """
        return self.client.insert_batch(table, rows, batch_size)
