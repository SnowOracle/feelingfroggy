"""
Script to populate the database with a larger collection of frog calls.
This extends our basic collection with calls from various sources.
"""

import pandas as pd
import requests
import pyodbc
import time
import json
import os
from database import get_db_connection, execute_query
from bs4 import BeautifulSoup

# List of reliable frog call sources
SOURCES = [
    {
        "name": "National Park Service",
        "base_url": "https://www.nps.gov/subjects/sound/frogs.htm",
        "type": "direct"
    },
    {
        "name": "FrogLife.org",
        "base_url": "https://www.froglife.org/info-advice/amphibians-and-reptiles/frogs/",
        "type": "organization"
    },
    {
        "name": "USGS Frog Call Lookup",
        "base_url": "https://www.pwrc.usgs.gov/Frogcall/index.cfm",
        "type": "database"
    },
    {
        "name": "California Herps",
        "base_url": "https://www.californiaherps.com/sounds.html",
        "type": "regional"
    },
    {
        "name": "AmphibiaWeb",
        "base_url": "https://amphibiaweb.org/sounds/index.html",
        "type": "scientific"
    },
    {
        "name": "Minnesota Frogs and Toads",
        "base_url": "https://mnherpsoc.org/mn-species/frogs-and-toads/",
        "type": "regional"
    },
]

# Manual collection of known frog calls with reliable URLs
ADDITIONAL_FROG_CALLS = [
    {
        "species_name": "American Bullfrog",
        "scientific_name": "Lithobates catesbeianus",
        "audio_url": "https://www.nps.gov/subjects/sound/upload/American-Bullfrog_NPS.mp3",
        "description": "Deep, resonant 'jug-o-rum' calls that carry far across water"
    },
    {
        "species_name": "Spring Peeper",
        "scientific_name": "Pseudacris crucifer",
        "audio_url": "https://www.nps.gov/subjects/sound/upload/Spring-Peeper_NPS.mp3",
        "description": "High-pitched 'peep' calls that signal the arrival of spring"
    },
    {
        "species_name": "Green Treefrog",
        "scientific_name": "Hyla cinerea",
        "audio_url": "https://www.nps.gov/subjects/sound/upload/Green-Treefrog_NPS.mp3",
        "description": "Repeated 'queenk-queenk' bell-like calls"
    },
    {
        "species_name": "Cope's Gray Treefrog",
        "scientific_name": "Hyla chrysoscelis",
        "audio_url": "https://www.nps.gov/subjects/sound/upload/Copes-Gray-Treefrog_NPS.mp3",
        "description": "Musical trill with metallic quality, faster than Gray Treefrog"
    },
    {
        "species_name": "Western Chorus Frog",
        "scientific_name": "Pseudacris triseriata",
        "audio_url": "https://www.nps.gov/subjects/sound/upload/Western-Chorus-Frog_NPS.mp3",
        "description": "Sound like running a finger along the teeth of a comb"
    },
    {
        "species_name": "Northern Leopard Frog",
        "scientific_name": "Lithobates pipiens",
        "audio_url": "https://www.nps.gov/subjects/sound/upload/Northern-Leopard-Frog_NPS.mp3",
        "description": "Low, guttural snore followed by several grunting pulses"
    },
    {
        "species_name": "Wood Frog",
        "scientific_name": "Lithobates sylvaticus",
        "audio_url": "https://www.nps.gov/subjects/sound/upload/Wood-Frog_NPS.mp3",
        "description": "Resembles quacking ducks, short and rapid"
    },
    {
        "species_name": "Pacific Treefrog",
        "scientific_name": "Pseudacris regilla",
        "audio_url": "https://www.californiaherps.com/sounds/pseudacrisregillamix3na.mp3",
        "description": "The classic 'ribbit' sound heard in many movies"
    },
    {
        "species_name": "Pickerel Frog",
        "scientific_name": "Lithobates palustris",
        "audio_url": "https://www.froglife.org/wp-content/uploads/2015/05/Pickerel-Frog.mp3",
        "description": "Low-pitched snore lasting 1-2 seconds"
    },
    {
        "species_name": "Common Frog",
        "scientific_name": "Rana temporaria",
        "audio_url": "https://www.froglife.org/wp-content/uploads/2015/05/Common-Frog.mp3",
        "description": "Series of low-pitched grunts and croaks"
    },
    {
        "species_name": "American Toad",
        "scientific_name": "Anaxyrus americanus",
        "audio_url": "https://www.froglife.org/wp-content/uploads/2015/05/American-Toad.mp3",
        "description": "Long, musical trills lasting 6-30 seconds"
    },
    {
        "species_name": "Great Plains Toad",
        "scientific_name": "Anaxyrus cognatus",
        "audio_url": "https://amphibiaweb.org/sounds/Anaxyrus_cognatus.mp3",
        "description": "Harsh, rattling trill like a jackhammer"
    },
    {
        "species_name": "Natterjack Toad",
        "scientific_name": "Epidalea calamita",
        "audio_url": "https://www.froglife.org/wp-content/uploads/2015/05/Natterjack-Toad.mp3",
        "description": "Loud, rasping calls that can be heard over a kilometer away"
    },
    {
        "species_name": "Fowler's Toad",
        "scientific_name": "Anaxyrus fowleri",
        "audio_url": "https://amphibiaweb.org/sounds/Anaxyrus_fowleri.mp3",
        "description": "Harsh, nasal 'waaaah' lasting 1-4 seconds"
    },
    {
        "species_name": "Barking Treefrog",
        "scientific_name": "Hyla gratiosa",
        "audio_url": "https://amphibiaweb.org/sounds/Hyla_gratiosa.mp3",
        "description": "Deep, dog-like barks or honks"
    }
]

