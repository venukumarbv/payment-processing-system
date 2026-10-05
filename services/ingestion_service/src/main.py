import logging
import time

from confluent_kafka import Consumer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from pydantic import ValidationError
from src.core.config import Config
from src.models.transactions import TransactionModel
from src.repository.db_repo import TransactionRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestionService")

# Kafka config
kafka_config = {
    "bootstrap.servers": Config.KAFKA_BOOTSTRAP_SERVERS,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": Config.KAFKA_API_KEY,
    "sasl.password": Config.KAFKA_API_SECRET,
    "group.id": Config.KAFKA_GROUP_ID,
    "auto.offset.reset": "latest",
}

# Schema registry Config
sr_conf = {
    "url": Config.SCHEMA_REGISTRY_URL,
    "basic.auth.user.info": f"{Config.SCHEMA_REGISTRY_API_KEY}:{Config.SCHEMA_REGISTRY_API_SECRET}",
}

# Consumer
consumer = Consumer(kafka_config)

# Producer
producer = Producer(
    {
        "bootstrap.servers": Config.KAFKA_BOOTSTRAP_SERVERS,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": Config.KAFKA_API_KEY,
        "sasl.password": Config.KAFKA_API_SECRET,
    }
)

# Initilize AVRO Deserializer
sr_client = SchemaRegistryClient(sr_conf)

with open("services/ingestion_service/src/models/transaction.avsc") as f:
    schema_str = f.read()

# De serialize
avro_deserializer = AvroDeserializer(sr_client, schema_str)

db_repo = TransactionRepository()


def publish_to_error_topic(msg_value, error_msg):

    logger.error(f"Routing to Error Topic: {error_msg}")

    producer.produce(Config.KAFKA_TOPIC_ERRORS, value=msg_value)
    producer.flush()


def process_message(msg_value):
    try:
        # Deserialize binary Avro to Python Dict
        data = avro_deserializer(msg_value, None)

        logger.info(f"Received transaction: {data}")

        # Validate with Pydantic
        txn = TransactionModel(**data)

        # Persist with 3 retry Mechanism (Exception)
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            if db_repo.save_transaction(txn):
                logger.info(f" Success: {txn.transaction_id} Saved to DB")
                return True
            logger.warning(
                f"Attempt {attempt} failed for {txn.transaction_id}. Retrying..."
            )
            time.sleep(2**attempt)

        publish_to_error_topic(msg_value, "DB persistence failed after 3 retries")
        return False

    except (ValidationError, Exception) as e:
        publish_to_error_topic(msg_value, f"Validating/Parsing Error: {str(e)}")
        return False


def main():
    consumer.subscribe([Config.KAFKA_TOPIC_TRANSACTIONS])
    logger.info("Ingestion service started. Polling Avro Messages...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka Error: {msg.error()}")
                continue
            process_message(msg.value())

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
