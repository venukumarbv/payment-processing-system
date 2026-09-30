IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TransactionStatuses]') AND type in (N'U'))
BEGIN
    CREATE TABLE TransactionStatuses (
        StatusID INT PRIMARY KEY,
        StatusName NVARCHAR(20) NOT NULL UNIQUE
    );
    INSERT INTO TransactionStatuses (StatusID, StatusName) VALUES (1, 'PENDING'), (2, 'SUCCESS'), (3, 'FAILED');
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[UserRoles]') AND type in (N'U'))
BEGIN
    CREATE TABLE UserRoles (
        RoleID INT PRIMARY KEY,
        RoleName NVARCHAR(20) NOT NULL UNIQUE
    );
    INSERT INTO UserRoles (RoleID, RoleName) VALUES (1, 'Admin'), (2, 'Viewer'), (3, 'Manager');
END


IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Merchants]') AND type in (N'U'))
BEGIN
    CREATE TABLE Merchants (
        MerchantID NVARCHAR(50) PRIMARY KEY,
        MerchantName NVARCHAR(255) NOT NULL,
        CountryCode NCHAR(2) NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1,
        CreatedAt DATETIME2 DEFAULT GETDATE(),
        UpdatedAt DATETIME2 DEFAULT GETDATE()
    );
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Payers]') AND type in (N'U'))
BEGIN
    CREATE TABLE Payers (
        PayerAccountID NVARCHAR(50) PRIMARY KEY,
        PanLast4 NCHAR(4) NOT NULL,
        IPAddress NVARCHAR(45),
        DeviceID NVARCHAR(100),
        IsActive BIT NOT NULL DEFAULT 1,
        CreatedAt DATETIME2 DEFAULT GETDATE(),
        UpdatedAt DATETIME2 DEFAULT GETDATE()
    );
END

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Users]') AND type in (N'U'))
BEGIN
    CREATE TABLE Users (
        UserID INT PRIMARY KEY IDENTITY(1,1),
        Username NVARCHAR(50) UNIQUE NOT NULL,
        HashedPassword NVARCHAR(255) NOT NULL,
        RoleID INT NOT NULL DEFAULT 2,
        CreatedAt DATETIME2 DEFAULT GETDATE(),
        CONSTRAINT FK_Users_Role FOREIGN KEY (RoleID) REFERENCES UserRoles(RoleID)
    );
END


IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Transactions]') AND type in (N'U'))
BEGIN
    CREATE TABLE Transactions (
        TransactionID NVARCHAR(50) PRIMARY KEY,
        TransactionTimestamp DATETIME2 NOT NULL,
        Channel NVARCHAR(50),
        Amount DECIMAL(18, 2) NOT NULL,
        Currency NCHAR(3) NOT NULL,
        MerchantID NVARCHAR(50) NOT NULL,
        PayerAccountID NVARCHAR(50) NOT NULL,
        StatusID INT NOT NULL DEFAULT 1,
        
        CONSTRAINT FK_Transactions_Merchants FOREIGN KEY (MerchantID) REFERENCES Merchants(MerchantID),
        CONSTRAINT FK_Transactions_Payers FOREIGN KEY (PayerAccountID) REFERENCES Payers(PayerAccountID),
        CONSTRAINT FK_Transactions_Status FOREIGN KEY (StatusID) REFERENCES TransactionStatuses(StatusID)
    );
END