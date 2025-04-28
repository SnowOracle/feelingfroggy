"""
Script to download reliable frog call samples and save them locally.
This script uses direct audio URLs from reliable sources and converts to MP3 format.
"""

import os
import requests
import time
from database import get_db_connection

# Directory to store audio files
AUDIO_DIR = "static/audio"

# List of reliable frog call URLs
SAMPLE_CALLS = [
    {
        "name": "American Bullfrog",
        "scientific_name": "Lithobates catesbeianus",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Lithobates_catesbeianus.ogg",
        "filename": "american_bullfrog.mp3",
        "description": "Deep, resonant 'jug-o-rum' calls"
    },
    {
        "name": "Spring Peeper",
        "scientific_name": "Pseudacris crucifer",
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Pseudacris_crucifer_02.mp3",
        "filename": "spring_peeper.mp3",
        "description": "High-pitched 'peep' calls that signal the arrival of spring"
    },
    {
        "name": "Green Treefrog", 
        "scientific_name": "Hyla cinerea",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Hyla_cinerea.ogg",
        "filename": "green_treefrog.mp3",
        "description": "Repeated 'queenk-queenk' bell-like calls"
    },
    {
        "name": "American Toad",
        "scientific_name": "Anaxyrus americanus",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/61/Anaxyrus_americanus_-_American_Toad_-_Call.ogg",
        "filename": "american_toad.mp3",
        "description": "Long musical trill that can last up to 30 seconds"
    },
    {
        "name": "Gray Treefrog",
        "scientific_name": "Hyla versicolor",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Hyla_versicolor.ogg",
        "filename": "gray_treefrog.mp3",
        "description": "Melodic bird-like trill that lasts 1-3 seconds"
    }
]

def ensure_directories():
    """Ensure the necessary directories exist."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f"Created audio directory at: {AUDIO_DIR}")

def download_audio_file(url, filename):
    """
    Download an audio file from a URL and save it locally.
    
    Args:
        url (str): The URL of the audio file
        filename (str): The name to save the file as
        
    Returns:
        str: The path to the saved file, or None if download failed
    """
    output_path = os.path.join(AUDIO_DIR, filename)
    
    # Skip if file already exists
    if os.path.exists(output_path):
        print(f"File already exists: {output_path}")
        return output_path
    
    try:
        # Download the file
        print(f"Downloading {url} to {output_path}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        
        # Check if the download was successful
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            
            # Convert OGG to MP3 if needed
            if url.endswith('.ogg') and output_path.endswith('.mp3'):
                try:
                    # Try to convert using pydub if available
                    from pydub import AudioSegment
                    temp_ogg = output_path.replace('.mp3', '.ogg')
                    os.rename(output_path, temp_ogg)
                    
                    sound = AudioSegment.from_ogg(temp_ogg)
                    sound.export(output_path, format="mp3")
                    
                    # Remove the temporary file
                    os.remove(temp_ogg)
                    print(f"Converted OGG to MP3: {output_path}")
                except ImportError:
                    print("Could not convert OGG to MP3 - pydub not installed.")
                    print("Install with: pip install pydub ffmpeg-python")
                    # Keep the file as is, Streamlit may still play it
            
            print(f"Successfully downloaded to {output_path}")
            return output_path
        else:
            print(f"Failed to download {url}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def add_sample_call(name, scientific_name, local_path, description):
    """
    Add a sample frog call to the database.
    
    Args:
        name (str): The name of the frog species
        scientific_name (str): The scientific name of the frog species
        local_path (str): The local path to the audio file
        description (str): A description of the call
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First find the species_id
        query = "SELECT species_id FROM frog_species WHERE name = ? OR scientific_name = ?"
        cursor.execute(query, (name, scientific_name))
        row = cursor.fetchone()
        
        if row:
            species_id = row[0]
            
            # Check if this call already exists
            check_query = "SELECT COUNT(*) FROM frog_calls WHERE audio_url = ?"
            cursor.execute(check_query, (local_path,))
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                # Check if the local_file column exists
                cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'frog_calls' AND COLUMN_NAME = 'local_file'
                """)
                
                local_file_exists = cursor.fetchone()[0] > 0
                
                # Insert the call
                if local_file_exists:
                    insert_query = """
                    INSERT INTO frog_calls (species_id, audio_url, description, local_file, created_at)
                    VALUES (?, ?, ?, 1, GETDATE())
                    """
                else:
                    insert_query = """
                    INSERT INTO frog_calls (species_id, audio_url, description, created_at)
                    VALUES (?, ?, ?, GETDATE())
                    """
                
                cursor.execute(insert_query, (species_id, local_path, description))
                cursor.commit()
                print(f"Added call for {name} to database")
                conn.close()
                return True
            else:
                print(f"Call for {name} already exists in database")
                conn.close()
                return False
        else:
            print(f"Species {name} not found in database")
            conn.close()
            return False
            
    except Exception as e:
        print(f"Error adding call to database: {e}")
        return False

def process_sample_calls():
    """Process and download the sample calls."""
    ensure_directories()
    
    print(f"Downloading {len(SAMPLE_CALLS)} sample frog calls...")
    successful_downloads = 0
    successful_additions = 0
    
    for call in SAMPLE_CALLS:
        # Download the file
        local_path = download_audio_file(call["url"], call["filename"])
        
        if local_path:
            successful_downloads += 1
            
            # Add to database
            db_path = os.path.join("static/audio", call["filename"])
            if add_sample_call(call["name"], call["scientific_name"], db_path, call["description"]):
                successful_additions += 1
                
        # Pause briefly
        time.sleep(0.5)
    
    print(f"\nDownloaded {successful_downloads}/{len(SAMPLE_CALLS)} frog calls.")
    print(f"Added {successful_additions}/{len(SAMPLE_CALLS)} calls to database.")
    
    return successful_downloads, successful_additions

if __name__ == "__main__":
    print("=" * 50)
    print("SAMPLE FROG CALLS DOWNLOADER")
    print("=" * 50)
    
    print("Note: For full functionality, you may need to install:")
    print("pip install pydub ffmpeg-python")
    print("=" * 50)
    
    downloads, additions = process_sample_calls()
    
    if downloads > 0:
        print("\nDownload complete. You can now run the app with:")
        print("streamlit run app.py")
    else:
        print("\nFailed to download any sample calls.")
        print("Please check the URLs and your internet connection.")
    
    print("=" * 50) 