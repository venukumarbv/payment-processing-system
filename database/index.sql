IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Transactions_Timestamp_Merchant' AND object_id = OBJECT_ID('Transactions'))
BEGIN
    CREATE INDEX IX_Transactions_Timestamp_Merchant 
    ON Transactions (TransactionTimestamp, MerchantID) 
    INCLUDE (Amount);
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Transactions_PayerID' AND object_id = OBJECT_ID('Transactions'))
BEGIN
    CREATE INDEX IX_Transactions_PayerID ON Transactions (PayerAccountID);
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Transactions_MerchantID' AND object_id = OBJECT_ID('Transactions'))
BEGIN
    CREATE INDEX IX_Transactions_MerchantID ON Transactions (MerchantID);
END