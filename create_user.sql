-- SQL Script to create climbing_user on FroggyDB
-- Run this as a user with server admin privileges (sa)

USE [master]
GO

-- Create login if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'climbing_user')
BEGIN
    CREATE LOGIN [climbing_user] WITH 
        PASSWORD = 'hoosierheights', 
        DEFAULT_DATABASE = [FroggyDB], 
        CHECK_EXPIRATION = OFF, 
        CHECK_POLICY = OFF
    PRINT 'Login climbing_user created.'
END
ELSE
BEGIN
    PRINT 'Login climbing_user already exists.'
END
GO

-- Switch to FroggyDB
USE [FroggyDB]
GO

-- Create user for the login if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'climbing_user')
BEGIN
    CREATE USER [climbing_user] FOR LOGIN [climbing_user]
    PRINT 'User climbing_user created in FroggyDB.'
END
ELSE
BEGIN
    PRINT 'User climbing_user already exists in FroggyDB.'
END
GO

-- Grant necessary permissions
PRINT 'Granting permissions to climbing_user...'
ALTER ROLE [db_datareader] ADD MEMBER [climbing_user]
ALTER ROLE [db_datawriter] ADD MEMBER [climbing_user]
GO

-- Grant execute permission on stored procedures (if any)
GRANT EXECUTE TO [climbing_user]
GO

-- Grant additional permissions needed for the app
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO [climbing_user]
GO

PRINT 'All permissions granted to climbing_user.'
GO 