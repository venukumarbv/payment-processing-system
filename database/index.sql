CREATE INDEX IX_Transactions_Timestamp_Merchant ON Transactions (TranactionTimestamp, MerchantID) INCLUDE (Amount);

CREATE INDEX IX_Transactions_PayerID ON Transactions (PayerAccountID);
CREATE INDEX IX_Transactions_MerchantID ON Transactions (MerchantID);
