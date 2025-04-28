import pandas as pd
import pyodbc
import os
import datetime
from database import get_db_connection
from test_connection import test_connection

def migrate_frog_species_from_csv():
    """
    Migrate frog species data from CSV to the database.
    """
    # First, test the connection
    if not test_connection():
        print("Database connection test failed. Cannot migrate data.")
        return False
        
    try:
        # Read the CSV file
        csv_path = "data/frog_species.csv"
        df = pd.read_csv(csv_path)

        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if there's already data in the table
        cursor.execute("SELECT COUNT(*) FROM frog_species")
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"The frog_species table already contains {count} records. Skipping migration.")
            conn.close()
            return False

        # Insert each row from the CSV into the database
        for _, row in df.iterrows():
            # Add vocalization descriptions based on species
            vocalization_desc = None
            vocalization_url = None

            if "Tree Frog" in row["name"]:
                vocalization_desc = "Melodic calls, often heard after rain"
            elif "Bullfrog" in row["name"]:
                vocalization_desc = "Deep, resonant 'jug-o-rum' calls"
            elif "Poison" in row["name"]:
                vocalization_desc = "Soft, buzzing calls"
            else:
                vocalization_desc = "Typical croaking sounds"

            # Create a description from available data
            description = f"{row['name']} ({row['scientific_name']}) is a {row['color']} frog found in {row['habitat']} habitats of {row['region']}. "
            description += f"It grows to approximately {row['size_cm']} cm and can live up to {row['lifespan_years']} years. "
            description += f"Its diet consists primarily of {row['diet']}. "
            description += f"The conservation status is currently listed as {row['conservation_status']}."

            # SQL Server uses ? as parameter placeholders
            sql = """
            INSERT INTO frog_species (
                name, scientific_name, habitat, region, conservation_status, 
                size_cm, lifespan_years, diet, color, image_url,
                description, vocalization_description, vocalization_url, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Current timestamp for created_at and updated_at
            now = datetime.datetime.now()

            # Execute the insert
            cursor.execute(sql, (
                row["name"], 
                row["scientific_name"], 
                row["habitat"], 
                row["region"], 
                row["conservation_status"],
                row["size_cm"], 
                row["lifespan_years"], 
                row["diet"], 
                row["color"], 
                row["image_url"],
                description,
                vocalization_desc,
                vocalization_url,
                now,
                now
            ))
            cursor.commit()  # Commit after each insert to avoid large transactions

        print(f"Successfully migrated {len(df)} frog species from CSV to database")

        # Close the connection
        conn.close()
        return True

    except Exception as e:
        print(f"Error migrating data: {e}")
        return False

def populate_initial_frog_calls_data():
    """
    Populate initial frog calls data if the table is empty.
    This function adds sample frog call data to the database.
    """
    # First, test the connection
    if not test_connection():
        print("Database connection test failed. Cannot populate frog calls.")
        return False
        
    try:
        # Get a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we already have frog calls
        cursor.execute("SELECT COUNT(*) FROM frog_calls")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"The frog_calls table already contains {count} records. Skipping population.")
            conn.close()
            return False
        
        # Sample frog call data
        frog_calls = [
            # The species_id should match the IDs in your frog_species table
            (1, "https://www.nps.gov/subjects/sound/upload/Spring-Peeper_NPS.mp3", "High-pitched peeping sounds, usually heard in early spring", None, None),  # Red-Eyed Tree Frog
            (3, "https://www.nps.gov/subjects/sound/upload/American-Bullfrog_NPS.mp3", "Deep resonant calls that sound like 'jug-o-rum'", None, None),  # American Bullfrog
            (5, "https://www.nps.gov/subjects/sound/upload/Green-Treefrog_NPS.mp3", "Bell-like calls, sounds like 'queenk-queenk'", None, None),  # Australian Green Tree Frog
            (12, "https://www.froglife.org/wp-content/uploads/2015/05/Gray-Tree-Frog.mp3", "Melodic bird-like trill that lasts 1-3 seconds", None, None),  # Gray Tree Frog
            (15, "https://www.froglife.org/wp-content/uploads/2015/05/Common-Frog.mp3", "Low-pitched grunting or croaking sounds", None, None),  # European Common Frog
            (10, "https://www.froglife.org/wp-content/uploads/2015/05/Whites-Tree-Frog.mp3", "Soft, low-pitched calls that sound like a duck quacking", None, None),  # White's Tree Frog
            (6, "https://www.froglife.org/wp-content/uploads/2015/05/Golden-Poison-Frog.mp3", "Soft, buzzing calls that sound like insects", None, None),  # Golden Poison Frog
        ]
        
        # Insert each frog call
        for call_data in frog_calls:
            species_id, audio_url, description, recorded_by, recording_date = call_data
            
            # SQL for insert
            sql = """
            INSERT INTO frog_calls (
                species_id, audio_url, description, recorded_by, recording_date, created_at
            ) VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            
            # Execute the insert
            cursor.execute(sql, (species_id, audio_url, description, recorded_by, recording_date))
            cursor.commit()  # Commit after each insert
        
        print(f"Successfully added {len(frog_calls)} frog calls to database")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error populating frog calls: {e}")
        return False

def execute_migration():
    """Execute the full migration process"""
    print("\n" + "=" * 50)
    print("FROG DATA MIGRATION")
    print("=" * 50)
    
    # First verify connection
    print("\nVerifying database connection...")
    if not test_connection():
        print("Database connection failed. Cannot proceed with migration.")
        return False
    
    # Migrate frog species data
    print("\nMigrating frog species data...")
    species_migrated = migrate_frog_species_from_csv()
    
    if species_migrated:
        print("Species data migration completed successfully.")
    else:
        print("Species data migration skipped or failed.")
    
    # Populate frog calls data
    print("\nPopulating frog call data...")
    calls_populated = populate_initial_frog_calls_data()
    
    if calls_populated:
        print("Frog call data population completed successfully.")
    else:
        print("Frog call data already exists or population failed.")
    
    print("\nData migration process complete.")
    return species_migrated or calls_populated

if __name__ == "__main__":
    execute_migration() 