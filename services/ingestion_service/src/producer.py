import logging
import os
import sys

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from src.core.config import Config

# Path Configuration
# Ensures that 'src' can be imported regardless of where the script is run from

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Logging Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TransactionProducer")


def delivery_report(err, msg):
    """
    Callback function called once for each message produced to indicate
    delivery result. Delivery reports are triggered by poll() or flush().
    """
    if err is not None:
        logger.error(f"❌ Delivery failed for record {msg.key()}: {err}")
    else:
        logger.info(
            f"✅ Message delivered to {msg.topic()} [partition {msg.partition()}]"
        )


def produce_test_messages():
    logger.info("🚀 Initializing Kafka Producer and Schema Registry...")

    # 1. Setup Schema Registry Client
    sr_conf = {
        "url": Config.SCHEMA_REGISTRY_URL,
        "basic.auth.user.info": f"{Config.SCHEMA_REGISTRY_API_KEY}:{Config.SCHEMA_REGISTRY_API_SECRET}",
    }
    try:
        schema_registry_client = SchemaRegistryClient(sr_conf)
    except Exception as e:
        logger.error(f"Failed to connect to Schema Registry: {e}")
        return

    # 2. Load Avro Schema from file
    # We use the exact same .avsc file the consumer uses
    schema_path = os.path.join(current_dir, "models", "transaction.avsc")
    try:
        with open(schema_path, "r") as f:
            schema_str = f.read()
    except FileNotFoundError:
        logger.error(f"Could not find schema file at {schema_path}")
        return

    # 3. Initialize the Avro Serializer
    # This object handles the "Magic Byte" and Schema ID automatically
    avro_serializer = AvroSerializer(schema_registry_client, schema_str)

    # 4. Setup the Kafka Producer
    producer_conf = {
        "bootstrap.servers": Config.KAFKA_BOOTSTRAP_SERVERS,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": Config.KAFKA_API_KEY,
        "sasl.password": Config.KAFKA_API_SECRET,
    }
    producer = Producer(producer_conf)

    # 5. Define Test Cases
    # We send one VALID message and two INVALID messages to test the Consumer's Pydantic logic
    test_messages = [
        {
            "type": "VALID",
            "data": {
                "transaction_id": "TX-10001",
                "timestamp": "2025-10-27T10:30:00Z",
                "channel": "CARD_NOT_PRESENT",
                "amount": 1250.00,
                "currency": "USD",
                "merchant": {
                    "id": "M-8721",
                    "name": "Luxury Watches Online",
                    "country": "CH",
                },
                "payer": {
                    "account_id": "U-9981",
                    "pan_last": "4821",
                    "ip_address": "192.168.1.1",
                    "device_id": "DEV-5509",
                },
            },
        },
        {
            "type": "INVALID_AMOUNT",
            "data": {
                "transaction_id": "TX-ERR-01",
                "timestamp": "2025-10-27T11:00:00Z",
                "channel": "POS",
                "amount": -50.00,  # Should fail: amount must be > 0
                "currency": "USD",
                "merchant": {"id": "M-1111", "name": "Coffee Shop", "country": "US"},
                "payer": {
                    "account_id": "U-2222",
                    "pan_last": "1234",
                    "ip_address": "1.1.1.1",
                    "device_id": "DEV-111",
                },
            },
        },
        {
            "type": "INVALID_CURRENCY",
            "data": {
                "transaction_id": "TX-ERR-02",
                "timestamp": "2025-10-27T12:00:00Z",
                "channel": "WEB",
                "amount": 100.00,
                "currency": "USDOLLARS",  # Should fail: length > 3
                "merchant": {"id": "M-1111", "name": "Coffee Shop", "country": "US"},
                "payer": {
                    "account_id": "U-2222",
                    "pan_last": "1234",
                    "ip_address": "1.1.1.1",
                    "device_id": "DEV-111",
                },
            },
        },
    ]

    logger.info("Sending messages to Kafka...")

    for item in test_messages:
        msg_type = item["type"]
        data = item["data"]

        try:
            ctx = SerializationContext(
                Config.KAFKA_TOPIC_TRANSACTIONS, MessageField.VALUE
            )

            binary_data = avro_serializer(data, ctx)
            # The AvroSerializer converts the dict to binary and adds the MAGIC BYTE
            # binary_data = avro_serializer(data, Config.KAFKA_TOPIC_TRANSACTIONS)

            # Produce the binary message to Kafka
            producer.produce(
                Config.KAFKA_TOPIC_TRANSACTIONS,
                value=binary_data,
                on_delivery=delivery_report,  # Trigger the callback on success/fail
            )
            logger.info(
                f"Successfully queued {msg_type} message: {data['transaction_id']}"
            )
        except Exception as e:
            logger.error(f"Failed to serialize {msg_type}: {e}")

    # IMPORTANT: flush() blocks until all messages are actually sent to the server
    producer.flush()
    logger.info("✅ All test messages processed. Check your Consumer logs!")


if __name__ == "__main__":
    produce_test_messages()
