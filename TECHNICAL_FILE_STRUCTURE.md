# Feeling Froggy - Technical File Structure

This document provides a detailed breakdown of each file in the Feeling Froggy application, including their purpose, key functions, and relationships to other files.

## Application Files

### app.py
**Purpose**: Main Streamlit application entry point and interface
- Initializes the Streamlit application
- Defines page layout and navigation
- Integrates all components (identification, sounds, conservation)
- Manages user interactions and session state

### frog_sounds.py
**Purpose**: Manages frog call audio playback and exploration
- `FrogSoundPlayer` class: Core functionality for audio management
- `render_call_player()`: Shows UI for browsing and playing frog calls
- `_render_audio_player()`: Handles both local and remote audio sources
- `render_interactive_quiz()`: Interactive quiz about frog calls
- `render_fun_facts()`: Displays educational content

### frog_identifier.py
**Purpose**: Frog species identification functionality
- Image processing and analysis for frog identification
- Species matching algorithms
- Display of identification results
- Educational content about frog identification features

### database.py
**Purpose**: Database connection and query management
- `get_db_connection()`: Establishes connection to FroggyDB
- `query_to_dataframe()`: Executes queries and returns pandas DataFrames
- `get_all_frog_species()`, `get_frog_species_by_id()`: Species data retrieval
- `get_all_frog_calls()`, `get_frog_calls_by_species()`: Audio data retrieval
- `insert_frog_call()`: Adds new call data to the database
- Error handling for database operations

## Data Management Files

### setup.py
**Purpose**: Sets up the application database and initial data
- Creates database tables if they don't exist
- Populates initial frog species data
- Configures database settings
- Validates database structure

### data_migration.py
**Purpose**: Tools for migrating data between versions
- Updates database schema when needed
- Transfers data between tables
- Handles version-specific data transformations
- Performs data integrity checks

### populate_frog_calls.py
**Purpose**: Populates the database with frog call data
- Inserts sample frog call records
- Links calls to species
- Validates data consistency
- Sets up initial call descriptions and URLs

### create_user.sql
**Purpose**: SQL script for database user creation
- SQL commands to create database users
- Assign permissions and roles
- Set up security context

## Audio Management Files

### download_sample_calls.py
**Purpose**: Downloads frog call samples from reliable sources
- Retrieves audio files from Wikimedia Commons
- Processes and stores files locally in static/audio/
- Updates database with file paths
- Handles format conversion (OGG to MP3)
- Functions:
  - `ensure_directories()`: Creates needed directories
  - `download_audio_file()`: Downloads files from URLs
  - `add_sample_call()`: Adds call data to database
  - `process_sample_calls()`: Orchestrates the download process

### download_frog_calls.py
**Purpose**: Original script to download frog call audio files
- Similar functionality to download_sample_calls.py but uses different sources
- May be used as a fallback or alternative download source

## Testing and Utility Files

### test_connection.py
**Purpose**: Tests database connectivity
- Validates database connection parameters
- Checks if tables exist and are accessible
- Reports connection status and issues
- Helps with troubleshooting database problems

## Directory Structure

```
feeling_froggy/
├── app.py                    # Main application entry point
├── database.py               # Database connection and queries
├── frog_sounds.py            # Frog call audio functionality
├── frog_identifier.py        # Frog identification functionality
├── setup.py                  # Database initialization
├── data_migration.py         # Data migration tools
├── download_sample_calls.py  # Audio file downloader (current)
├── download_frog_calls.py    # Audio file downloader (original)
├── populate_frog_calls.py    # Database population script
├── test_connection.py        # Database connection testing
├── create_user.sql           # SQL user creation script
├── requirements.txt          # Project dependencies
├── README.md                 # Project readme
└── static/                   # Static files directory
    └── audio/                # Local audio files
```

## Database Schema Details

### frog_species
- species_id (PK)
- name
- scientific_name
- description
- habitat
- region
- conservation_status
- image_url

### frog_calls
- call_id (PK)
- species_id (FK)
- audio_url
- description
- local_file (boolean flag)
- created_at

### frog_sightings
- sighting_id (PK)
- species_id (FK)
- location
- date_time
- observer_name
- notes
- image_url

### conservation_projects
- project_id (PK)
- species_id (FK)
- name
- description
- organization
- start_date
- end_date
- status

## Code Dependencies

```
Primary Dependencies:
- streamlit >= 1.24.0   # Web interface
- pandas >= 2.0.0       # Data processing
- matplotlib >= 3.7.0   # Visualization
- plotly >= 5.15.0      # Interactive visualization
- requests >= 2.30.0    # HTTP requests
- pillow >= 10.0.0      # Image processing
- pyodbc >= 4.0.39      # Database connectivity
- beautifulsoup4 >= 4.9.0 # Web scraping

Optional Dependencies:
- pydub                 # Audio conversion
- ffmpeg-python         # Audio processing
```

## Extension Points

Areas where the application could be extended:

1. **frog_sounds.py**: 
   - Add real-time audio analysis
   - Implement machine learning for call identification

2. **database.py**:
   - Add support for additional database backends
   - Implement caching for improved performance

3. **app.py**:
   - Add user authentication
   - Implement social features
   - Create a mobile-friendly interface

4. **frog_identifier.py**:
   - Integrate with computer vision APIs
   - Add advanced image analysis capabilities 