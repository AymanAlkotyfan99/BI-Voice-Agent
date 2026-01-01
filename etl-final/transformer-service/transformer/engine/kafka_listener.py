"""
Enhanced Transformer Service Kafka Listener
Processes extracted rows, applies cleaning/transformation, and emits metadata
"""
import logging
from datetime import datetime
from typing import Dict, Any, List
from shared.utils.kafka_consumer import KafkaMessageConsumer
from shared.utils.kafka_producer import KafkaMessageProducer
from shared.utils.metadata_schema import MetadataSchema
from .transformer_logic import TransformerLogic
from .cleaning_rules import CleaningRules

logger = logging.getLogger(__name__)


class RawRowListener:
    """
    Enhanced listener for extracted_rows_topic.
    
    Features:
    - Comprehensive cleaning and transformation
    - Metadata emission
    - Error handling and recovery
    - Batch processing statistics
    """

    def __init__(self):
        self.consumer = KafkaMessageConsumer("extracted_rows_topic")
        self.producer = KafkaMessageProducer()
        self.transformer = TransformerLogic()
        self.cleaner = CleaningRules()
        
        # Statistics tracking
        self.processed_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.warnings: List[str] = []
        self.current_source = None
        self.source_stats: Dict[str, Dict[str, int]] = {}
        
        # Metadata emission interval
        self.metadata_interval = 1000  # Emit metadata every 1000 rows

    def _update_source_stats(self, source: str, success: bool):
        """Update statistics for a source."""
        if source not in self.source_stats:
            self.source_stats[source] = {"processed": 0, "success": 0, "failed": 0}
        self.source_stats[source]["processed"] += 1
        if success:
            self.source_stats[source]["success"] += 1
        else:
            self.source_stats[source]["failed"] += 1

    def _emit_cleaning_metadata(self, source: str):
        """Emit cleaning metadata to metadata_topic."""
        if source not in self.source_stats:
            return
        
        stats = self.source_stats[source]
        metadata = MetadataSchema.create_cleaning_metadata(
            source_id=source,
            rows_processed=stats["processed"],
            rows_cleaned=stats["success"],
            rows_failed=stats["failed"],
            cleaning_rules_applied=[
                "remove_null_fields",
                "trim_strings",
                "normalize_whitespace",
                "handle_empty_strings",
                "coerce_types",
                "validate_row"
            ],
            validation_warnings=self.warnings[-10:] if self.warnings else []  # Last 10 warnings
        )
        
        self.producer.send("metadata_topic", metadata)
        logger.info(f"[TRANSFORMER] Emitted cleaning metadata for {source}")

    def process_row(self, message: Dict[str, Any]):
        """
        Clean and transform a single row with comprehensive error handling.
        
        Args:
            message: Message from extracted_rows_topic
        """
        source = message.get("source", "unknown")
        self.current_source = source
        
        try:
            # Extract row data
            row_data = message.get("data", {})
            
            if not row_data:
                logger.warning(f"[TRANSFORMER] Empty row data from {source}")
                self.failed_count += 1
                self._update_source_stats(source, False)
                return
            
            # Apply cleaning rules (returns tuple: cleaned_row, warnings)
            cleaned_row, cleaning_warnings = self.cleaner.apply_all(row_data)
            self.warnings.extend(cleaning_warnings)
            
            # Apply transformations (returns tuple: transformed_row, warnings)
            transformed_row, transform_warnings = self.transformer.transform_row(cleaned_row)
            self.warnings.extend(transform_warnings)
            
            # Skip if row is empty after cleaning
            if not transformed_row or all(v is None or v == "" for v in transformed_row.values()):
                logger.debug(f"[TRANSFORMER] Skipping empty row after cleaning")
                self.failed_count += 1
                self._update_source_stats(source, False)
                return
            
            # Prepare cleaned message
            clean_message = {
                "source": source,
                "data": transformed_row
            }
            
            # Add table info if present (for database sources)
            if "table" in message:
                clean_message["table"] = message["table"]
            
            # Add row_id if present (for file sources)
            if "row_id" in message:
                clean_message["row_id"] = message["row_id"]
            
            # Publish to clean_rows_topic
            success = self.producer.send("clean_rows_topic", clean_message)
            
            if success:
                self.processed_count += 1
                self.success_count += 1
                self._update_source_stats(source, True)
            else:
                self.failed_count += 1
                self._update_source_stats(source, False)
                logger.error(f"[TRANSFORMER] Failed to send cleaned row to Kafka")
            
            # Emit metadata periodically
            if self.processed_count % self.metadata_interval == 0:
                self._emit_cleaning_metadata(source)
                logger.info(f"[TRANSFORMER] Processed {self.processed_count} rows (success: {self.success_count}, failed: {self.failed_count})")
            
        except Exception as e:
            self.failed_count += 1
            self._update_source_stats(source, False)
            logger.error(f"[TRANSFORMER ERROR] Failed to process row from {source}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def listen(self):
        """
        Listen to extracted_rows_topic and process messages.
        Emits final metadata on completion.
        """
        logger.info("[TRANSFORMER] Listening to extracted_rows_topic...")
        
        try:
            for message in self.consumer.listen():
                self.process_row(message)
        except KeyboardInterrupt:
            logger.info("[TRANSFORMER] Shutting down...")
        except Exception as e:
            logger.error(f"[TRANSFORMER] Fatal error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # Emit final metadata for all sources
            for source in self.source_stats.keys():
                self._emit_cleaning_metadata(source)
            logger.info(f"[TRANSFORMER] Final stats - Processed: {self.processed_count}, Success: {self.success_count}, Failed: {self.failed_count}")


def start_listener():
    """Entry point for the Kafka listener."""
    logger.info("[TRANSFORMER] Starting row listener...")
    listener = RawRowListener()
    listener.listen()
