"""
Enhanced Extractor Service Kafka Listener
Extracts data from files/databases and emits comprehensive metadata
"""
import os
import sys
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from shared.utils.kafka_consumer import KafkaMessageConsumer
from shared.utils.kafka_producer import KafkaMessageProducer
from shared.utils.metadata_schema import MetadataSchema
from .db_connector import DBConnector
from .row_extractor import RowExtractor

logger = logging.getLogger(__name__)


class ConnectionListener:
    """
    Listens to connection_topic and extracts data from files or databases
    """

    def __init__(self):
        self.consumer = KafkaMessageConsumer("connection_topic")
        self.producer = KafkaMessageProducer()
        self.db_connector = DBConnector()
        self.row_extractor = RowExtractor()

    def process_file(self, message: Dict[str, Any]):
        """
        Extract schema and rows from a file with metadata emission.
        
        Args:
            message: Message from connection_topic
        """
        source_id = message.get("filename", "unknown")
        file_path = message.get("path")
        
        try:
            logger.info(f"[EXTRACTOR] Processing file: {source_id}")
            
            # Read file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                logger.error(f"[EXTRACTOR ERROR] Unsupported file type: {file_path}")
                return
            
            # Extract schema
            schema = {
                "source": source_id,
                "type": "file",
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "row_count": len(df)
            }
            
            # Publish schema
            self.producer.send("schema_topic", schema)
            logger.info(f"[EXTRACTOR] Published schema: {len(schema['columns'])} columns, {len(df)} rows")
            
            # Emit schema metadata
            schema_metadata = MetadataSchema.create_schema_metadata(
                source_id=source_id,
                schema=schema,
                row_count=len(df)
            )
            self.producer.send("metadata_topic", schema_metadata)
            
            # Extract and publish rows
            rows_successful = 0
            rows_failed = 0
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    row_data = {
                        "source": source_id,
                        "row_id": int(idx),
                        "data": row.to_dict()
                    }
                    if self.producer.send("extracted_rows_topic", row_data):
                        rows_successful += 1
                    else:
                        rows_failed += 1
                        errors.append(f"Failed to send row {idx}")
                except Exception as e:
                    rows_failed += 1
                    errors.append(f"Row {idx}: {str(e)}")
                    logger.warning(f"[EXTRACTOR] Error processing row {idx}: {e}")
            
            logger.info(f"[EXTRACTOR] Published {rows_successful} rows (failed: {rows_failed})")
            
            # Emit extraction metadata
            extraction_metadata = MetadataSchema.create_extraction_metadata(
                source_id=source_id,
                rows_processed=len(df),
                rows_successful=rows_successful,
                rows_failed=rows_failed,
                errors=errors[:10] if errors else []  # First 10 errors
            )
            self.producer.send("metadata_topic", extraction_metadata)
            
        except Exception as e:
            logger.error(f"[EXTRACTOR ERROR] Failed to process file {source_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def process_database(self, message: Dict[str, Any]):
        """
        Extract schema and rows from a database with metadata emission.
        
        Args:
            message: Message from connection_topic
        """
        try:
            db_config = {
                "db_type": message["db_type"],
                "host": message["host"],
                "user": message["user"],
                "password": message["password"],
                "database": message["database"],
                "port": message["port"]
            }
            
            source_id = f"{db_config['database']}"
            logger.info(f"[EXTRACTOR] Connecting to {db_config['db_type']} database: {source_id}")
            
            # Connect to database
            connection = self.db_connector.connect(db_config)
            cursor = connection.cursor()
            
            # Get list of tables
            if db_config["db_type"] == "mysql":
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
            elif db_config["db_type"] == "postgres":
                cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
                tables = [row[0] for row in cursor.fetchall()]
            else:
                logger.error(f"[EXTRACTOR ERROR] Unsupported database type")
                return
            
            logger.info(f"[EXTRACTOR] Found {len(tables)} tables")
            
            # Extract schema for each table
            for table in tables:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                columns = [desc[0] for desc in cursor.description]
                
                table_source = f"{db_config['database']}.{table}"
                schema = {
                    "source": table_source,
                    "type": "database",
                    "table": table,
                    "columns": columns,
                    "db_type": db_config["db_type"]
                }
                
                self.producer.send("schema_topic", schema)
                logger.info(f"[EXTRACTOR] Published schema for {table}: {len(columns)} columns")
                
                # Emit schema metadata
                schema_metadata = MetadataSchema.create_schema_metadata(
                    source_id=table_source,
                    schema=schema,
                    row_count=0  # Will be updated after extraction
                )
                self.producer.send("metadata_topic", schema_metadata)
            
            # Extract rows
            total_rows = 0
            rows_successful = 0
            rows_failed = 0
            errors = []
            
            for table, row in self.row_extractor.extract_rows(connection, tables):
                try:
                    table_source = f"{db_config['database']}.{table}"
                    row_data = {
                        "source": table_source,
                        "table": table,
                        "data": row
                    }
                    if self.producer.send("extracted_rows_topic", row_data):
                        rows_successful += 1
                    else:
                        rows_failed += 1
                    total_rows += 1
                except Exception as e:
                    rows_failed += 1
                    errors.append(f"Table {table}: {str(e)}")
                    logger.warning(f"[EXTRACTOR] Error extracting row from {table}: {e}")
            
            logger.info(f"[EXTRACTOR] Published {rows_successful} rows (failed: {rows_failed})")
            
            # Emit extraction metadata
            extraction_metadata = MetadataSchema.create_extraction_metadata(
                source_id=source_id,
                rows_processed=total_rows,
                rows_successful=rows_successful,
                rows_failed=rows_failed,
                errors=errors[:10] if errors else []
            )
            self.producer.send("metadata_topic", extraction_metadata)
            
            connection.close()
            
        except Exception as e:
            logger.error(f"[EXTRACTOR ERROR] Failed to process database: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def listen(self):
        """Listen to connection_topic and process messages"""
        logger.info("[EXTRACTOR] Listening to connection_topic...")
        try:
            for message in self.consumer.listen():
                logger.info(f"[EXTRACTOR] Received message: type={message.get('type')}")
                
                # Emit connection metadata
                connection_metadata = MetadataSchema.create_connection_metadata(
                    source_type=message.get("type", "unknown"),
                    source_id=message.get("filename") or message.get("database", "unknown"),
                    connection_info=message
                )
                self.producer.send("metadata_topic", connection_metadata)
                
                if message.get("type") == "file":
                    self.process_file(message)
                elif message.get("type") == "database":
                    self.process_database(message)
                else:
                    logger.error(f"[EXTRACTOR ERROR] Unknown message type: {message.get('type')}")
        except KeyboardInterrupt:
            logger.info("[EXTRACTOR] Shutting down...")
        except Exception as e:
            logger.error(f"[EXTRACTOR] Fatal error: {e}")
            import traceback
            logger.error(traceback.format_exc())


def start_listener():
    """Entry point for the Kafka listener"""
    logger.info("[EXTRACTOR] Starting connection listener...")
    listener = ConnectionListener()
    listener.listen()
