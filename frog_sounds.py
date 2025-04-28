"""
Frog sounds module for the Feeling Froggy app.
This module manages frog call data and provides functionality for playing and exploring frog sounds.
"""

import streamlit as st
import pandas as pd
import requests
import re
import os
from io import BytesIO
from database import get_all_frog_calls, get_frog_calls_by_species, get_all_frog_species

class FrogSoundPlayer:
    """
    A class to manage and play frog sounds in the Streamlit app.
    """
    
    def __init__(self):
        """Initialize the frog sound player."""
        self.frog_calls = None
        self.species_data = None
        self.load_data()
    
    def load_data(self):
        """Load frog call data from the database."""
        try:
            # Load from database
            self.frog_calls = get_all_frog_calls()
            self.species_data = get_all_frog_species()
        except Exception as e:
            st.error(f"Error loading frog call data: {e}")
    
    def render_call_player(self):
        """Render the frog call player in the Streamlit app."""
        st.markdown("### 🔊 Frog Calls Explorer")
        st.write("""
        Different frog species have distinct calls that serve various purposes 
        including attracting mates, defining territory, and alerting others to danger.
        Listen to some examples below and learn about each species' unique vocalization.
        """)
        
        # Create tabs for different ways to explore frog calls
        tab1, tab2, tab3 = st.tabs(["Browse by Species", "Search Calls", "Compare Calls"])
        
        with tab1:
            self._render_browse_by_species()
        
        with tab2:
            self._render_search_calls()
            
        with tab3:
            self._render_compare_calls()
    
    def _render_browse_by_species(self):
        """Render the browse by species tab."""
        if self.frog_calls is not None and not self.frog_calls.empty:
            # Create a selectbox for species
            species_options = self.frog_calls['species_name'].unique()
            selected_species = st.selectbox(
                "Select a frog species to hear its call:",
                options=species_options
            )
            
            # Filter calls for the selected species
            species_calls = self.frog_calls[self.frog_calls['species_name'] == selected_species]
            
            if len(species_calls) > 1:
                # If multiple calls exist for the species, let the user choose
                call_options = [f"Call {i+1}: {call['description'][:30]}..." 
                               for i, (_, call) in enumerate(species_calls.iterrows())]
                selected_call_idx = st.radio(
                    "Multiple calls available for this species:",
                    options=range(len(call_options)),
                    format_func=lambda i: call_options[i]
                )
                selected_call = species_calls.iloc[selected_call_idx]
            else:
                selected_call = species_calls.iloc[0]
            
            # Create columns for info and audio
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown(f"#### {selected_call['species_name']}")
                st.markdown(f"*{selected_call['scientific_name']}*")
                st.markdown(f"**Call description:** {selected_call['description']}")
                
                # Add an info box about when and why frogs make this call
                with st.expander("Learn more about this call"):
                    st.write("""
                    Frog calls are primarily used for:
                    - **Mating**: Males call to attract females
                    - **Territory**: To establish and defend territory
                    - **Warning**: To alert others to danger
                    - **Weather**: Some frogs call more before or after rain
                    """)
            
            with col2:
                # Display audio player
                self._render_audio_player(selected_call)
            
            # Show a visualization of the call patterns
            self._render_call_visualization(selected_call)
            
        else:
            st.error("No frog call data available. Please check the database connection.")
    
    def _render_search_calls(self):
        """Render the search calls tab."""
        if self.frog_calls is not None and not self.frog_calls.empty:
            st.markdown("#### Search for Frog Calls")
            
            # Search options
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("Search by species name or call description:", "")
            with col2:
                search_filters = st.multiselect(
                    "Filter by region:",
                    options=self.species_data['region'].unique() if 'region' in self.species_data.columns else []
                )
            
            # Execute search
            if search_term or search_filters:
                # Filter by search term if provided
                filtered_calls = self.frog_calls
                
                if search_term:
                    # Case-insensitive search in species name, scientific name, and description
                    pattern = re.compile(search_term, re.IGNORECASE)
                    filtered_calls = filtered_calls[
                        filtered_calls['species_name'].str.contains(pattern, regex=True) |
                        filtered_calls['scientific_name'].str.contains(pattern, regex=True) |
                        filtered_calls['description'].str.contains(pattern, regex=True)
                    ]
                
                # Filter by region if selected
                if search_filters and 'region' in self.species_data.columns:
                    species_in_regions = self.species_data[
                        self.species_data['region'].isin(search_filters)
                    ]['species_id'].unique()
                    
                    filtered_calls = filtered_calls[
                        filtered_calls['species_id'].isin(species_in_regions)
                    ]
                
                # Display results
                if not filtered_calls.empty:
                    st.success(f"Found {len(filtered_calls)} matching frog calls.")
                    
                    # Create a table of results
                    st.dataframe(
                        filtered_calls[['species_name', 'scientific_name', 'description']],
                        use_container_width=True
                    )
                    
                    # Let user select a call to play
                    call_options = [f"{call['species_name']} - {call['description'][:30]}..." 
                                   for _, call in filtered_calls.iterrows()]
                    
                    selected_idx = st.selectbox(
                        "Select a call to play:",
                        options=range(len(call_options)),
                        format_func=lambda i: call_options[i]
                    )
                    
                    selected_call = filtered_calls.iloc[selected_idx]
                    
                    # Display audio player for selected call
                    st.markdown(f"#### {selected_call['species_name']}")
                    st.markdown(f"*{selected_call['scientific_name']}*")
                    st.markdown(f"**Description:** {selected_call['description']}")
                    
                    self._render_audio_player(selected_call)
                    
                    # Show visualization
                    self._render_call_visualization(selected_call)
                else:
                    st.warning("No frog calls found matching your search criteria.")
            else:
                st.info("Enter a search term or select filters to find frog calls.")
                
                # Show all available calls
                st.markdown("#### All Available Calls")
                st.dataframe(
                    self.frog_calls[['species_name', 'scientific_name', 'description']],
                    use_container_width=True
                )
        else:
            st.error("No frog call data available. Please check the database connection.")
    
    def _render_compare_calls(self):
        """Render the compare calls tab."""
        st.markdown("#### Compare Different Frog Calls")
        
        if self.frog_calls is not None and not self.frog_calls.empty:
            # Let users select multiple species to compare
            selected_species = st.multiselect(
                "Select 2-4 frog species to compare their calls:",
                options=self.frog_calls['species_name'].unique(),
                default=self.frog_calls['species_name'].unique()[:2] if len(self.frog_calls['species_name'].unique()) >= 2 else []
            )
            
            if len(selected_species) > 0:
                # Filter calls for selected species
                filtered_calls = self.frog_calls[self.frog_calls['species_name'].isin(selected_species)]
                
                # Create a column for each selected species
                cols = st.columns(len(selected_species))
                
                for i, (_, call) in enumerate(filtered_calls.iterrows()):
                    with cols[i % len(cols)]:
                        st.markdown(f"**{call['species_name']}**")
                        st.markdown(f"*{call['scientific_name']}*")
                        
                        # Display audio player
                        self._render_audio_player(call)
                        
                        st.markdown(f"*{call['description']}*")
            else:
                st.info("Please select at least one species to compare.")
        else:
            st.error("No frog call data available. Please check the database connection.")
    
    def _render_call_visualization(self, call_data):
        """Render a visualization for the selected call."""
        st.markdown("#### Call Pattern Visualization")
        
        # For now, we just show a generic spectrogram image
        # In a full implementation, you could generate actual spectrograms from the audio files
        st.image(
            "https://www.froglife.org/wp-content/uploads/2015/09/spectrogram-example.jpg",
            caption=f"Example spectrogram showing {call_data['species_name']} call pattern (representative image)",
            width=600
        )
        
        # Add some educational content about call patterns
        with st.expander("Understanding Call Patterns"):
            st.write("""
            **Frog call spectrograms** show the frequency (pitch) and amplitude (volume) of calls over time:
            
            - **Vertical axis**: Frequency (higher = higher pitch)
            - **Horizontal axis**: Time
            - **Brightness**: Amplitude (brighter = louder)
            
            Different frog species have characteristic patterns that help scientists identify them.
            """)
    
    def _render_audio_player(self, call_data):
        """Render an audio player for a frog call, handling both local files and remote URLs."""
        audio_path = call_data['audio_url']
        
        # Check if this is a local file (starts with 'static/audio/')
        is_local_file = audio_path.startswith('static/audio/')
        
        try:
            if is_local_file:
                # If it's a local file, check if it exists
                if os.path.exists(audio_path):
                    # Open and read the file
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format='audio/mp3')
                else:
                    st.error(f"Local audio file not found: {audio_path}")
                    st.info("Try running the download_frog_calls.py script to download audio files.")
            else:
                # It's a remote URL, try to play it directly
                st.audio(audio_path)
        except Exception as e:
            st.error(f"Could not play audio: {e}")
            st.info(f"Audio source: {audio_path}")
            
            # Provide a fallback message
            if is_local_file:
                st.info("Try running the download_frog_calls.py script to download audio files.")
            else:
                st.info("Try clicking the link directly or updating to local files: " + audio_path)
    
    def render_fun_facts(self):
        """Render fun facts about frog sounds."""
        st.markdown("### 🎵 Fun Facts About Frog Sounds")
        
        facts = [
            "Some frogs can make calls underwater by pushing air back and forth between their lungs and mouth.",
            "The Coqui frog from Puerto Rico has a call so loud (90-100 decibels) it can be heard from far away.",
            "Each frog species has a unique call, which helps females identify males of their own species.",
            "Some female frogs also make sounds, although usually quieter than males.",
            "Frogs don't use vocal cords to make sounds - they use vocal sacs which amplify sounds like a balloon.",
            "The Pacific Tree Frog's 'ribbit' sound is what you typically hear in movies, even for scenes set where this frog doesn't live!",
            "The largest frog, the Goliath Frog, ironically makes very little sound compared to smaller species.",
            "Scientists can use frog call recordings to monitor population health and biodiversity in an area.",
            "Some frogs change their calling patterns based on their environment - they may call differently in urban areas versus natural habitats.",
            "Frog choruses often follow patterns where individuals take turns or synchronize their calls."
        ]
        
        # Display 3 random facts
        import random
        selected_facts = random.sample(facts, 3)
        
        for i, fact in enumerate(selected_facts):
            st.info(fact)
    
    def render_interactive_quiz(self):
        """Render an interactive quiz about frog sounds."""
        st.markdown("### 🎮 Frog Call Quiz")
        st.write("Test your knowledge of frog calls with this quick quiz!")
        
        if 'quiz_score' not in st.session_state:
            st.session_state.quiz_score = 0
            st.session_state.quiz_started = False
            st.session_state.current_question = 0
            st.session_state.questions_asked = []
        
        # Quiz questions - modified to use local paths if audio files have been downloaded
        questions = [
            {
                "audio_url": "static/audio/american_bullfrog_1.mp3",  # Local path
                "remote_url": "https://www.nps.gov/subjects/sound/upload/American-Bullfrog_NPS.mp3",  # Fallback URL
                "question": "Which frog makes this sound?",
                "options": ["Spring Peeper", "American Bullfrog", "Green Treefrog", "Gray Tree Frog"],
                "correct": "American Bullfrog",
                "explanation": "The American Bullfrog makes a deep 'jug-o-rum' sound."
            },
            {
                "audio_url": "static/audio/spring_peeper_1.mp3",  # Local path
                "remote_url": "https://www.nps.gov/subjects/sound/upload/Spring-Peeper_NPS.mp3",  # Fallback URL
                "question": "This sound is typically heard during which season?",
                "options": ["Summer", "Fall", "Winter", "Spring"],
                "correct": "Spring",
                "explanation": "Spring Peepers are aptly named because their calls announce the arrival of spring."
            },
            {
                "audio_url": "static/audio/green_treefrog_2.mp3",  # Local path
                "remote_url": "https://www.nps.gov/subjects/sound/upload/Green-Treefrog_NPS.mp3",  # Fallback URL
                "question": "What is the primary purpose of this frog's call?",
                "options": ["Warning predators", "Attracting mates", "Defining territory", "Calling for rain"],
                "correct": "Attracting mates",
                "explanation": "Most frog calls are primarily used by males to attract females for breeding."
            },
            {
                "question": "Which body part do frogs use to amplify their calls?",
                "options": ["Throat", "Vocal sac", "Lungs", "Tongue"],
                "correct": "Vocal sac",
                "explanation": "Frogs use vocal sacs (balloon-like pouches) to amplify their calls."
            },
            {
                "question": "True or False: All frog species make sounds.",
                "options": ["True", "False"],
                "correct": "False", 
                "explanation": "Some frogs are actually silent or make very minimal sounds."
            }
        ]
        
        if not st.session_state.quiz_started:
            if st.button("Start Quiz"):
                st.session_state.quiz_started = True
                st.session_state.quiz_score = 0
                st.session_state.current_question = 0
                st.session_state.questions_asked = []
                st.experimental_rerun()
        else:
            # Show current score
            st.markdown(f"**Current Score: {st.session_state.quiz_score}/{len(st.session_state.questions_asked)}**")
            
            if st.session_state.current_question < len(questions):
                # Get current question
                current_q = questions[st.session_state.current_question]
                
                # Display question
                st.markdown(f"#### Question {st.session_state.current_question + 1}")
                st.markdown(current_q["question"])
                
                # If there's an audio URL, play it with fallback
                if "audio_url" in current_q:
                    try:
                        # Try local file first
                        local_path = current_q["audio_url"]
                        if os.path.exists(local_path):
                            with open(local_path, 'rb') as f:
                                audio_bytes = f.read()
                            st.audio(audio_bytes, format='audio/mp3')
                        elif "remote_url" in current_q:
                            # Fall back to remote URL if local file doesn't exist
                            st.audio(current_q["remote_url"])
                        else:
                            st.error("Audio file not available.")
                    except Exception as e:
                        st.error(f"Could not play audio: {e}")
                        if "remote_url" in current_q:
                            st.info(f"Try accessing the audio directly: {current_q['remote_url']}")
                
                # Get user answer
                user_answer = st.radio(
                    "Choose your answer:",
                    options=current_q["options"],
                    key=f"question_{st.session_state.current_question}"
                )
                
                # Check answer when user submits
                if st.button("Submit Answer"):
                    st.session_state.questions_asked.append(st.session_state.current_question)
                    
                    if user_answer == current_q["correct"]:
                        st.success(f"Correct! {current_q['explanation']}")
                        st.session_state.quiz_score += 1
                    else:
                        st.error(f"Incorrect. The right answer is: {current_q['correct']}. {current_q['explanation']}")
                    
                    # Move to next question
                    st.session_state.current_question += 1
                    
                    # If we've reached the end, show final score
                    if st.session_state.current_question >= len(questions):
                        st.markdown(f"### Quiz Complete!")
                        st.markdown(f"Your final score: {st.session_state.quiz_score}/{len(questions)}")
                        
                        # Provide feedback based on score
                        if st.session_state.quiz_score == len(questions):
                            st.balloons()
                            st.success("Perfect score! You're a frog call expert! 🏆")
                        elif st.session_state.quiz_score >= len(questions) * 0.7:
                            st.success("Great job! You know your frog calls pretty well!")
                        elif st.session_state.quiz_score >= len(questions) * 0.5:
                            st.info("Good effort! You're learning about frog calls.")
                        else:
                            st.info("Keep learning about frog calls! They're fascinating.")
                        
                        # Option to restart
                        if st.button("Restart Quiz"):
                            st.session_state.quiz_started = False
                            st.experimental_rerun()
                    else:
                        # Continue to next question
                        st.button("Next Question", on_click=st.experimental_rerun)
            
            else:
                # Show final results if we're at the end
                st.markdown(f"### Quiz Complete!")
                st.markdown(f"Your final score: {st.session_state.quiz_score}/{len(questions)}")
                
                # Option to restart
                if st.button("Restart Quiz"):
                    st.session_state.quiz_started = False
                    st.experimental_rerun()
    
    def _check_audio_url(self, url):
        """Check if an audio URL is valid and provide troubleshooting info if not."""
        # Skip checks for local files
        if url.startswith('static/audio/'):
            return
            
        try:
            response = requests.head(url, timeout=2)
            if response.status_code != 200:
                st.warning(f"The audio URL may not be accessible (Status code: {response.status_code})")
                st.info("If the audio doesn't play below, try accessing it directly: " + url)
        except Exception as e:
            st.warning(f"Could not verify audio URL: {e}")

# Main function to use in Streamlit app
def render_frog_sounds_section():
    """Render the full frog sounds section in the Streamlit app."""
    sound_player = FrogSoundPlayer()
    
    # Create tabs for different sound-related sections
    tab1, tab2, tab3 = st.tabs(["Frog Call Explorer", "Fun Facts", "Sound Quiz"])
    
    with tab1:
        sound_player.render_call_player()
    
    with tab2:
        sound_player.render_fun_facts()
    
    with tab3:
        sound_player.render_interactive_quiz()

# Example usage as standalone
if __name__ == "__main__":
    st.set_page_config(page_title="Frog Sounds", page_icon="🐸")
    st.title("🐸 Frog Sounds Explorer")
    render_frog_sounds_section() 