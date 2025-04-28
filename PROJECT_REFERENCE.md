# Feeling Froggy - Project Reference

## Project Overview
Feeling Froggy is an interactive web application built with Streamlit that provides information about frog species, enables users to identify frogs, explore frog calls, and learn about conservation efforts. The application connects to a database (FroggyDB) to store and retrieve data about frog species, sightings, calls, and conservation projects.

## Key Features
- Frog species information and identification
- Frog call audio playback and exploration
- Interactive frog call quiz
- Local audio file support and online fallback
- Database integration for persistent data storage

## Technical Stack
- **Frontend**: Streamlit
- **Database**: SQL Server (FroggyDB)
- **Data Processing**: Pandas, NumPy
- **Audio Processing**: pydub (for conversion)
- **Visualization**: Matplotlib, Plotly

## File Directory Structure

### Core Application Files
- **app.py** - Main Streamlit application entry point with UI/UX structure
- **frog_sounds.py** - Module for managing and playing frog call audio files
- **frog_identifier.py** - Frog identification functionality and image processing
- **database.py** - Database connection and query functionality

### Data Management
- **setup.py** - Database setup and initial configuration
- **data_migration.py** - Tools for migrating data between versions
- **populate_frog_calls.py** - Script to populate the database with frog call data
- **create_user.sql** - SQL script for database user creation

### Audio File Management
- **download_sample_calls.py** - Downloads frog call samples from reliable sources (Wikimedia Commons)
- **download_frog_calls.py** - Original script to download frog call audio files

### Testing and Utilities
- **test_connection.py** - Script to test database connection

### Configuration
- **requirements.txt** - Python dependencies for the project

## Database Schema
The application uses a database with the following main tables:
- `frog_species` - Information about frog species
- `frog_calls` - Audio files and descriptions of frog calls
- `frog_sightings` - User-reported frog sightings with location data
- `conservation_projects` - Conservation efforts for endangered frog species

## Key Components

### Frog Sound Player
The `FrogSoundPlayer` class in `frog_sounds.py` provides functionality to:
- Browse frog calls by species
- Search for specific calls
- Compare calls between different species
- Present an interactive quiz about frog sounds
- Handle both local audio files and remote URLs

### Database Connection
The `database.py` file manages:
- Database connection setup
- Query execution and data retrieval
- Error handling for database operations
- Support for local audio file paths

### Audio File Management
The audio management scripts:
- Download audio files from reliable sources
- Convert between audio formats when needed
- Store files locally in the static/audio directory
- Update database records with file information

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Download audio files: `python download_sample_calls.py`
3. Run the application: `streamlit run app.py`

## Future Development Ideas
- Mobile app version for field identification
- Integration with machine learning for automated call recognition
- Expanded quiz and educational content
- Community features for sharing frog sightings
- Integration with conservation organizations' APIs
- Visualization tools for frog population trends 