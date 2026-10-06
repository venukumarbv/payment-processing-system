from sqlalchemy import text
from sqlalchemy.orm import Session


class ReadRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_transactions(self, txn_id: str):
        # SQL query statements
        query = text("""
            SELECT
                t.*,
                m.MerchantID as m_id, m.MerchantName, m.CountryCode, m.IsActive as m_active, m.CreatedAt as m_created, m.UpdatedAt as m_updated,
                p.PayerAccountID as p_id, p.PanLast4, p.IPAddress, p.DeviceID, p.IsActive as p_active, p.CreatedAt as p_created, p.UpdatedAt as p_updated
            FROM Transactions t
            JOIN Merchants m ON t.MerchantID = m.MerchantID
            JOIN Payers p ON t.PayerAccountID = p.PayerAccountID
            WHERE t.TransactionID = :tid

            """)

        result = self.db.execute(query, {"tid": txn_id}).fetchone()

        if not result:
            return None

        # Map the flat SQL row into the Nested Dictionary structure
        # This matches the TransactionResponse Pydantic model
        return {
            "TransactionID": result.TransactionID,
            "TransactionTimestamp": result.TransactionTimestamp,
            "Channel": result.Channel,
            "Amount": result.Amount,
            "Currency": result.Currency,
            "StatusID": result.StatusID,
            "merchant": {
                "MerchantID": result.m_id,
                "MerchantName": result.MerchantName,
                "CountryCode": result.CountryCode,
                "IsActive": result.m_active,
                "CreatedAt": result.m_created,
                "UpdatedAt": result.m_updated,
            },
            "payer": {
                "PayerAccountID": result.p_id,
                "PanLast4": result.PanLast4,
                "IPAddress": result.IPAddress,
                "DeviceID": result.DeviceID,
                "IsActive": result.p_active,
                "CreatedAt": result.p_created,
                "UpdatedAt": result.p_updated,
            },
        }

    def get_top_merchants(self, start: str, end: str):
        query = text("""
            SELECT TOP 5 m.MerchantName, SUM(t.Amount) as TotalVolume
            FROM Transactions t
            JOIN Merchants m ON t.MerchantID = m.MerchantID
            WHERE t.TransactionTimestamp BETWEEN :start AND :end
            GROUP BY m.MerchantName
            ORDER BY TotalVolume DESC
        """)
        return self.db.execute(query, {"start": start, "end": end}).fetchall()
