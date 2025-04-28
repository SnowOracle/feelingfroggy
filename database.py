import pyodbc
import pandas as pd
import os
import json
import warnings

# Flag to control whether to use real database or fallback
USE_FALLBACK = False

def get_db_connection():
    """
    Returns a live connection to your SQL Server using pyodbc 
    with your provided driver path and credentials.
    """
    conn = pyodbc.connect(
        "DRIVER=/opt/homebrew/lib/libtdsodbc.so;"
        "SERVER=127.0.0.1;"
        "PORT=1433;"
        "DATABASE=FroggyDB;"
        "UID=climbing_user;"
        "PWD=hoosierheights;"
        "TDS_Version=7.4;"
    )
    return conn

def execute_query(query, params=None):
    """
    Execute a SQL query and return results if applicable.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # Check if the query is a SELECT statement
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            conn.close()
            return results
        else:
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        conn.close()
        raise e

def query_to_dataframe(query, params=None):
    """
    Execute a SQL query and return results as a pandas DataFrame.
    """
    conn = get_db_connection()
    
    try:
        # Execute query directly with cursor to avoid pandas warning
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names from cursor description
        columns = [column[0] for column in cursor.description]
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Create DataFrame from rows
        df = pd.DataFrame.from_records(rows, columns=columns)
        
        return df
    except Exception as e:
        raise e
    finally:
        conn.close()

# Functions for frog species data
def get_all_frog_species():
    """Get all frog species from the database"""
    query = """
    SELECT species_id, name, scientific_name, habitat, region, 
           conservation_status, size_cm, lifespan_years, diet, 
           color, image_url, description, vocalization_description, vocalization_url
    FROM frog_species
    """
    return query_to_dataframe(query)

def get_frog_by_id(species_id):
    """Get a specific frog species by ID"""
    query = """
    SELECT species_id, name, scientific_name, habitat, region, 
           conservation_status, size_cm, lifespan_years, diet, 
           color, image_url, description, vocalization_description, vocalization_url
    FROM frog_species
    WHERE species_id = ?
    """
    return query_to_dataframe(query, params=[species_id])

# Functions for frog calls
def get_all_frog_calls():
    """Get all frog calls from the database"""
    try:
        query = """
        SELECT fc.call_id, fc.species_id, fc.audio_url, fc.description, fc.recording_date,
               ISNULL(fc.local_file, 0) as local_file,
               fs.name as species_name, fs.scientific_name
        FROM frog_calls fc
        JOIN frog_species fs ON fc.species_id = fs.species_id
        """
        return query_to_dataframe(query)
    except Exception as e:
        # This might happen if the local_file column doesn't exist yet
        if "local_file" in str(e).lower():
            # Retry with a query that doesn't include local_file
            query = """
            SELECT fc.call_id, fc.species_id, fc.audio_url, fc.description, fc.recording_date,
                   0 as local_file, -- Default to 0 (false) for local_file
                   fs.name as species_name, fs.scientific_name
            FROM frog_calls fc
            JOIN frog_species fs ON fc.species_id = fs.species_id
            """
            return query_to_dataframe(query)
        else:
            raise e

def get_frog_calls_by_species(species_id):
    """Get all calls for a specific frog species"""
    try:
        query = """
        SELECT fc.call_id, fc.audio_url, fc.description, fc.recording_date,
               ISNULL(fc.local_file, 0) as local_file
        FROM frog_calls fc
        WHERE fc.species_id = ?
        """
        return query_to_dataframe(query, params=[species_id])
    except Exception as e:
        # This might happen if the local_file column doesn't exist yet
        if "local_file" in str(e).lower():
            # Retry with a query that doesn't include local_file
            query = """
            SELECT fc.call_id, fc.audio_url, fc.description, fc.recording_date,
                   0 as local_file -- Default to 0 (false) for local_file
            FROM frog_calls fc
            WHERE fc.species_id = ?
            """
            return query_to_dataframe(query, params=[species_id])
        else:
            raise e

# Insert frog call data
def insert_frog_call(species_id, audio_url, description, recorded_by=None, recording_date=None):
    """Insert a new frog call into the database"""
    # Check if the local_file column exists
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the column exists
        cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'frog_calls' AND COLUMN_NAME = 'local_file'
        """)
        
        column_exists = cursor.fetchone()[0] > 0
        conn.close()
        
        # If column exists, include it in the insert
        if column_exists:
            is_local = 1 if audio_url.startswith('static/audio/') else 0
            query = """
            INSERT INTO frog_calls (species_id, audio_url, description, recorded_by, recording_date, local_file, created_at)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """
            return execute_query(query, params=[species_id, audio_url, description, recorded_by, recording_date, is_local])
        else:
            # Original query without local_file
            query = """
            INSERT INTO frog_calls (species_id, audio_url, description, recorded_by, recording_date, created_at)
            VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            return execute_query(query, params=[species_id, audio_url, description, recorded_by, recording_date])
            
    except Exception as e:
        print(f"Error in insert_frog_call: {e}")
        # Fallback to original query
        query = """
        INSERT INTO frog_calls (species_id, audio_url, description, recorded_by, recording_date, created_at)
        VALUES (?, ?, ?, ?, ?, GETDATE())
        """
        return execute_query(query, params=[species_id, audio_url, description, recorded_by, recording_date])

# Initial data population function - to move data from CSV to database
def populate_initial_frog_calls_data():
    """
    Populate initial frog calls data if the table is empty.
    This function adds sample frog call data to the database.
    """
    # Check if we already have frog calls
    count_query = "SELECT COUNT(*) FROM frog_calls"
    count = execute_query(count_query)[0][0]
    
    if count == 0:
        # Sample frog call data
        frog_calls = [
            # The species_id should match the IDs in your frog_species table
            (1, "https://www.nps.gov/subjects/sound/upload/American-Bullfrog_NPS.mp3", "Deep resonant calls that sound like 'jug-o-rum'", None, None),  # Red-Eyed Tree Frog
            (3, "https://www.nps.gov/subjects/sound/upload/Spring-Peeper_NPS.mp3", "High-pitched peeping sounds, usually heard in early spring", None, None),  # American Bullfrog
            (5, "https://www.nps.gov/subjects/sound/upload/Green-Treefrog_NPS.mp3", "Bell-like calls, sounds like 'queenk-queenk'", None, None),  # Australian Green Tree Frog
            (12, "https://www.froglife.org/wp-content/uploads/2015/05/Gray-Tree-Frog.mp3", "Melodic bird-like trill that lasts 1-3 seconds", None, None),  # Gray Tree Frog
            (15, "https://www.froglife.org/wp-content/uploads/2015/05/Common-Frog.mp3", "Low-pitched grunting or croaking sounds", None, None),  # European Common Frog
            (10, "https://www.froglife.org/wp-content/uploads/2015/05/Whites-Tree-Frog.mp3", "Soft, low-pitched calls that sound like a duck quacking", None, None),  # White's Tree Frog
            (6, "https://www.froglife.org/wp-content/uploads/2015/05/Golden-Poison-Frog.mp3", "Soft, buzzing calls that sound like insects", None, None),  # Golden Poison Frog
        ]
        
        # Insert each frog call
        for call in frog_calls:
            insert_frog_call(*call)
        
        return True
    return False

# When this module is run directly, it should initialize the fallback data
if __name__ == "__main__":
    print("Initializing fallback data...")
    frog_species = get_all_frog_species()
    frog_calls = get_all_frog_calls()
    print(f"Loaded {len(frog_species)} frog species and {len(frog_calls)} frog calls.")
    print("Done.") 