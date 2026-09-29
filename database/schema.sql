CREATE TABLE Merchants(
    MerchantId NVARCHAR(50)  PRIMARY KEY,
    MerchantName NVARCHAR(255) NOT NULL,
    CountryCode NCHAR(2) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE Payers(
    PayerAccountID NVARCHAR(50) PRIMARY KEY,
    PanLast4 NCHAR(4) NOT NULL,
    IpAddress NVARCHAR(45),
    DeviceId NVARCHAR(100),
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE Transactions(
    TransactionId NVARCHAR(50) PRIMARY KEY,
    TranactionTimestamp DATETIME2 NOT NULL,
    Channel NVARCHAR(50), -- check whether it can be an Enum
    Amount DECIMAL(18,2) NOT NULL,
    Currency NCHAR(3) NOT NULL,-- check whether it can be an Enum
    
    -- Foreign keys definition 
    MerchantId NVARCHAR(50) NOT NULL,
    PayerAccountID NVARCHAR(50) NOT NULL,

    CONSTRAINT FK_Transactions_Merchants FOREIGN KEY (MerchantId) REFERENCES Merchants(MerchantId),
    CONSTRAINT FK_Transactions_Payers FOREIGN KEY (PayerAccountID) REFERENCES Payers(PayerAccountID)
);