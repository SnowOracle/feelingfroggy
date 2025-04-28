import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
from PIL import Image
import io
import os
import random
from frog_identifier import FrogIdentifier
from frog_sounds import render_frog_sounds_section

# Set page configuration
st.set_page_config(
    page_title="Feeling Froggy - Interactive Frog Explorer",
    page_icon="🐸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3CB371;
    }
    .species-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f8f0;
        margin-bottom: 1rem;
    }
    .species-name {
        color: #2E8B57;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .species-scientific {
        font-style: italic;
        color: #666;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
@st.cache_data
def load_frog_data():
    data_path = os.path.join("data", "frog_species.csv")
    return pd.read_csv(data_path)

# Sidebar navigation
st.sidebar.title("🐸 Feeling Froggy")
page = st.sidebar.radio(
    "Choose a section:",
    ["Home", "Frog Species Explorer", "Frog Identifier", "Frog Anatomy", "Frog Conservation", "Frog Life Cycle", "Fun Facts"]
)

# Home page
if page == "Home":
    st.markdown("<h1 class='main-header'>Welcome to Feeling Froggy! 🐸</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>Your Interactive Guide to the Fascinating World of Frogs</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        This app is designed for frog enthusiasts and anyone curious about these amazing amphibians.
        Explore different species, learn about frog anatomy, understand conservation efforts,
        and discover the incredible life cycle of frogs!
        
        **Use the sidebar to navigate through different sections of the app.**
        """)
        
        st.markdown("### What makes frogs special?")
        st.write("""
        - Frogs are amphibians that live both in water and on land
        - They have unique adaptations for their semi-aquatic lifestyle
        - Frogs play crucial roles in ecosystems as both predator and prey
        - They are sensitive to environmental changes, making them important bioindicators
        """)
    
    with col2:
        # Placeholder for an image - you can replace with a real image URL later
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Frog_in_pond.jpg/1200px-Frog_in_pond.jpg", caption="A frog in its natural habitat")

# Frog Species Explorer page
elif page == "Frog Species Explorer":
    st.markdown("<h1 class='main-header'>Frog Species Explorer 🔍</h1>", unsafe_allow_html=True)
    
    # Load data from CSV
    try:
        df = load_frog_data()
        
        # Filters
        st.sidebar.markdown("### Filters")
        habitat_filter = st.sidebar.multiselect("Select habitat type:", df["habitat"].unique())
        region_filter = st.sidebar.multiselect("Select region:", df["region"].unique())
        conservation_filter = st.sidebar.multiselect("Select conservation status:", df["conservation_status"].unique())
        
        # Apply filters
        filtered_df = df.copy()
        if habitat_filter:
            filtered_df = filtered_df[filtered_df["habitat"].isin(habitat_filter)]
        if region_filter:
            filtered_df = filtered_df[filtered_df["region"].isin(region_filter)]
        if conservation_filter:
            filtered_df = filtered_df[filtered_df["conservation_status"].isin(conservation_filter)]
        
        # Display results
        st.markdown(f"### Found {len(filtered_df)} frog species")
        
        # Toggle between table and card view
        view_type = st.radio("Select view:", ["Card View", "Table View"])
        
        if view_type == "Table View":
            # Display as table
            st.dataframe(filtered_df)
        else:
            # Display as cards
            cols = st.columns(2)
            
            for i, (_, row) in enumerate(filtered_df.iterrows()):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="species-card">
                        <div class="species-name">{row['name']}</div>
                        <div class="species-scientific">{row['scientific_name']}</div>
                        <img src="{row['image_url']}" style="width:100%; border-radius:5px; margin:10px 0;">
                        <p><strong>Habitat:</strong> {row['habitat']}</p>
                        <p><strong>Region:</strong> {row['region']}</p>
                        <p><strong>Conservation:</strong> {row['conservation_status']}</p>
                        <p><strong>Size:</strong> {row['size_cm']} cm</p>
                        <p><strong>Lifespan:</strong> {row['lifespan_years']} years</p>
                        <p><strong>Diet:</strong> {row['diet']}</p>
                        <p><strong>Color:</strong> {row['color']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Visualizations
        st.markdown("### Species Distribution")
        
        # Habitat distribution
        fig1 = px.bar(
            df.groupby('habitat').size().reset_index(name='count'),
            x='habitat', 
            y='count',
            title="Number of Frog Species by Habitat Type",
            color='habitat'
        )
        st.plotly_chart(fig1)
        
        # Region distribution
        fig2 = px.pie(
            df.groupby('region').size().reset_index(name='count'),
            values='count',
            names='region', 
            title="Frog Species by Region",
            hole=0.4
        )
        st.plotly_chart(fig2)
        
        # Conservation status
        fig3 = px.bar(
            df.groupby('conservation_status').size().reset_index(name='count'),
            x='conservation_status', 
            y='count',
            title="Conservation Status of Frog Species",
            color='conservation_status',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig3)
        
    except Exception as e:
        st.error(f"Error loading frog species data: {e}")
        st.info("Please make sure the frog_species.csv file exists in the data directory.")

# Frog Identifier page
elif page == "Frog Identifier":
    st.markdown("<h1 class='main-header'>Frog Identifier 🔍</h1>", unsafe_allow_html=True)
    
    st.write("""
    Upload an image of a frog, and our identifier will try to determine the species.
    
    Note: This is a demonstration feature. In a real application, this would use a trained 
    machine learning model for accurate identification. The current implementation provides
    random results for demonstration purposes.
    """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a frog image", type=["jpg", "jpeg", "png"])
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if uploaded_file:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Add an identify button
            if st.button("Identify Frog Species"):
                with st.spinner("Identifying frog species..."):
                    # Simulate processing time
                    import time
                    time.sleep(2)
                    
                    # Use our identifier
                    identifier = FrogIdentifier()
                    results = identifier.identify_from_image(image)
                    
                    # Store results in session state for display
                    st.session_state.identification_results = results
        else:
            # Show a placeholder or demo image
            st.info("Upload an image to identify the frog species.")
            
            # Option to use a test image
            if st.button("Use a Demo Image"):
                # Use a random frog from our dataset
                try:
                    df = load_frog_data()
                    random_frog = df.iloc[random.randint(0, len(df)-1)]
                    
                    st.image(random_frog['image_url'], caption=f"Demo Image: {random_frog['name']}", use_column_width=True)
                    
                    if st.button("Identify This Frog"):
                        with st.spinner("Identifying frog species..."):
                            # Simulate processing time
                            import time
                            time.sleep(2)
                            
                            # Use our identifier
                            identifier = FrogIdentifier()
                            results = identifier.identify_from_image()
                            
                            # Store results in session state for display
                            st.session_state.identification_results = results
                            
                            # Force a rerun to display results
                            st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error loading demo image: {e}")
    
    with col2:
        # Display identification results if available
        if 'identification_results' in st.session_state:
            results = st.session_state.identification_results
            
            st.markdown("### Identification Results")
            st.write(results['message'])
            
            for i, result in enumerate(results['results']):
                with st.container():
                    st.markdown(f"""
                    <div class="species-card">
                        <div class="species-name">{result['name']}</div>
                        <div class="species-scientific">{result['scientific_name']}</div>
                        <div style="margin-bottom:10px;">
                            <strong>Confidence:</strong> 
                            <div style="width:100%; background-color:#eee; height:20px; border-radius:10px;">
                                <div style="width:{result['confidence']}%; background-color:#2E8B57; height:20px; border-radius:10px;">
                                    <span style="padding-left:10px; color:white;">{result['confidence']}%</span>
                                </div>
                            </div>
                        </div>
                        <img src="{result['image_url']}" style="width:100%; border-radius:5px; margin:10px 0;">
                        <p><strong>Habitat:</strong> {result['habitat']}</p>
                        <p><strong>Region:</strong> {result['region']}</p>
                        <p><strong>Conservation Status:</strong> {result['conservation_status']}</p>
                    </div>
                    """, unsafe_allow_html=True)

# Frog Anatomy page
elif page == "Frog Anatomy":
    st.markdown("<h1 class='main-header'>Frog Anatomy 🔬</h1>", unsafe_allow_html=True)
    
    st.write("""
    Frogs have unique anatomical features that help them thrive in their environments.
    Explore the various parts of a frog and learn about their functions.
    """)
    
    # Interactive anatomy diagram - placeholder
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Frog_anatomy_en.svg/1200px-Frog_anatomy_en.svg.png", caption="Frog Anatomy Diagram")
    
    # Anatomy information
    with st.expander("External Anatomy"):
        st.write("""
        - **Skin**: Permeable, helps in respiration and water absorption
        - **Eyes**: Bulging eyes provide a wide field of vision
        - **Tympanum**: External ear drum for hearing
        - **Legs**: Powerful hind legs for jumping, webbed feet for swimming
        """)
    
    with st.expander("Internal Anatomy"):
        st.write("""
        - **Heart**: Three-chambered heart
        - **Lungs**: Simple, sac-like lungs for respiration
        - **Digestive System**: Complete digestive tract with specialized parts
        - **Excretory System**: Kidneys, urinary bladder, and cloaca
        """)

# Frog Conservation page
elif page == "Frog Conservation":
    st.markdown("<h1 class='main-header'>Frog Conservation 🌍</h1>", unsafe_allow_html=True)
    
    st.write("""
    Frogs face numerous threats globally, including habitat loss, pollution, climate change, 
    and diseases like chytrid fungus. Learn about conservation efforts and how you can help.
    """)
    
    # Conservation status visualization - sample data
    conservation_data = {
        "Status": ["Least Concern", "Near Threatened", "Vulnerable", "Endangered", "Critically Endangered", "Extinct"],
        "Percentage": [40, 20, 15, 12, 10, 3]
    }
    df_conservation = pd.DataFrame(conservation_data)
    
    fig = px.pie(df_conservation, values="Percentage", names="Status", 
                 title="Global Conservation Status of Frog Species",
                 color_discrete_sequence=px.colors.sequential.Viridis)
    st.plotly_chart(fig)
    
    st.markdown("### Major Threats to Frogs")
    threats = {
        "Threat": ["Habitat Loss", "Climate Change", "Pollution", "Disease", "Invasive Species"],
        "Impact": [35, 25, 20, 15, 5]
    }
    df_threats = pd.DataFrame(threats)
    
    fig_threats = px.bar(df_threats, x="Threat", y="Impact", 
                         title="Major Threats to Frog Populations",
                         color="Threat")
    st.plotly_chart(fig_threats)
    
    st.markdown("### How You Can Help")
    st.write("""
    - Support conservation organizations focused on amphibian protection
    - Reduce use of pesticides and chemicals that can harm frogs
    - Participate in citizen science projects to monitor local frog populations
    - Create frog-friendly habitats in your backyard with small ponds
    - Educate others about the importance of frogs to ecosystems
    """)

# Frog Life Cycle page
elif page == "Frog Life Cycle":
    st.markdown("<h1 class='main-header'>Frog Life Cycle 🥚➡️🐸</h1>", unsafe_allow_html=True)
    
    st.write("""
    Frogs undergo metamorphosis, transforming from aquatic tadpoles to terrestrial adults.
    Explore the fascinating stages of a frog's life cycle.
    """)
    
    # Life cycle stages
    stages = ["Egg", "Tadpole", "Tadpole with legs", "Froglet", "Adult Frog"]
    
    # Interactive life cycle explorer
    selected_stage = st.select_slider("Explore Life Cycle Stages", options=stages)
    
    if selected_stage == "Egg":
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Frogeggs.JPG/1200px-Frogeggs.JPG", caption="Frog Eggs (spawn)")
        st.write("""
        **Egg Stage**
        
        Frog eggs are usually laid in water in large clusters called spawn. 
        Each egg is protected by a jelly-like substance. Depending on the species, 
        a female frog can lay hundreds to thousands of eggs at once.
        
        **Duration**: 1-3 weeks, depending on species and temperature
        """)
    
    elif selected_stage == "Tadpole":
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Rana_temporaria_tadpole.jpg/1200px-Rana_temporaria_tadpole.jpg", caption="Tadpole")
        st.write("""
        **Tadpole Stage**
        
        After hatching, tadpoles breathe through gills and have a long tail for swimming.
        They are herbivorous, feeding mainly on algae and other plant matter.
        
        **Duration**: 6-12 weeks, depending on species and environment
        """)
    
    elif selected_stage == "Tadpole with legs":
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Rana_temporaria_metamorphosis.jpg/800px-Rana_temporaria_metamorphosis.jpg", caption="Tadpole with Legs")
        st.write("""
        **Tadpole with Legs Stage**
        
        As metamorphosis progresses, tadpoles develop hind legs first, followed by front legs.
        During this time, internal changes are also occurring, including the development of lungs.
        
        **Duration**: 1-4 weeks
        """)
    
    elif selected_stage == "Froglet":
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Froglet.jpg/800px-Froglet.jpg", caption="Froglet")
        st.write("""
        **Froglet Stage**
        
        The tail begins to shrink as it's absorbed by the body. The froglet begins to look more like a frog,
        but it's smaller than an adult. It can breathe through lungs and spend time on land.
        
        **Duration**: 2-4 weeks
        """)
    
    elif selected_stage == "Adult Frog":
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Frog_in_pond.jpg/800px-Frog_in_pond.jpg", caption="Adult Frog")
        st.write("""
        **Adult Frog Stage**
        
        The fully developed frog has no tail, breathes through lungs and skin, and has a carnivorous diet.
        It can live both in water and on land. When mature, it can reproduce and begin the cycle again.
        
        **Lifespan**: 2-20 years, depending on species
        """)

# Fun Facts page
elif page == "Fun Facts":
    st.markdown("<h1 class='main-header'>Fun Frog Facts 🎮</h1>", unsafe_allow_html=True)
    
    # Use our enhanced frog sounds module
    render_frog_sounds_section()
    
    # Fun fact generator
    st.markdown("<h2 class='sub-header'>Random Frog Facts</h2>", unsafe_allow_html=True)
    if st.button("Generate a Random Frog Fact"):
        facts = [
            "Some frogs can jump over 20 times their body length in a single leap!",
            "The goliath frog is the largest frog species, measuring up to 32 cm (12.6 inches) in length and weighing up to 3.3 kg (7.2 lbs).",
            "The smallest frog is the Paedophryne amauensis, which is only about 7.7 mm long!",
            "A group of frogs is called an 'army'.",
            "Frogs don't drink water - they absorb it through their skin.",
            "Some frogs can freeze during winter and thaw in spring without harmful effects.",
            "Frogs have been on Earth for more than 200 million years, outliving dinosaurs.",
            "There are over 7,000 species of frogs worldwide.",
            "The glass frog has transparent skin, allowing you to see its internal organs.",
            "Some poison dart frogs have enough toxin to kill 10 adult humans!",
            "Frogs typically lay eggs in water, but some species carry eggs on their backs or even in their stomachs!",
            "The golden poison dart frog has enough toxin to kill up to 20,000 mice.",
            "Some frogs can change color depending on temperature, light, and moisture.",
            "Frogs completely close their eyes when they swallow food.",
            "The Titicaca water frog never develops lungs and breathes entirely through its skin.",
            "The wood frog can survive being frozen solid during winter and thaws back to life in spring.",
            "The waxy monkey tree frog coats itself in a waxy substance to prevent water loss.",
            "The Vietnamese mossy frog looks exactly like moss as a form of camouflage.",
            "The Darwin's frog keeps its tadpoles in its vocal sac until they develop into froglets.",
            "The hairy frog breaks its own toe bones to create claws when threatened!"
        ]
        import random
        st.info(random.choice(facts)) 