def fetch_species_mapping():
    """
    Fetch all species from the CSV file and create a mapping from name to ID.
    """
    try:
        # Read from CSV instead of database
        csv_path = os.path.join("data", "frog_species.csv")
        
        if not os.path.exists(csv_path):
            print(f"Error: Species CSV file not found at {csv_path}")
            return {}, {}, pd.DataFrame()
            
        df = pd.read_csv(csv_path)
        
        # Add species_id if not present
        if 'species_id' not in df.columns:
            df['species_id'] = range(1, len(df) + 1)
        
        # Create mappings
        name_to_id = {}
        scientific_to_id = {}
        
        for _, row in df.iterrows():
            name_to_id[row['name'].lower()] = row['species_id']
            scientific_to_id[row['scientific_name'].lower()] = row['species_id']
        
        return name_to_id, scientific_to_id, df
        
    except Exception as e:
        print(f"Error fetching species mapping from CSV: {e}")
        return {}, {}, pd.DataFrame()

def match_species_id(species_name, scientific_name, name_map, scientific_map, species_df):
    """
    Try to match a species name or scientific name to an ID in our database.
    Uses fuzzy matching as fallback.
    """
    # Direct match by name
    if species_name.lower() in name_map:
        return name_map[species_name.lower()]
    
    # Direct match by scientific name
    if scientific_name and scientific_name.lower() in scientific_map:
        return scientific_map[scientific_name.lower()]
    
    # Try to match genus
    if scientific_name:
        genus = scientific_name.split(' ')[0].lower()
        for sci_name, species_id in scientific_map.items():
            if sci_name.lower().startswith(genus):
                return species_id
    
    # Fallback to naive partial matching
    for name, species_id in name_map.items():
        if species_name.lower() in name.lower() or name.lower() in species_name.lower():
            return species_id
    
    # If all else fails, use the most common ID (typically a treefrog)
    if len(species_df) > 0:
        if "Tree Frog" in species_df['name'].values:
            for _, row in species_df.iterrows():
                if "Tree Frog" in row['name']:
                    return row['species_id']
        
        # Just return the first ID as last resort
        return species_df.iloc[0]['species_id']
    
    # Absolute fallback
    return 1

def verify_audio_url(url):
    """
    Verify that an audio URL is accessible.
    """
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type or url.endswith(('.mp3', '.wav', '.ogg')):
                return True
        return False
    except Exception:
        return False

def populate_calls_from_list():
    """
    Populate frog calls from our predefined list.
    """
    print("Populating frog calls from predefined list...")
    
    # Get species mappings from CSV
    name_map, scientific_map, species_df = fetch_species_mapping()
    
    if len(name_map) == 0:
        print("Error: Could not fetch species data from CSV file.")
        return False
    
    # Count existing calls - this is just for reporting, we'll skip if there's an error
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM frog_calls")
        existing_count = cursor.fetchone()[0]
        
        # Get existing audio URLs to avoid duplicates
        cursor.execute("SELECT audio_url FROM frog_calls")
        existing_urls = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        print(f"Warning: Could not check existing calls: {e}")
        existing_count = 0
        existing_urls = []
    
    # Insert each call
    added_count = 0
    for call in ADDITIONAL_FROG_CALLS:
        if call['audio_url'] in existing_urls:
            print(f"Skipping duplicate URL: {call['audio_url']}")
            continue
            
        # Verify URL is valid
        if not verify_audio_url(call['audio_url']):
            print(f"Warning: Could not verify audio URL: {call['audio_url']}")
            # Continue anyway - URL might still work for streaming
        
        # Match to a species ID
        species_id = match_species_id(
            call['species_name'], 
            call['scientific_name'], 
            name_map, 
            scientific_map, 
            species_df
        )
        
        # Insert the call
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO frog_calls (
                species_id, audio_url, description, created_at
            ) VALUES (?, ?, ?, GETDATE())
            """
            
            cursor.execute(sql, (
                species_id,
                call['audio_url'],
                call['description']
            ))
            
            cursor.commit()
            conn.close()
            
            added_count += 1
            print(f"Added call for {call['species_name']}")
            
        except Exception as e:
            print(f"Error adding call for {call['species_name']}: {e}")
    
    print(f"Added {added_count} new frog calls. Database now has approximately {existing_count + added_count} calls.")
    return added_count > 0

def save_source_list():
    """
    Save the list of sources to a JSON file for reference.
    """
    with open("data/frog_call_sources.json", "w") as f:
        json.dump(SOURCES, f, indent=2)
    print("Saved source list to data/frog_call_sources.json")

if __name__ == "__main__":
    print("=" * 50)
    print("FROG CALLS POPULATION UTILITY")
    print("=" * 50)
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save source list
    save_source_list()
    
    # Populate calls
    populate_calls_from_list()
    
    print("\nPopulation complete. You can now run the app with:")
    print("streamlit run app.py")
    print("=" * 50) 