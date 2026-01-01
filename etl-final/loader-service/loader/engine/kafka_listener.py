"""
Enhanced Loader Service Kafka Listener
Batch loads data into ClickHouse with comprehensive error handling and metadata
"""
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, List , Optional
from collections import defaultdict
from shared.utils.kafka_consumer import KafkaMessageConsumer
from shared.utils.kafka_producer import KafkaMessageProducer
from shared.utils.metadata_schema import MetadataSchema
from .loader_logic import LoaderLogic
from .clickhouse_client import ClickHouseClient

logger = logging.getLogger(__name__)


class CleanRowListener:
    """
    Enhanced listener for clean_rows_topic with batch loading.
    
    Features:
    - Batch inserts for performance
    - Table schema management
    - Error handling and retries
    - Metadata emission
    - Connection pooling
    """

    def __init__(self, batch_size: int = 1000):
        """
        Initialize loader listener.
        
        Args:
            batch_size: Number of rows to batch before inserting (default: 1000)
        """
        self.consumer = KafkaMessageConsumer("clean_rows_topic")
        self.producer = KafkaMessageProducer()
        self.batch_size = batch_size
        
        # Initialize ClickHouse client
        clickhouse_config = {
            "host": os.getenv("CLICKHOUSE_HOST", "clickhouse"),
            "port": int(os.getenv("CLICKHOUSE_PORT", "9000")),
            "user": os.getenv("CLICKHOUSE_USER", "default"),
            "password": os.getenv("CLICKHOUSE_PASSWORD", ""),
            "database": os.getenv("CLICKHOUSE_DATABASE", "etl")
        }
        
        self.loader = LoaderLogic(clickhouse_config)
        
        # Batch buffers per table
        self.batch_buffers: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.table_schemas: Dict[str, Dict[str, str]] = {}  # table_name -> {col: type}
        
        # Statistics tracking
        self.loaded_count = 0
        self.error_count = 0
        self.source_stats: Dict[str, Dict[str, int]] = {}  # source -> {loaded, failed}
        
        # Metadata emission interval
        self.metadata_interval = 5000  # Emit metadata every 5000 rows

    def _sanitize_table_name(self, source: str) -> str:
        """Sanitize source name to valid ClickHouse table name."""
        # Replace invalid characters
        table_name = source.replace(".", "_").replace("/", "_").replace("-", "_")
        table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)
        # Ensure it starts with letter or underscore
        if table_name and not table_name[0].isalpha():
            table_name = f"t_{table_name}"
        return table_name or "unknown_table"

    def _ensure_table_schema(self, source: str, row_data: Dict[str, Any]) -> Optional[str]:
        """
        Ensure table exists with correct schema.
        
        Args:
            source: Source identifier
            row_data: Sample row to infer schema
            
        Returns:
            Table name if successful, None otherwise
        """
        if not row_data:
            return None
        
        table_name = self._sanitize_table_name(source)
        
        # Check if we already know the schema
        if table_name in self.table_schemas:
            return table_name
        
        # Infer schema from row data (all String for now, can be enhanced)
        columns = {col: "String" for col in row_data.keys()}
        self.table_schemas[table_name] = columns
        
        try:
            # Create table if it doesn't exist
            if not self.loader.client.table_exists(table_name):
                self.loader.client.create_table(table_name, columns)
                logger.info(f"[LOADER] Created table {table_name} with {len(columns)} columns")
            else:
                # Verify columns match
                existing_columns = set(self.loader.client.get_table_columns(table_name))
                new_columns = set(columns.keys())
                if new_columns - existing_columns:
                    logger.warning(f"[LOADER] Table {table_name} has new columns: {new_columns - existing_columns}")
            
            return table_name
            
        except Exception as e:
            logger.error(f"[LOADER ERROR] Failed to ensure table schema for {table_name}: {e}")
            return None

    def _flush_batch(self, table_name: str, source: str):
        """
        Flush batch buffer for a table.
        
        Args:
            table_name: Table name
            source: Source identifier
        """
        if table_name not in self.batch_buffers or not self.batch_buffers[table_name]:
            return
        
        batch = self.batch_buffers[table_name]
        start_time = time.time()
        
        try:
            # Insert batch
            inserted = self.loader.client.insert_batch(table_name, batch, self.batch_size)
            
            # Update statistics
            self.loaded_count += inserted
            if source not in self.source_stats:
                self.source_stats[source] = {"loaded": 0, "failed": 0}
            self.source_stats[source]["loaded"] += inserted
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Publish success status
            status_message = {
                "source": source,
                "table": table_name,
                "status": "success",
                "row_count": inserted,
                "load_duration_ms": duration_ms
            }
            self.producer.send("load_rows_topic", status_message)
            
            logger.info(f"[LOADER] Flushed batch: {inserted} rows to {table_name} in {duration_ms}ms")
            
            # Clear batch
            self.batch_buffers[table_name] = []
            
        except Exception as e:
            self.error_count += len(batch)
            if source not in self.source_stats:
                self.source_stats[source] = {"loaded": 0, "failed": 0}
            self.source_stats[source]["failed"] += len(batch)
            
            logger.error(f"[LOADER ERROR] Failed to flush batch for {table_name}: {e}")
            
            # Publish error status
            error_message = {
                "source": source,
                "table": table_name,
                "status": "error",
                "error": str(e),
                "row_count": len(batch)
            }
            self.producer.send("load_rows_topic", error_message)
            
            # Clear batch on error (rows are lost, but pipeline continues)
            self.batch_buffers[table_name] = []

    def _emit_loading_metadata(self, source: str):
        """Emit loading metadata to metadata_topic."""
        if source not in self.source_stats:
            return
        
        stats = self.source_stats[source]
        table_name = self._sanitize_table_name(source)
        
        metadata = MetadataSchema.create_loading_metadata(
            source_id=source,
            table_name=table_name,
            rows_loaded=stats["loaded"],
            rows_failed=stats["failed"],
            errors=[]  # Can be enhanced to track specific errors
        )
        
        self.producer.send("metadata_topic", metadata)
        logger.info(f"[LOADER] Emitted loading metadata for {source}")

    def process_row(self, message: Dict[str, Any]):
        """
        Process a single row and add to batch buffer.
        
        Args:
            message: Message from clean_rows_topic
        """
        source = message.get("source", "unknown")
        row_data = message.get("data", {})
        
        if not row_data:
            logger.debug(f"[LOADER] Skipping empty row from {source}")
            return
        
        try:
            # Ensure table schema exists
            table_name = self._ensure_table_schema(source, row_data)
            
            if not table_name:
                self.error_count += 1
                logger.error(f"[LOADER] Failed to get table name for {source}")
                return
            
            # Add to batch buffer
            self.batch_buffers[table_name].append(row_data)
            
            # Flush if batch is full
            if len(self.batch_buffers[table_name]) >= self.batch_size:
                self._flush_batch(table_name, source)
            
            # Emit metadata periodically
            if self.loaded_count % self.metadata_interval == 0 and self.loaded_count > 0:
                self._emit_loading_metadata(source)
                logger.info(f"[LOADER] Processed {self.loaded_count} rows (errors: {self.error_count})")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"[LOADER ERROR] Failed to process row from {source}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def listen(self):
        """
        Listen to clean_rows_topic and process messages with batch loading.
        Flushes remaining batches on completion.
        """
        logger.info("[LOADER] Listening to clean_rows_topic...")
        
        try:
            for message in self.consumer.listen():
                self.process_row(message)
        except KeyboardInterrupt:
            logger.info("[LOADER] Shutting down...")
        except Exception as e:
            logger.error(f"[LOADER] Fatal error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # Flush all remaining batches
            logger.info("[LOADER] Flushing remaining batches...")
            for table_name in list(self.batch_buffers.keys()):
                if self.batch_buffers[table_name]:
                    # Extract source from table name (approximate)
                    source = table_name.replace("_", ".")
                    self._flush_batch(table_name, source)
            
            # Emit final metadata for all sources
            for source in self.source_stats.keys():
                self._emit_loading_metadata(source)
            
            logger.info(f"[LOADER] Final stats - Loaded: {self.loaded_count}, Errors: {self.error_count}")


def start_listener():
    """Entry point for the Kafka listener"""
    print("[LOADER] Starting clean row listener...")
    listener = CleanRowListener()
    listener.listen()
