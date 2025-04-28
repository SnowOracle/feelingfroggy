"""
Test script to verify database connection to FroggyDB with climbing_user credentials.
"""

import pyodbc
import sys

def test_connection():
    """Test connection to FroggyDB database."""
    print("Testing connection to FroggyDB...")
    
    try:
        # Connection string for FroggyDB
        conn = pyodbc.connect(
            "DRIVER=/opt/homebrew/lib/libtdsodbc.so;"
            "SERVER=127.0.0.1;"
            "PORT=1433;"
            "DATABASE=FroggyDB;"
            "UID=climbing_user;"
            "PWD=hoosierheights;"
            "TDS_Version=7.4;"
        )
        
        # Execute a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        
        # Fetch the result
        row = cursor.fetchone()
        print("Connection successful!")
        print(f"SQL Server version: {row[0]}")
        
        # Try to access frog_species table
        try:
            cursor.execute("SELECT COUNT(*) FROM frog_species")
            species_count = cursor.fetchone()[0]
            print(f"Found {species_count} frog species in the database.")
            
            # Check if frog_calls table exists
            cursor.execute("SELECT COUNT(*) FROM frog_calls")
            calls_count = cursor.fetchone()[0]
            print(f"Found {calls_count} frog calls in the database.")
            
            # Additional permission test - try to insert a record
            if species_count > 0:
                try:
                    print("Testing write permissions...")
                    # Get a species ID to reference
                    cursor.execute("SELECT TOP 1 species_id FROM frog_species")
                    species_id = cursor.fetchone()[0]
                    
                    # Try to insert a test frog call
                    cursor.execute("""
                        IF NOT EXISTS (SELECT 1 FROM frog_calls WHERE audio_url = 'test_url')
                        INSERT INTO frog_calls (species_id, audio_url, description, created_at)
                        VALUES (?, 'test_url', 'Test frog call for connection test', GETDATE())
                    """, species_id)
                    conn.commit()
                    print("Write permissions verified successfully.")
                    
                    # Clean up test data
                    cursor.execute("DELETE FROM frog_calls WHERE audio_url = 'test_url'")
                    conn.commit()
                    print("Test data cleaned up.")
                except Exception as e:
                    print(f"Write permissions test failed: {e}")
        except Exception as e:
            print(f"Error accessing tables: {e}")
            print("Make sure the required tables exist in the database.")
        
        # Close connection
        conn.close()
        print("Connection test completed.")
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nPossible issues:")
        print("1. SQL Server is not running")
        print("2. The climbing_user login doesn't exist or has incorrect password")
        print("3. FroggyDB database doesn't exist")
        print("4. The climbing_user doesn't have access to FroggyDB")
        print("5. The ODBC driver is not correctly installed")
        print("\nPlease run the create_user.sql script to create the necessary user.")
        return False

if __name__ == "__main__":
    success = test_connection()
    if not success:
        sys.exit(1) 