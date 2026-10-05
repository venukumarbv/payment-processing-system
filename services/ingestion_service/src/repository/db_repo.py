import urllib.parse

from sqlalchemy import create_engine, text
from src.core.config import Config

# 1. Build the raw ODBC connection string exactly as the Driver expects
# We use f-strings to ensure no spaces or weird characters are added
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={Config.DB_SERVER};"
    f"DATABASE={Config.DB_NAME};"
    f"UID={Config.DB_USER};"
    f"PWD={Config.DB_PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# 2. URL-encode the connection string for SQLAlchemy
params = urllib.parse.quote_plus(connection_string)

# 3. Create the engine using the 'odbc_connect' parameter
# This bypasses the SQLAlchemy URL parser and sends the string directly to the driver
engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)


class TransactionRepository:
    def save_transaction(self, txn):
        # Use engine.connect() directly to avoid the Session/__init__ bug
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # 1. Upsert Merchant
                connection.execute(
                    text("""
                    IF NOT EXISTS (SELECT 1 FROM Merchants WHERE MerchantID = :id)
                    INSERT INTO Merchants (MerchantID, MerchantName, CountryCode)
                    VALUES (:id, :name, :country)
                """),
                    {
                        "id": txn.merchant.id,
                        "name": txn.merchant.name,
                        "country": txn.merchant.country,
                    },
                )

                # 2. Upsert Payer
                connection.execute(
                    text("""
                    IF NOT EXISTS (SELECT 1 FROM Payers WHERE PayerAccountID = :id)
                    INSERT INTO Payers (PayerAccountID, PanLast4, IPAddress, DeviceID)
                    VALUES (:id, :pan, :ip, :dev)
                """),
                    {
                        "id": txn.payer.account_id,
                        "pan": txn.payer.pan_last,
                        "ip": txn.payer.ip_address,
                        "dev": txn.payer.device_id,
                    },
                )

                # 3. Insert Transaction
                connection.execute(
                    text("""
                    INSERT INTO Transactions (TransactionID, TransactionTimestamp, Channel, Amount, Currency, MerchantID, PayerAccountID, StatusID)
                    VALUES (:tid, :ts, :ch, :amt, :cur, :mid, :pid, 2)
                """),
                    {
                        "tid": txn.transaction_id,
                        "ts": txn.timestamp,
                        "ch": txn.channel,
                        "amt": txn.amount,
                        "cur": txn.currency,
                        "mid": txn.merchant.id,
                        "pid": txn.payer.account_id,
                    },
                )

                trans.commit()
                return True
            except Exception as e:
                trans.rollback()
                print(f"❌ DB Error: {e}")
                return False
