"""
Enhanced Kafka Producer with Message Validation and Error Handling
"""
import json
import os
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
from typing import Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class KafkaMessageProducer:
    """
    Enhanced Kafka message producer with validation, retries, and proper error handling.
    
    Features:
    - Message schema validation
    - Automatic retries with exponential backoff
    - Proper error logging
    - Connection pooling
    - Message acknowledgements
    """

    def __init__(self, validate_messages: bool = True):
        """
        Initialize Kafka producer.
        
        Args:
            validate_messages: Whether to validate message schemas before sending
        """
        servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.validate_messages = validate_messages

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                retries=5,
                acks='all',  # Wait for all replicas to acknowledge
                max_in_flight_requests_per_connection=1,  # Ensure ordering
                enable_idempotence=True,  # Prevent duplicate messages
                compression_type='gzip',  # Compress messages
                request_timeout_ms=30000,
                delivery_timeout_ms=120000,
            )
            logger.info(f"[Kafka Producer] Connected to {servers}")
        except Exception as e:
            logger.error(f"[Kafka Producer] Failed to connect: {e}")
            raise Exception(f"[Shared Kafka] Failed to connect: {e}")

    def _validate_message(self, topic: str, message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate message schema based on topic.
        
        Args:
            topic: Kafka topic name
            message: Message dict to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.validate_messages:
            return True, None
        
        try:
            from .message_validator import MessageValidator
            
            validators = {
                "connection_topic": MessageValidator.validate_connection_message,
                "schema_topic": MessageValidator.validate_schema_message,
                "extracted_rows_topic": MessageValidator.validate_extracted_row_message,
                "clean_rows_topic": MessageValidator.validate_clean_row_message,
                "load_rows_topic": MessageValidator.validate_load_status_message,
                "metadata_topic": MessageValidator.validate_metadata_message,
            }
            
            if topic in validators:
                return validators[topic](message)
            
            # Unknown topic - allow but warn
            logger.warning(f"[Kafka Producer] No validator for topic: {topic}")
            return True, None
            
        except Exception as e:
            logger.error(f"[Kafka Producer] Validation error: {e}")
            return False, str(e)

    def send(self, topic: str, message: Dict[str, Any], validate: Optional[bool] = None) -> bool:
        """
        Send message to Kafka topic with validation.
        
        Args:
            topic: Kafka topic name
            message: Message dict to send
            validate: Override validation flag (defaults to instance setting)
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Validate message if requested
        should_validate = validate if validate is not None else self.validate_messages
        if should_validate:
            is_valid, error = self._validate_message(topic, message)
            if not is_valid:
                logger.error(f"[Kafka Producer] Invalid message for {topic}: {error}")
                logger.error(f"[Kafka Producer] Message: {json.dumps(message, indent=2)}")
                return False
        
        try:
            future = self.producer.send(topic, message)
            record_metadata = future.get(timeout=10)
            logger.debug(f"[Kafka Producer] Sent to {topic} [partition={record_metadata.partition}, offset={record_metadata.offset}]")
            return True
        except KafkaError as e:
            logger.error(f"[Kafka Producer ERROR] Kafka error sending to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"[Kafka Producer ERROR] Unexpected error sending to {topic}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def flush(self):
        """Flush all pending messages."""
        try:
            self.producer.flush(timeout=30)
            logger.debug("[Kafka Producer] Flushed pending messages")
        except Exception as e:
            logger.error(f"[Kafka Producer] Error flushing: {e}")
    
    def close(self):
        """Close producer connection."""
        try:
            self.flush()
            self.producer.close()
            logger.info("[Kafka Producer] Closed connection")
        except Exception as e:
            logger.error(f"[Kafka Producer] Error closing: {e}")
