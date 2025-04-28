"""
Script to download frog call audio files and store them locally.
This eliminates reliance on external URLs that may be unreliable.
"""

import os
import requests
import pandas as pd
import time
from populate_frog_calls import ADDITIONAL_FROG_CALLS
from database import get_db_connection
import urllib.parse

# Directory to store audio files
AUDIO_DIR = "static/audio"

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
        response = requests.get(url, timeout=10, stream=True)
        
        # Check if the download was successful
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Successfully downloaded to {output_path}")
            return output_path
        else:
            print(f"Failed to download {url}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def download_frog_calls():
    """Download all frog calls from the predefined list."""
    ensure_directories()
    
    total = len(ADDITIONAL_FROG_CALLS)
    success_count = 0
    local_paths = {}
    
    print(f"Downloading {total} frog call audio files...")
    
    for i, call in enumerate(ADDITIONAL_FROG_CALLS):
        print(f"\nProcessing {i+1}/{total}: {call['species_name']}")
        
        # Create a filename from the species name and URL
        url = call['audio_url']
        url_filename = os.path.basename(urllib.parse.urlparse(url).path)
        extension = os.path.splitext(url_filename)[1]
        if not extension:
            extension = ".mp3"  # Default to mp3 if no extension in URL
            
        safe_name = call['species_name'].replace(' ', '_').lower()
        filename = f"{safe_name}_{i+1}{extension}"
        
        # Download the file
        local_path = download_audio_file(url, filename)
        
        if local_path:
            success_count += 1
            relative_path = os.path.join("static/audio", filename)
            local_paths[url] = relative_path
            
        # Pause briefly to avoid overwhelming servers
        time.sleep(0.5)
    
    print(f"\nDownloaded {success_count}/{total} audio files.")
    return local_paths

def update_database_paths(local_paths):
    """
    Update the database to use local paths instead of URLs.
    
    Args:
        local_paths (dict): Dictionary mapping original URLs to local paths
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_count = 0
        
        # For each URL that was downloaded successfully
        for url, local_path in local_paths.items():
            # Check if this URL exists in the database
            cursor.execute("SELECT call_id FROM frog_calls WHERE audio_url = ?", (url,))
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    call_id = row[0]
                    # Update the database with the local path
                    cursor.execute(
                        "UPDATE frog_calls SET audio_url = ?, local_file = 1 WHERE call_id = ?",
                        (local_path, call_id)
                    )
                    update_count += 1
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print(f"Updated {update_count} database records to use local paths.")
        return update_count
        
    except Exception as e:
        print(f"Error updating database: {e}")
        return 0

def add_local_file_column():
    """Add a local_file column to the frog_calls table if it doesn't exist."""
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
        
        if not column_exists:
            # Add the local_file column
            cursor.execute("""
            ALTER TABLE frog_calls 
            ADD local_file BIT NOT NULL DEFAULT 0
            """)
            conn.commit()
            print("Added local_file column to frog_calls table.")
        else:
            print("local_file column already exists in frog_calls table.")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding local_file column: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FROG CALL DOWNLOADER")
    print("=" * 50)
    
    # Add local_file column to database
    add_local_file_column()
    
    # Download audio files
    local_paths = download_frog_calls()
    
    # Update database with local paths
    if local_paths:
        update_database_paths(local_paths)
    
    print("\nDownload complete. You can now run the app with:")
    print("streamlit run app.py")
    print("=" * 50) 