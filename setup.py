"""
Setup script for the Feeling Froggy app.
This script handles data migration and prepares the application for use.
"""

import os
import sys
import time
import pandas as pd
import pyodbc
from database import get_db_connection
from data_migration import execute_migration
from test_connection import test_connection

def verify_app_files():
    """Verify that all required application files exist."""
    print("Verifying application files...")
    required_files = [
        'app.py', 
        'database.py', 
        'frog_sounds.py', 
        'frog_identifier.py',
        'data/frog_species.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("All required files exist.")
        return True

def check_tables_exist():
    """Check if the required tables exist in the database."""
    print("Checking if required tables exist...")
    tables = ['frog_species', 'frog_calls']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for table in tables:
            cursor.execute(f"IF OBJECT_ID('{table}', 'U') IS NOT NULL SELECT 1 ELSE SELECT 0")
            result = cursor.fetchone()[0]
            if result == 0:
                print(f"Table {table} does not exist.")
                conn.close()
                return False
        
        conn.close()
        print("All required tables exist.")
        return True
    except Exception as e:
        print(f"Error checking tables: {e}")
        return False

def check_data_exists():
    """Check if data exists in the tables."""
    print("Checking if data exists in tables...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check frog_species
        cursor.execute("SELECT COUNT(*) FROM frog_species")
        species_count = cursor.fetchone()[0]
        
        # Check frog_calls
        cursor.execute("SELECT COUNT(*) FROM frog_calls")
        calls_count = cursor.fetchone()[0]
        
        conn.close()
        
        if species_count > 0 and calls_count > 0:
            print(f"Data exists: {species_count} frog species and {calls_count} frog calls found.")
            return True
        else:
            print("Data missing or incomplete.")
            return False
    except Exception as e:
        print(f"Error checking data: {e}")
        return False

def run_setup():
    """Run the complete setup process."""
    print("=" * 50)
    print("FEELING FROGGY APP SETUP")
    print("=" * 50)
    
    # Verify app files
    if not verify_app_files():
        print("ERROR: Some required files are missing. Setup failed.")
        return False
    
    # Test database connection
    print("\nTesting database connection...")
    if not test_connection():
        print("\nERROR: Database connection failed. Please ensure:")
        print("1. The SQL Server is running")
        print("2. The climbing_user exists with password 'hoosierheights'")
        print("3. The FroggyDB database exists")
        print("4. The user has appropriate permissions")
        print("\nYou can run the following DDL to create the user:")
        print("""
CREATE LOGIN [climbing_user] WITH PASSWORD = 'hoosierheights', 
    DEFAULT_DATABASE = [FroggyDB], CHECK_EXPIRATION = OFF, CHECK_POLICY = OFF;
USE [FroggyDB];
CREATE USER [climbing_user] FOR LOGIN [climbing_user];
ALTER ROLE [db_datareader] ADD MEMBER [climbing_user];
ALTER ROLE [db_datawriter] ADD MEMBER [climbing_user];
GRANT EXECUTE TO [climbing_user];
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO [climbing_user];
        """)
        return False
    
    # Check if tables exist
    if not check_tables_exist():
        print("NOTICE: Required tables are missing in the database.")
        print("Please run the database creation DDL script first and try again.")
        return False
    
    # Check if data exists
    data_exists = check_data_exists()
    if not data_exists:
        print("\nNOTICE: Data missing or incomplete. Running data migration...")
        if execute_migration():
            print("Data migration completed successfully.")
        else:
            print("WARNING: Data migration failed or was incomplete.")
            return False
    
    # Final verification
    if check_data_exists():
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("Run the app with: streamlit run app.py")
        print("=" * 50)
        return True
    else:
        print("\nERROR: Setup failed. Data verification failed.")
        return False

if __name__ == "__main__":
    run_setup() 