from shared.utils.kafka_consumer import KafkaMessageConsumer
from shared.utils.kafka_producer import KafkaMessageProducer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def start_listener():
    logger.info("[DETECTOR] Creating Kafka consumer...")
    consumer = KafkaMessageConsumer("extracted_rows_topic")
    producer = KafkaMessageProducer()

    logger.info("[DETECTOR] Listening to extracted_rows_topic")

    for message in consumer.listen():
        try:
            producer.send("clean_rows_topic", message)
            producer.send("metadata_topic", {
                "service": "detector",
                "status": "processed",
                "source": message.get("source")
            })
        except Exception as e:
            logger.error(f"[DETECTOR ERROR] {e}")

 