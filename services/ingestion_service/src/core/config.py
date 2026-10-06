import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # --- Kafka Cluster Config ---
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_TOPIC_TRANSACTIONS = "transactions"
    KAFKA_TOPIC_ERRORS = "transaction_errors"
    KAFKA_GROUP_ID = "ingestion_service_group"
    KAFKA_API_KEY = os.getenv("KAFKA_API_KEY")
    KAFKA_API_SECRET = os.getenv("KAFKA_API_SECRET")

    # --- Schema Registry Config ---
    SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL")
    SCHEMA_REGISTRY_API_KEY = os.getenv("SCHEMA_REGISTRY_API_KEY")
    SCHEMA_REGISTRY_API_SECRET = os.getenv("SCHEMA_REGISTRY_API_SECRET")

    # --- Database Config ---
    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DRIVER = "{ODBC Driver 18 for SQL Server}"

    server_formatted = DB_SERVER.replace(",", ":") if DB_SERVER else ""
    # SQLAlchemy Connection String
    # DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver={DB_DRIVER}"  # noqa: E501
    DATABASE_URL = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{server_formatted}/{DB_NAME}"
        f"?driver={DB_DRIVER}"
    )
