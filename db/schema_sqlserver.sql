-- Microsoft SQL Server Database DDL Schema for com.cth Enterprise Application

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
BEGIN
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(100) NOT NULL UNIQUE,
        email NVARCHAR(150) NOT NULL UNIQUE,
        password_hash NVARCHAR(255) NOT NULL,
        full_name NVARCHAR(150),
        is_admin BIT DEFAULT 0,
        is_locked BIT DEFAULT 0,
        failed_attempts INT DEFAULT 0,
        password_expiry_date DATETIME,
        otp_code NVARCHAR(10),
        otp_expiry DATETIME,
        created_at DATETIME DEFAULT GETDATE()
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'roles')
BEGIN
    CREATE TABLE roles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        role_name NVARCHAR(50) NOT NULL UNIQUE,
        description NVARCHAR(255)
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'audit_logs')
BEGIN
    CREATE TABLE audit_logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(100),
        action NVARCHAR(100) NOT NULL,
        details NVARCHAR(MAX),
        ip_address NVARCHAR(45),
        created_at DATETIME DEFAULT GETDATE()
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'report_configs')
BEGIN
    CREATE TABLE report_configs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(100) NOT NULL,
        description NVARCHAR(255),
        table_name NVARCHAR(100) NOT NULL,
        selected_fields NVARCHAR(MAX) NOT NULL,
        where_clause NVARCHAR(500),
        order_by NVARCHAR(200),
        created_by NVARCHAR(100),
        created_at DATETIME DEFAULT GETDATE()
    );
END;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'system_settings')
BEGIN
    CREATE TABLE system_settings (
        setting_key NVARCHAR(100) PRIMARY KEY,
        setting_value NVARCHAR(500) NOT NULL,
        description NVARCHAR(255)
    );
END;
