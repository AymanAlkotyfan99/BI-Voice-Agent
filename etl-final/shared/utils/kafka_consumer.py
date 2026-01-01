import json
import os
import time
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from typing import Generator, Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaMessageConsumer:
    def __init__(self, topic: str, consumer_group: Optional[str] = None, validate_messages: bool = True):
        self.topic = topic
        self.validate_messages = validate_messages
        self.consumer_group = consumer_group or f"{topic}_consumer_group"
        self.servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.consumer = None

    def connect(self):
        """Connect to Kafka with infinite retry."""
        while True:
            try:
                logger.info(
                    f"[Kafka Consumer] Connecting to {self.servers}, topic={self.topic}, group={self.consumer_group}"
                )
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.servers,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id=self.consumer_group,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000,
                )
                logger.info("[Kafka Consumer] Connected successfully")
                break
            except Exception as e:
                logger.warning(f"[Kafka Consumer] Kafka not ready, retrying in 5s: {e}")
                time.sleep(5)

    def _validate_message(self, message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
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
            if self.topic in validators:
                return validators[self.topic](message)
            return True, None
        except Exception as e:
            return False, str(e)

    def listen(self) -> Generator[Dict[str, Any], None, None]:
        if self.consumer is None:
            self.connect()

        logger.info(f"[Kafka Consumer] Listening on topic: {self.topic}")

        while True:
            try:
                for msg in self.consumer:
                    message = msg.value
                    if self.validate_messages:
                        is_valid, error = self._validate_message(message)
                        if not is_valid:
                            logger.error(f"[Kafka Consumer] Invalid message: {error}")
                            continue
                    yield message
            except KafkaError as e:
                logger.error(f"[Kafka Consumer] Kafka error, reconnecting: {e}")
                time.sleep(5)
                self.connect()
            except Exception as e:
                logger.error(f"[Kafka Consumer] Unexpected error, reconnecting: {e}")
                time.sleep(5)
                self.connect()

    def close(self):
        if self.consumer:
            self.consumer.close()
