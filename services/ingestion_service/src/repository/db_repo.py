from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import Config
from src.models.transactions import TransactionModel

# Create Engine with connection pooling for scalability
engine = create_engine(
    Config.DATABASE_URL, pool_size=10, max_overflow=20, pool_pre_ping=True
)

SessionLocal = sessionmaker(build=engine)


class TransactionRepository:
    def save_transaction(self, txn: TransactionModel):
        session = SessionLocal
        try:
            # UPSERT Merchant table
            session.execute(
                text("""
                IF NOT EXISTS (SELECT 1 FROM Merchants WHERE MerchantID = :id)
                INSERT INTO Merchants (MerchantID, MerchantName, CountryCode)
                VALUES (:id, :name, :country)"""),
                {
                    "id": txn.merchant.id,
                    "name": txn.merchant.name,
                    "country": txn.merchant.country,
                },
            )

            # UPSERT Payer Table

            session.execute(
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

            # INSERT Transaction table
            session.execute(
                text("""INSERT INTO Transactions (
                TransactionID,
                TransactionTimestamp,
                Channel,
                Amount,
                Currency,
                MerchantID,
                PayerAccountID,
                StatusID
                )
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
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"DB Error: {e}")
            return False

        finally:
            session.close()
