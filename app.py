import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
from datetime import datetime
import os
import base64
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="ENS Dashboard Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme mode will be set in main function
theme_mode = "Light"  # Default theme

# Custom CSS for light and dark themes - will be applied dynamically in main function

@st.cache_data
def load_data():
    """Load and process the ensemble data from JSON file"""
    try:
        with open('Find_Ensembles_ with Open Seats_ _(RE).json', 'r') as file:
            data = json.load(file)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Clean and process the data
        df['secInstrumentation_seatsavail'] = pd.to_numeric(df['secInstrumentation_seatsavail'], errors='coerce')
        df['secInstrumentation_activestucount'] = pd.to_numeric(df['secInstrumentation_activestucount'], errors='coerce')
        df['secInstrumentation_seatscap'] = pd.to_numeric(df['secInstrumentation_seatscap'], errors='coerce')
        df['ratingOverall'] = pd.to_numeric(df['ratingOverall'], errors='coerce')
        
        # Calculate additional metrics
        df['enrollment_rate'] = (df['secInstrumentation_activestucount'] / df['secInstrumentation_seatscap'] * 100).fillna(0)
        df['open_seats'] = df['secInstrumentation_seatscap'] - df['secInstrumentation_activestucount']
        
        # Process rhythm instruments data
        df['rhythm_instruments'] = df['rhythminstrument'].apply(lambda x: x if isinstance(x, list) else [])
        df['rhythm_enrolled'] = df['rhythmenrolled'].apply(lambda x: [int(i) for i in x] if isinstance(x, list) else [])
        df['rhythm_needed'] = df['rhythmneeded'].apply(lambda x: x if isinstance(x, list) else [])
        
        # Create instrument status columns
        instruments = ['GUIT', 'PNO', 'BASS', 'DRUMS', 'VOICE']
        for i, instrument in enumerate(instruments):
            df[f'{instrument}_enrolled'] = df['rhythm_enrolled'].apply(
                lambda x: x[i] if i < len(x) else 0
            )
            df[f'{instrument}_needed'] = df['rhythm_needed'].apply(
                lambda x: x.count(instrument)
            )
            df[f'{instrument}_status'] = df.apply(
                lambda row: 'Filled' if row[f'{instrument}_enrolled'] > 0 else 
                           ('Needed' if row[f'{instrument}_needed'] > 0 else 'Not Required'),
                axis=1
            )
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def get_status_color(status):
    """Get color for status indicators"""
    if status == 'Filled':
        return '#4caf50'  # Green
    elif status == 'Needed':
        return '#f44336'  # Red
    else:
        return '#ff9800'  # Orange

def identify_performance_classes(df):
    """Identify performance classes where faculty cannot be scheduled for rating auditions"""
    performance_classes = []
    
    for _, ensemble in df.iterrows():
        section_name = ensemble['secInstrumentation_sectionname']
        course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
        faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
        
        # Check if this is a performance class (ENMX-100 or specific patterns)
        is_performance_class = False
        performance_reason = ""
        
        # Check for ENMX-100 classes
        if 'ENMX-100' in section_name:
            is_performance_class = True
            performance_reason = "ENMX-100 Performance Class"
        
        # Check for specific faculty patterns (you can add more faculty names here)
        elif any(faculty_name in faculty for faculty_name in ['PISJ', 'ENDS']):
            is_performance_class = True
            performance_reason = f"Faculty {faculty} - Cannot be scheduled for rating auditions"
        
        # Check for other performance class patterns
        elif any(keyword in course_title.upper() for keyword in ['PERFORMANCE', 'ENSEMBLE', 'RECITAL']):
            is_performance_class = True
            performance_reason = "Performance/Ensemble Class"
        
        if is_performance_class:
            days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
            time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
            enrolled_count = ensemble['secInstrumentation_activestucount']
            total_capacity = ensemble['secInstrumentation_seatscap']
            enrollment_rate = ensemble['enrollment_rate']
            style = ensemble['style']
            rating = ensemble['ratingOverall']
            
            performance_classes.append({
                'section_name': section_name,
                'course_title': course_title,
                'faculty': faculty,
                'days': days,
                'time': time,
                'enrolled_count': enrolled_count,
                'total_capacity': total_capacity,
                'enrollment_rate': enrollment_rate,
                'style': style,
                'rating': rating,
                'performance_reason': performance_reason
            })
    
    return performance_classes

def categorize_faculty_contract(faculty_name):
    """Categorize faculty by contract type based on name patterns or manual mapping"""
    # This is a placeholder function - in a real implementation, this would come from a database
    # or be manually configured by staff
    
    # Example mappings - these would be configurable
    faculty_contract_mapping = {
        # Full Time Faculty
        'Lello Molinari': 'FT',
        'Eric Doob': 'FT',
        'Sharik Hasan': 'FT',
        'Robert Schlink': 'FT',
        'Consuelo Candelaria-Barry': 'FT',

        # Part Time 3-Year Contract
        'Albino Mbie': 'PT3yr',
        'Mark Copeland': 'PT3yr',
        
        # Part Time Special Circumstances
        'Ricardo Monzon': 'PT_special',
        'Alexandria Dewalt': 'PT_special',
        'Robert Pate': 'PT_special',
        'Anastassiya Petrova': 'PT_special',
        
        # Adjunct Faculty
        'Tolieth Marks': 'adjunct',
        'Elan Trotman': 'adjunct',
    }
    
    return faculty_contract_mapping.get(faculty_name, 'Unknown')

def get_contract_color(contract_type):
    """Get color for contract type"""
    color_mapping = {
        'FT': '#ff0000',  # Red
        'PT3yr': '#0000ff',  # Blue
        'PT_special': '#ffa500',  # Orange
        'adjunct': '#8b4513',  # Brown
        'Unknown': '#808080'  # Gray
    }
    return color_mapping.get(contract_type, '#808080')

def get_registration_priority_score(enrolled_count, contract_type):
    """Calculate registration priority score based on student count and faculty contract"""
    # Priority order: 3 students > 2 students > 1 student > 0 students
    # Within each student count, prioritize by contract type: FT > PT3yr > PT_special > adjunct
    
    contract_priority = {
        'FT': 4,
        'PT3yr': 3,
        'PT_special': 2,
        'adjunct': 1,
        'Unknown': 0
    }
    
    # Base score from student count (higher is better)
    student_score = enrolled_count * 10
    
    # Contract priority score
    contract_score = contract_priority.get(contract_type, 0)
    
    # Total score (student count is primary, contract type is secondary)
    return student_score + contract_score

def analyze_registration_preferences(df):
    """Analyze classes for registration preferences based on student count and faculty contract"""
    registration_data = []
    
    for _, ensemble in df.iterrows():
        faculty_names = ensemble['secInstrumentation_facnamepreffml']
        if isinstance(faculty_names, list) and faculty_names:
            faculty_name = faculty_names[0]  # Take first faculty member
            contract_type = categorize_faculty_contract(faculty_name)
            enrolled_count = ensemble['secInstrumentation_activestucount']
            priority_score = get_registration_priority_score(enrolled_count, contract_type)
            
            # Determine priority level
            if enrolled_count == 3:
                priority_level = "HIGHEST - 3 instruments/ratings"
            elif enrolled_count == 2:
                priority_level = "HIGH - 2 instruments/ratings"
            elif enrolled_count == 1:
                priority_level = "MEDIUM - 1 instrument/rating"
            else:
                priority_level = "LOW - 0 instruments/ratings"
            
            registration_data.append({
                'section_name': ensemble['secInstrumentation_sectionname'],
                'course_title': ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A',
                'faculty': faculty_name,
                'contract_type': contract_type,
                'enrolled_count': enrolled_count,
                'total_capacity': ensemble['secInstrumentation_seatscap'],
                'enrollment_rate': ensemble['enrollment_rate'],
                'priority_score': priority_score,
                'priority_level': priority_level,
                'days': ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A',
                'time': f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}",
                'style': ensemble['style'],
                'rating': ensemble['ratingOverall'],
                'instruments_needed': ', '.join(ensemble['rhythmneeded']) if isinstance(ensemble['rhythmneeded'], list) else 'None'
            })
    
    # Sort by priority score (highest first)
    registration_data.sort(key=lambda x: x['priority_score'], reverse=True)
    return registration_data

def get_faculty_image_path(faculty_name):
    """Get the path to faculty image/document if it exists"""
    # Create a safe filename from faculty name
    safe_name = "".join(c for c in faculty_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    
    # Check for different file extensions
    extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    for ext in extensions:
        file_path = f"faculty_images/{safe_name}{ext}"
        if os.path.exists(file_path):
            return file_path, ext.lstrip('.')
    
    return None, None

def save_faculty_image(faculty_name, uploaded_file):
    """Save uploaded faculty image/document"""
    try:
        # Create faculty_images directory if it doesn't exist
        os.makedirs("faculty_images", exist_ok=True)
        
        # Create a safe filename from faculty name
        safe_name = "".join(c for c in faculty_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        # Get file extension from uploaded file
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Validate file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']
        if file_extension not in allowed_extensions:
            st.error(f"❌ Unsupported file type. Please upload: {', '.join(allowed_extensions).upper()}")
            return False
        
        # Save the uploaded file with original extension
        file_path = f"faculty_images/{safe_name}.{file_extension}"
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return True
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False

def display_faculty_image(faculty_name, width=100, height=100):
    """Display faculty image/document with fallback to placeholder"""
    image_path, file_type = get_faculty_image_path(faculty_name)
    
    if image_path and file_type in ['jpg', 'jpeg', 'png']:
        try:
            image = Image.open(image_path)
            # Resize image to fit the card
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to base64 for display
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{img_str}"
        except Exception as e:
            st.error(f"Error loading image for {faculty_name}: {str(e)}")
    
    # Return placeholder image (you can replace this with a default image)
    return None

def get_faculty_file_info(faculty_name):
    """Get faculty file information for display"""
    image_path, file_type = get_faculty_image_path(faculty_name)
    
    if image_path:
        return {
            'path': image_path,
            'type': file_type,
            'name': os.path.basename(image_path),
            'size': os.path.getsize(image_path) if os.path.exists(image_path) else 0
        }
    
    return None

def main():
    # Load data first
    df = load_data()
    
    if df.empty:
        st.error("No data loaded. Please check the JSON file.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Term filter
    terms = sorted(df['bSecTerm'].unique())
    selected_term = st.sidebar.selectbox("Select Term", terms, index=len(terms)-1, key="term_filter")
    
    # Style filter
    styles = ['All'] + sorted(df['style'].unique())
    selected_style = st.sidebar.selectbox("Select Style", styles, key="style_filter")
    
    # Rating filter
    ratings = ['All'] + sorted(df['ratingOverall'].unique())
    selected_rating = st.sidebar.selectbox("Select Rating", ratings, key="rating_filter")
    
    # Instrument filter
    instruments = ['All', 'GUIT', 'PNO', 'BASS', 'DRUMS', 'VOICE']
    selected_instrument = st.sidebar.selectbox("Filter by Instrument Need", instruments, key="instrument_filter")
    
    # Sorting options
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Sort Options")
    
    sort_options = [
        "Default (No Sorting)",
        "Priority Order: 3 Students > 2 > 1 > 0 (FT > PT3yr > PT_special > adjunct)",
        "Enrollment Count (High to Low)",
        "Enrollment Count (Low to High)",
        "Class Name (A-Z)",
        "Faculty Name (A-Z)"
    ]
    selected_sort = st.sidebar.selectbox("Sort Classes By", sort_options, key="sort_filter")
    
    # Specific instrument needs filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Specific Instrument Needs")
    
    bass_only = st.sidebar.checkbox("🎸 Show Only Classes Needing Bass Players", key="bass_filter")
    piano_only = st.sidebar.checkbox("🎹 Show Only Classes Needing Piano Players", key="piano_filter")
    drums_only = st.sidebar.checkbox("🥁 Show Only Classes Needing Drum Players", key="drums_filter")
    vocal_only = st.sidebar.checkbox("🎤 Show Only Classes Needing Vocal Players", key="vocal_filter")
    
    # Apply filters
    filtered_df = df[df['bSecTerm'] == selected_term]
    
    if selected_style != 'All':
        filtered_df = filtered_df[filtered_df['style'] == selected_style]
    
    if selected_rating != 'All':
        filtered_df = filtered_df[filtered_df['ratingOverall'] == selected_rating]
    
    if selected_instrument != 'All':
        filtered_df = filtered_df[filtered_df[f'{selected_instrument}_needed'] > 0]
    
    # Apply specific instrument filters
    if bass_only:
        filtered_df = filtered_df[filtered_df['BASS_needed'] > 0]
        st.sidebar.success(f"🎸 Showing {len(filtered_df)} classes that need Bass players")
    
    if piano_only:
        filtered_df = filtered_df[filtered_df['PNO_needed'] > 0]
        st.sidebar.success(f"🎹 Showing {len(filtered_df)} classes that need Piano players")
    
    if drums_only:
        filtered_df = filtered_df[filtered_df['DRUMS_needed'] > 0]
        st.sidebar.success(f"🥁 Showing {len(filtered_df)} classes that need Drum players")
    
    if vocal_only:
        filtered_df = filtered_df[filtered_df['VOICE_needed'] > 0]
        st.sidebar.success(f"🎤 Showing {len(filtered_df)} classes that need Vocal players")
    
    # Apply sorting based on user selection
    if selected_sort != "Default (No Sorting)":
        if selected_sort == "Priority Order: 3 Students > 2 > 1 > 0 (FT > PT3yr > PT_special > adjunct)":
            # Calculate priority scores for sorting
            def calculate_priority_score(row):
                enrolled_count = row['secInstrumentation_activestucount']
                # Get the first faculty name for contract type determination
                faculty_names = row['secInstrumentation_facnamepreffml']
                if isinstance(faculty_names, list) and faculty_names:
                    contract_type = categorize_faculty_contract(faculty_names[0])
                else:
                    contract_type = "Unknown"
                
                # Priority: 3 students > 2 > 1 > 0
                # Within each student count: FT > PT3yr > PT_special > adjunct
                contract_priority = {"FT": 4, "PT3yr": 3, "PT_special": 2, "adjunct": 1, "Unknown": 0}
                
                # Create a composite score: (student_count * 10) + contract_priority
                # This ensures 3 students always rank higher than 2 students, etc.
                return (enrolled_count * 10) + contract_priority.get(contract_type, 0)
            
            # Add priority score column and sort
            filtered_df = filtered_df.copy()
            filtered_df['priority_score'] = filtered_df.apply(calculate_priority_score, axis=1)
            filtered_df = filtered_df.sort_values('priority_score', ascending=False)
            filtered_df = filtered_df.drop('priority_score', axis=1)
            
        elif selected_sort == "Enrollment Count (High to Low)":
            filtered_df = filtered_df.sort_values('secInstrumentation_activestucount', ascending=False)
        elif selected_sort == "Enrollment Count (Low to High)":
            filtered_df = filtered_df.sort_values('secInstrumentation_activestucount', ascending=True)
        elif selected_sort == "Class Name (A-Z)":
            filtered_df = filtered_df.sort_values('secInstrumentation_sectionname', ascending=True)
        elif selected_sort == "Faculty Name (A-Z)":
            # Sort by the first faculty name in the list
            def get_first_faculty(row):
                faculty_names = row['secInstrumentation_facnamepreffml']
                if isinstance(faculty_names, list) and faculty_names:
                    return faculty_names[0]
                return ""
            
            filtered_df = filtered_df.copy()
            filtered_df['first_faculty'] = filtered_df.apply(get_first_faculty, axis=1)
            filtered_df = filtered_df.sort_values('first_faculty', ascending=True)
            filtered_df = filtered_df.drop('first_faculty', axis=1)
    
    # Enhanced theme selector at the top
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        # Theme Mode Selector with Icons
        theme_mode = st.selectbox(
            "🌙 Theme Mode",
            ["Light", "Dark"],
            key="theme_selector"
        )
    with col2:
        # Theme Color Selector
        theme_colors = {
            "Classic Blue": {"primary": "#4a9eff", "secondary": "#63b3ed", "accent": "#3182ce"},
            "Ocean Green": {"primary": "#38b2ac", "secondary": "#4fd1c7", "accent": "#319795"},
            "Sunset Orange": {"primary": "#ed8936", "secondary": "#f6ad55", "accent": "#dd6b20"},
            "Royal Purple": {"primary": "#9f7aea", "secondary": "#b794f4", "accent": "#805ad5"},
            "Coral Pink": {"primary": "#f687b3", "secondary": "#fbb6ce", "accent": "#e53e3e"},
            "Emerald": {"primary": "#48bb78", "secondary": "#68d391", "accent": "#38a169"}
        }
        
        selected_color_theme = st.selectbox(
            "🎨 Color Theme",
            list(theme_colors.keys()),
            key="color_theme_selector"
        )
        
        # Store selected colors in session state
        st.session_state['theme_colors'] = theme_colors[selected_color_theme]
    with col3:
        # Faculty Contract Management Button
        if st.button("⚙️ Faculty Contract Management", key="faculty_contract_btn"):
            st.session_state['show_faculty_management'] = not st.session_state.get('show_faculty_management', False)
    with col4:
        # Theme Preview
        colors = st.session_state.get('theme_colors', theme_colors["Classic Blue"])
        st.markdown(f"""
        <div style="
            display: flex; 
            gap: 8px; 
            align-items: center; 
            padding: 8px; 
            background: {'#2d3748' if theme_mode == 'Dark' else '#f7fafc'}; 
            border-radius: 8px;
            border: 1px solid {'#4a5568' if theme_mode == 'Dark' else '#e2e8f0'};
        ">
            <div style="
                width: 20px; 
                height: 20px; 
                background: {colors['primary']}; 
                border-radius: 50%;
                border: 2px solid {'#ffffff' if theme_mode == 'Dark' else '#000000'};
            "></div>
            <div style="
                width: 20px; 
                height: 20px; 
                background: {colors['secondary']}; 
                border-radius: 50%;
                border: 2px solid {'#ffffff' if theme_mode == 'Dark' else '#000000'};
            "></div>
            <div style="
                width: 20px; 
                height: 20px; 
                background: {colors['accent']}; 
                border-radius: 50%;
                border: 2px solid {'#ffffff' if theme_mode == 'Dark' else '#000000'};
            "></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Header with title
    st.markdown("""
    <div class="header-container">
        <div class="header-content">
            <h2 class="main-header">ENS Dashboard Hub</h2>
            <div class="status-display">
                <span class="status-label">Status</span>
                <span class="status-value">Active: """ + str(len(filtered_df)) + """ classes</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Faculty Contract Management Section
    if st.session_state.get('show_faculty_management', False):
        st.markdown("---")
        st.subheader("⚙️ Faculty Contract Management")
        
        # Get unique faculty names from the data
        all_faculty = set()
        for _, ensemble in filtered_df.iterrows():
            faculty_names = ensemble['secInstrumentation_facnamepreffml']
            if isinstance(faculty_names, list):
                all_faculty.update(faculty_names)
        
        faculty_list = sorted(list(all_faculty))
        
        if faculty_list:
            st.markdown("### 📝 Update Faculty Contract Types")
            st.markdown("Configure faculty contract types to improve registration preference calculations.")
            
            # Create a simple interface for updating faculty contracts
            selected_faculty = st.selectbox(
                "Select Faculty Member:",
                faculty_list,
                key="faculty_selector"
            )
            
            contract_type = st.selectbox(
                "Contract Type:",
                ["FT", "PT3yr", "PT_special", "adjunct", "Unknown"],
                key="contract_type_selector"
            )
            
            # Faculty Image Upload Section
            st.markdown("### 📸 Faculty Image Management")
            st.markdown("Upload profile images for faculty members to enhance the directory display.")
            
            # Image upload for selected faculty
            uploaded_image = st.file_uploader(
                f"Upload image for {selected_faculty}:",
                type=['jpg', 'jpeg', 'png'],
                key="faculty_image_upload"
            )
            
            if uploaded_image is not None:
                # Display preview
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(uploaded_image, caption=f"Preview for {selected_faculty}", width=150)
                
                with col2:
                    if st.button("Save Image", key="save_image_btn"):
                        if save_faculty_image(selected_faculty, uploaded_image):
                            st.success(f"✅ Image saved successfully for {selected_faculty}!")
                        else:
                            st.error("❌ Failed to save image. Please try again.")
            
            # Contract management buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Contract Type", key="update_contract_btn"):
                    # In a real implementation, this would save to a database or configuration file
                    st.success(f"Updated {selected_faculty} to {contract_type} contract type!")
                    st.info("Note: In a production system, this would be saved to a database.")
            
            with col2:
                if st.button("Reset All to Unknown", key="reset_contracts_btn"):
                    st.warning("Reset all faculty contract types to 'Unknown'!")
                    st.info("Note: In a production system, this would update the database.")
            
            # Display current faculty contract mappings
            st.markdown("### 📋 Current Faculty Contract Mappings")
            st.markdown("**Color Legend:**")
            st.markdown("""
            - <span style="color: #ff0000; font-weight: bold;">🔴 Red</span> = Full Time (FT)
            - <span style="color: #0000ff; font-weight: bold;">🔵 Blue</span> = Part Time 3-Year Contract (PT3yr)
            - <span style="color: #ffa500; font-weight: bold;">🟠 Orange</span> = Part Time Special Circumstances (PT_special)
            - <span style="color: #8b4513; font-weight: bold;">🟤 Brown</span> = Adjunct
            - <span style="color: #808080; font-weight: bold;">⚫ Gray</span> = Unknown
            """, unsafe_allow_html=True)
            
            # Display faculty list with their contract types in card view
            faculty_contract_display = []
            for faculty in faculty_list:
                contract_type = categorize_faculty_contract(faculty)
                color = get_contract_color(contract_type)
                faculty_contract_display.append({
                    'Faculty': faculty,
                    'Contract Type': contract_type,
                    'Color': color
                })
            
            # Search and Filter Section
            st.markdown("### 🔍 Search & Filter Faculty")
            
            # Search by faculty name
            search_term = st.text_input(
                "Search by faculty name:",
                placeholder="Enter faculty name...",
                key="faculty_search"
            )
            
            # Filter by contract type
            contract_filter = st.selectbox(
                "Filter by contract type:",
                ["All", "FT", "PT3yr", "PT_special", "adjunct", "Unknown"],
                key="contract_filter"
            )
            
            # Apply filters
            filtered_faculty = faculty_contract_display.copy()
            
            # Apply search filter
            if search_term:
                filtered_faculty = [f for f in filtered_faculty if search_term.lower() in f['Faculty'].lower()]
            
            # Apply contract type filter
            if contract_filter != "All":
                filtered_faculty = [f for f in filtered_faculty if f['Contract Type'] == contract_filter]
            
            # Display filtered results
            if filtered_faculty:
                st.markdown(f"### 👥 Faculty Directory ({len(filtered_faculty)} found)")
                
                # Show filter summary
                if search_term or contract_filter != "All":
                    filter_summary = []
                    if search_term:
                        filter_summary.append(f"Name: '{search_term}'")
                    if contract_filter != "All":
                        filter_summary.append(f"Contract: {contract_filter}")
                    
                    st.info(f"🔍 Showing results for: {' & '.join(filter_summary)}")
                
                # Create columns for responsive card layout
                cols = st.columns(3)
                for idx, faculty_info in enumerate(filtered_faculty):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        # Check if faculty has an image or file
                        faculty_image = display_faculty_image(faculty_info['Faculty'], width=80, height=80)
                        faculty_file_info = get_faculty_file_info(faculty_info['Faculty'])
                        
                        # Create a unique key for this faculty's edit section
                        edit_key = f"edit_{faculty_info['Faculty'].replace(' ', '_').replace('-', '_')}"
                        
                        # Determine what to display in the card
                        has_image = faculty_image is not None
                        has_file = faculty_file_info is not None
                        
                        if has_image:
                            # Display card with image
                            st.markdown(f"""
                            <div class="faculty-card" style="
                                padding: 1.5rem;
                                margin: 0.5rem 0;
                                text-align: center;
                                min-height: 200px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                            ">
                                <div style="
                                    margin-bottom: 1rem;
                                    display: flex;
                                    justify-content: center;
                                ">
                                    <img src="{faculty_image}" 
                                         style="
                                             width: 80px; 
                                             height: 80px; 
                                             border-radius: 50%; 
                                             object-fit: cover;
                                             border: 3px solid {faculty_info['Color']};
                                         "
                                         alt="{faculty_info['Faculty']}">
                                </div>
                                <div style="
                                    background-color: {faculty_info['Color']}; 
                                    color: white; 
                                    padding: 0.5rem 1rem; 
                                    border-radius: 0.5rem; 
                                    font-size: 0.9rem; 
                                    font-weight: bold; 
                                    margin-bottom: 1rem;
                                    display: inline-block;
                                    width: fit-content;
                                    margin-left: auto;
                                    margin-right: auto;
                                ">
                                    {faculty_info['Contract Type']}
                                </div>
                                <div style="
                                    font-size: 1.1rem; 
                                    font-weight: bold; 
                                    color: #333;
                                    margin-top: 0.5rem;
                                    line-height: 1.3;
                                    margin-bottom: 1rem;
                                ">
                                    {faculty_info['Faculty']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        elif has_file:
                            # Display card with file icon
                            file_icon = "📄" if faculty_file_info['type'] == 'pdf' else "🖼️"
                            st.markdown(f"""
                            <div class="faculty-card" style="
                                padding: 1.5rem;
                                margin: 0.5rem 0;
                                text-align: center;
                                min-height: 200px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                            ">
                                <div style="
                                    margin-bottom: 1rem;
                                    display: flex;
                                    justify-content: center;
                                ">
                                    <div style="
                                        width: 80px; 
                                        height: 80px; 
                                        border-radius: 50%; 
                                        background-color: #f0f0f0;
                                        border: 3px solid {faculty_info['Color']};
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        font-size: 2rem;
                                        color: #666;
                                    ">
                                        {file_icon}
                                    </div>
                                </div>
                                <div style="
                                    background-color: {faculty_info['Color']}; 
                                    color: white; 
                                    padding: 0.5rem 1rem; 
                                    border-radius: 0.5rem; 
                                    font-size: 0.9rem; 
                                    font-weight: bold; 
                                    margin-bottom: 1rem;
                                    display: inline-block;
                                    width: fit-content;
                                    margin-left: auto;
                                    margin-right: auto;
                                ">
                                    {faculty_info['Contract Type']}
                                </div>
                                <div style="
                                    font-size: 1.1rem; 
                                    font-weight: bold; 
                                    color: #333;
                                    margin-top: 0.5rem;
                                    line-height: 1.3;
                                    margin-bottom: 0.5rem;
                                ">
                                    {faculty_info['Faculty']}
                                </div>
                                <div style="
                                    font-size: 0.8rem; 
                                    color: #666;
                                    margin-bottom: 1rem;
                                ">
                                    📎 {faculty_file_info['type'].upper()} file
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Display card without image (placeholder)
                            st.markdown(f"""
                            <div class="faculty-card" style="
                                padding: 1.5rem;
                                margin: 0.5rem 0;
                                text-align: center;
                                min-height: 200px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                            ">
                                <div style="
                                    margin-bottom: 1rem;
                                    display: flex;
                                    justify-content: center;
                                ">
                                    <div style="
                                        width: 80px; 
                                        height: 80px; 
                                        border-radius: 50%; 
                                        background-color: #f0f0f0;
                                        border: 3px solid {faculty_info['Color']};
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        font-size: 2rem;
                                        color: #999;
                                    ">
                                        👤
                                    </div>
                                </div>
                                <div style="
                                    background-color: {faculty_info['Color']}; 
                                    color: white; 
                                    padding: 0.5rem 1rem; 
                                    border-radius: 0.5rem; 
                                    font-size: 0.9rem; 
                                    font-weight: bold; 
                                    margin-bottom: 1rem;
                                    display: inline-block;
                                    width: fit-content;
                                    margin-left: auto;
                                    margin-right: auto;
                                ">
                                    {faculty_info['Contract Type']}
                                </div>
                                <div style="
                                    font-size: 1.1rem; 
                                    font-weight: bold; 
                                    color: #333;
                                    margin-top: 0.5rem;
                                    line-height: 1.3;
                                    margin-bottom: 1rem;
                                ">
                                    {faculty_info['Faculty']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Add Edit button below each card
                        if st.button(f"✏️ Edit {faculty_info['Faculty']}", key=f"edit_btn_{edit_key}"):
                            st.session_state[f'edit_faculty_{edit_key}'] = not st.session_state.get(f'edit_faculty_{edit_key}', False)
                        
                        # Show edit section if button was clicked
                        if st.session_state.get(f'edit_faculty_{edit_key}', False):
                            st.markdown("---")
                            st.markdown(f"### 📸 Edit Profile for {faculty_info['Faculty']}")
                            
                            # Show current file information if exists
                            if faculty_file_info:
                                st.info(f"📎 **Current file:** {faculty_file_info['name']} ({faculty_file_info['type'].upper()}, {faculty_file_info['size']} bytes)")
                            
                            # File upload for this specific faculty
                            uploaded_file = st.file_uploader(
                                f"Upload new file for {faculty_info['Faculty']}:",
                                type=['jpg', 'jpeg', 'png', 'pdf'],
                                key=f"faculty_file_upload_{edit_key}",
                                help="Supported formats: JPG, JPEG, PNG, PDF"
                            )
                            
                            if uploaded_file is not None:
                                # Display file information
                                file_size = len(uploaded_file.getbuffer())
                                file_type = uploaded_file.name.split('.')[-1].lower()
                                
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    if file_type in ['jpg', 'jpeg', 'png']:
                                        st.image(uploaded_file, caption=f"Preview for {faculty_info['Faculty']}", width=150)
                                    else:
                                        st.markdown(f"""
                                        <div style="
                                            width: 150px; 
                                            height: 150px; 
                                            background-color: #f0f0f0;
                                            border: 2px dashed #ccc;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            margin: 0 auto;
                                        ">
                                            <div style="text-align: center;">
                                                <div style="font-size: 3rem;">📄</div>
                                                <div style="font-size: 0.8rem; color: #666;">PDF Preview</div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown(f"**File Details:**")
                                    st.markdown(f"- **Name:** {uploaded_file.name}")
                                    st.markdown(f"- **Type:** {file_type.upper()}")
                                    st.markdown(f"- **Size:** {file_size:,} bytes")
                                    
                                    if st.button("Save File", key=f"save_file_btn_{edit_key}"):
                                        if save_faculty_image(faculty_info['Faculty'], uploaded_file):
                                            st.success(f"✅ File saved successfully for {faculty_info['Faculty']}!")
                                            # Reset the edit state to close the edit section
                                            st.session_state[f'edit_faculty_{edit_key}'] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to save file. Please try again.")
                            
                            # Close edit section button
                            if st.button("Close", key=f"close_edit_{edit_key}"):
                                st.session_state[f'edit_faculty_{edit_key}'] = False
                                st.rerun()
                            
                            st.markdown("---")
            else:
                st.warning("🔍 No faculty found matching your search criteria.")
                st.markdown("**Try:**")
                st.markdown("- Clearing the search field")
                st.markdown("- Selecting 'All' in the contract filter")
                st.markdown("- Using different search terms")
        else:
            st.info("No faculty data available for management.")
        
        st.markdown("---")
    
    # Apply CSS based on selected theme and colors
    colors = st.session_state.get('theme_colors', {"primary": "#4a9eff", "secondary": "#63b3ed", "accent": "#3182ce"})
    
    if theme_mode == "Dark":
        st.markdown(f"""
        <style>
            /* Dark Theme Styles with Dynamic Colors */
            .stApp {{
                background-color: #1a1a1a;
                color: #ffffff;
            }}
            
            /* Header Container */
            .header-container {{
                background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
                border-bottom: 3px solid {colors['primary']};
                padding: 1.5rem 0;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }}
            
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            
            .main-header {{
                font-size: 2.8rem;
                color: {colors['primary']};
                font-weight: 700;
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            
            .header-controls {{
                display: flex;
                gap: 2rem;
                align-items: center;
            }}
            
            .status-display {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .status-label {{
                font-size: 0.8rem;
                color: #a0aec0;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .status-value {{
                font-size: 1rem;
                color: #ffffff;
                font-weight: 600;
                background: #2d3748;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                border: 1px solid {colors['secondary']};
            }}
            
            /* Instrument Card Styles */
            .instrument-card {{
                transition: all 0.4s ease;
            }}
            
            .instrument-card:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 15px 45px rgba(0, 0, 0, 0.5);
                border-color: {colors['primary']};
            }}
            
            /* Class List Styles */
            .class-list {
                display: grid;
                gap: 1rem;
            }
            
            .class-item {
                background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
                border: 1px solid #718096;
                border-radius: 0.75rem;
                padding: 1.5rem;
                transition: all 0.3s ease;
            }
            
            .class-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                border-color: {colors['primary']};
            }}
            
            .class-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }
            
            .class-name {
                font-size: 1.2rem;
                font-weight: 700;
                color: #ffffff;
            }
            
            .class-status {
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.8rem;
                font-weight: 600;
            }
            
            .status-needed {
                background: #742a2a;
                color: #fed7d7;
            }
            
            .status-filled {
                background: #22543d;
                color: #9ae6b4;
            }
            
            .class-details {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                font-size: 0.9rem;
            }
            
            .detail-item {
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }
            
            .detail-label {
                color: #a0aec0;
                font-weight: 600;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .detail-value {
                color: #ffffff;
                font-weight: 500;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
                color: #ffffff;
                padding: 2.5rem;
                border-radius: 1.5rem;
                border: 2px solid #4a5568;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                margin: 2rem 0;
                text-align: center;
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #4a9eff, #63b3ed);
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                border-color: #4a9eff;
            }
            
            .danger {
                background-color: #742a2a;
                border-color: #f56565;
                color: #fed7d7;
            }
            
            .warning {
                background-color: #744210;
                border-color: #ed8936;
                color: #fbd38d;
            }
            
            .success {
                background-color: #22543d;
                border-color: #48bb78;
                color: #9ae6b4;
            }
            
            .info-box {
                background: linear-gradient(135deg, #2a4365 0%, #1a365d 100%);
                color: #ffffff;
                padding: 2rem;
                border-radius: 1rem;
                margin: 2rem 0;
                border-left: 6px solid #4a9eff;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
                border: 2px solid #4a5568;
                position: relative;
                transition: all 0.4s ease;
                overflow: hidden;
            }
            
            .info-box::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 6px;
                height: 100%;
                background: linear-gradient(180deg, #4a9eff, #63b3ed);
            }
            
            .info-box:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
                border-color: #4a9eff;
            }
            
            .instrument-card {
                background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
                color: #ffffff;
                padding: 2.5rem;
                border-radius: 1.5rem;
                border: 2px solid #4a5568;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                margin: 2rem;
                text-align: center;
                min-height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
            }
            
            .instrument-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #4a9eff, #63b3ed);
            }
            
            .instrument-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                border-color: #4a9eff;
            }
            
            .instrument-card h3 {
                margin: 0 0 1rem 0;
                font-size: 1.5rem;
                font-weight: bold;
                color: #ffffff;
            }
            
            .instrument-card p {
                margin: 0.25rem 0;
                font-size: 1rem;
                color: #e2e8f0;
            }
            
            .instrument-card.danger {
                background-color: #742a2a;
                border-color: #f56565;
                color: #fed7d7;
            }
            
            .instrument-card.warning {
                background-color: #744210;
                border-color: #ed8936;
                color: #fbd38d;
            }
            
            .instrument-card.success {
                background-color: #22543d;
                border-color: #48bb78;
                color: #9ae6b4;
            }
            
            .status-icon {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
            
            /* Dark theme for Streamlit elements */
            .stSelectbox > div > div {
                background-color: #2d3748 !important;
                color: #ffffff !important;
            }
            
            .stTextInput > div > div > input {
                background-color: #2d3748 !important;
                color: #ffffff !important;
                border-color: #4a5568 !important;
            }
            
            /* Dark theme for text input labels */
            .stTextInput label {
                color: #ffffff !important;
                font-weight: bold !important;
                font-size: 1rem !important;
                margin-bottom: 0.5rem !important;
                display: block !important;
            }
            
            .stDataFrame {
                background-color: #2d3748 !important;
                color: #ffffff !important;
            }
            
                    /* Dark theme for tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #2d3748 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #4a5568 !important;
            color: #ffffff !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #4a9eff !important;
            color: #ffffff !important;
        }
        
        /* Custom class for red numbers in dark theme */
        .red-number {
            color: #ff0000 !important;
            font-weight: bold !important;
        }
        
        /* Faculty card styling for dark theme */
        .faculty-card {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%) !important;
            border: 2px solid #4a5568 !important;
            border-radius: 1rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        
        .faculty-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
            border-color: #4a9eff !important;
        }
        

            
            /* Dark theme for buttons */
            .stButton > button {
                background-color: #4a9eff !important;
                color: #ffffff !important;
                border-color: #4a9eff !important;
            }
            
            .stButton > button:hover {
                background-color: #3182ce !important;
            }
            
            /* Dark theme for sidebar */
            .css-1d391kg {
                background-color: #1a202c !important;
            }
            
            /* Dark theme for main content */
            .main .block-container {
                background-color: #1a1a1a !important;
            }
            
                    /* Dark theme for text elements */
        .stMarkdown {
            color: #ffffff !important;
        }
        
        /* Dark theme for success/error messages */
        .stAlert {
            background-color: #2d3748 !important;
            color: #ffffff !important;
        }
        
        /* Dark theme for success messages specifically */
        .stAlert[data-baseweb="notification"] {
            background-color: #22543d !important;
            color: #9ae6b4 !important;
            border-color: #48bb78 !important;
        }
        
        /* Dark theme for all success messages - more specific */
        .stAlert, .stAlert * {
            color: #9ae6b4 !important;
        }
        
        /* Dark theme for success message text specifically */
        .stAlert div, .stAlert span, .stAlert p {
            color: #9ae6b4 !important;
        }
        
                    /* Dark theme for all text elements - comprehensive coverage */
        .stText, .stMarkdown, .stSubheader, .stHeader, .stTitle, .stCaption {
            color: #ffffff !important;
        }
        
        /* Dark theme for all heading elements */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        /* Dark theme for Streamlit headings */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #ffffff !important;
        }
        
        /* Dark theme for sidebar text */
        .css-1d391kg .stMarkdown {
            color: #ffffff !important;
        }
        
        /* Dark theme for all paragraph and span elements */
        p, span, div {
            color: #ffffff !important;
        }
        
        /* Dark theme for Streamlit specific text elements */
        .stMarkdown p, .stMarkdown span, .stMarkdown div {
            color: #ffffff !important;
        }
        
        /* Dark theme for sidebar headings and text */
        .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg p, .css-1d391kg span {
            color: #ffffff !important;
        }
        
        /* Dark theme for main content text */
        .main .block-container p, .main .block-container span, .main .block-container div {
            color: #ffffff !important;
        }
        
        /* Dark theme for all Streamlit text widgets */
        .stTextInput label, .stSelectbox label, .stCheckbox label, .stRadio label {
            color: #ffffff !important;
        }
        
        /* Dark theme for file uploader text */
        .stFileUploader label, .stFileUploader p {
            color: #ffffff !important;
        }
        
        /* Dark theme for button text */
        .stButton button {
            color: #ffffff !important;
        }
        
        /* Dark theme for download button text */
        .stDownloadButton button {
            color: #ffffff !important;
        }
        
        /* Dark theme for expander text */
        .streamlit-expanderHeader {
            color: #ffffff !important;
        }
        
        /* Dark theme for metric text */
        .stMetric label, .stMetric div {
            color: #ffffff !important;
        }
        
        /* Dark theme for chart text */
        .js-plotly-plot .plotly .main-svg text {
            fill: #ffffff !important;
        }
        
        /* Dark theme for table text */
        .stDataFrame th, .stDataFrame td {
            color: #ffffff !important;
        }
        
        /* Dark theme for any remaining text elements */
        * {
            color: #ffffff !important;
        }
        
        /* Exception for specific colored elements */
        .danger, .warning, .success, .info-box, .instrument-card, .metric-card {
            color: inherit !important;
        }
        
        /* Exception for faculty cards */
        .faculty-card {
            color: inherit !important;
        }
        
        /* Exception for status badges */
        .status-needed, .status-filled, .class-status {
            color: inherit !important;
        }
            
            /* Dark theme for critical alert headers */
            .critical-alert-header {
                color: #f56565 !important;
                font-weight: bold !important;
            }
            
            /* Dark theme for critical alerts section */
            .critical-alerts-section {
                color: #ffffff !important;
            }
            
            .critical-alerts-section h3 {
                color: #f56565 !important;
            }
            
            .critical-alerts-section .stMarkdown {
                color: #ffffff !important;
            }
            
            /* Dark theme for success messages in critical alerts section */
            .critical-alerts-section .stAlert {
                background-color: #22543d !important;
                color: #9ae6b4 !important;
                border-color: #48bb78 !important;
            }
            
            /* Dark theme for success message text in critical alerts section - very specific */
            .critical-alerts-section .stAlert *,
            .critical-alerts-section .stAlert div,
            .critical-alerts-section .stAlert span,
            .critical-alerts-section .stAlert p {
                color: #9ae6b4 !important;
                font-weight: bold !important;
            }
            
            /* Dark theme for custom success message */
            .critical-alerts-section div[style*="background-color: #e8f5e8"] {
                background-color: #22543d !important;
                color: #9ae6b4 !important;
                border-left-color: #48bb78 !important;
            }
            
            /* Dark theme for info messages */
            .stAlert[data-baseweb="notification"][data-testid="stAlert"] {
                background-color: #2a4365 !important;
                color: #ffffff !important;
                border-color: #4a9eff !important;
            }
            
            /* Dark theme for warning messages */
            .stAlert[data-baseweb="notification"] {
                background-color: #744210 !important;
                color: #fbd38d !important;
                border-color: #ed8936 !important;
            }
            
            /* Dark theme for error messages */
            .stAlert[data-baseweb="notification"] {
                background-color: #742a2a !important;
                color: #fed7d7 !important;
                border-color: #f56565 !important;
            }
            
            /* Dark theme for all info boxes and containers */
            .stMarkdown div[style*="background-color"] {
                color: #ffffff !important;
            }
            
            /* Dark theme for any remaining text that might be hidden */
            .stMarkdown strong, .stMarkdown b {
                color: #ffffff !important;
            }
            
            /* Dark theme for list items */
            .stMarkdown ul li, .stMarkdown ol li {
                color: #ffffff !important;
            }
            
            /* Dark theme for links */
            .stMarkdown a {
                color: #4a9eff !important;
            }
            
            /* Dark theme for code blocks */
            .stMarkdown code {
                background-color: #2d3748 !important;
                color: #e2e8f0 !important;
            }
            
            /* Dark theme for blockquotes */
            .stMarkdown blockquote {
                border-left-color: #4a9eff !important;
                color: #e2e8f0 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light Theme (default) with Dynamic Colors
        st.markdown(f"""
        <style>
                    /* Light Theme Styles with Dynamic Colors */
            /* Header Container */
            .header-container {{
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border-bottom: 3px solid {colors['primary']};
                padding: 1.5rem 0;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            }}
            
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            
            .main-header {{
                font-size: 2.8rem;
                color: {colors['primary']};
                font-weight: 700;
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            
            .header-controls {{
                display: flex;
                gap: 2rem;
                align-items: center;
            }}
            
            .status-display {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.5rem;
            }}
            
            .status-label {{
                font-size: 0.8rem;
                color: #666666;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .status-value {{
                font-size: 1rem;
                color: #333333;
                font-weight: 600;
                background: #f8f9fa;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                border: 1px solid {colors['secondary']};
            }}
            
            /* Instrument Card Styles */
            .instrument-card {{
                transition: all 0.4s ease;
            }}
            
            .instrument-card:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 15px 45px rgba(0, 0, 0, 0.2);
                border-color: {colors['primary']};
            }}
            
            /* Class List Styles */
            .class-list {
                display: grid;
                gap: 1rem;
            }
            
            .class-item {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border: 1px solid #e0e0e0;
                border-radius: 0.75rem;
                padding: 1.5rem;
                transition: all 0.3s ease;
            }
            
            .class-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border-color: #2196f3;
            }
            
            .class-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }
            
            .class-name {
                font-size: 1.2rem;
                font-weight: 700;
                color: #333333;
            }
            
            .class-status {
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.8rem;
                font-weight: 600;
            }
            
            .status-needed {
                background: #ffebee;
                color: #c62828;
            }
            
            .status-filled {
                background: #e8f5e8;
                color: #2e7d32;
            }
            
            .class-details {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                font-size: 0.9rem;
            }
            
            .detail-item {
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
            }
            
            .detail-label {
                color: #666666;
                font-weight: 600;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .detail-value {
                color: #333333;
                font-weight: 500;
            }
        
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            color: #000000;
            padding: 2.5rem;
            border-radius: 1.5rem;
            border: 2px solid #e0e0e0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
            text-align: center;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #2196f3, #1976d2);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            border-color: #2196f3;
        }
            
            .danger {
                background-color: #ffebee;
                border-color: #f44336;
                color: #c62828;
            }
            
            .warning {
                background-color: #fff3e0;
                border-color: #ff9800;
                color: #ef6c00;
            }
            
            .success {
                background-color: #e8f5e8;
                border-color: #4caf50;
                color: #2e7d32;
            }
            
        .info-box {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            color: #000000;
            padding: 2rem;
            border-radius: 1rem;
            margin: 2rem 0;
            border-left: 6px solid #2196f3;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            border: 2px solid #e0e0e0;
            position: relative;
            transition: all 0.4s ease;
            overflow: hidden;
        }
        
        .info-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 6px;
            height: 100%;
            background: linear-gradient(180deg, #2196f3, #1976d2);
        }
        
        .info-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
            border-color: #2196f3;
        }
        
        .instrument-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            color: #000000;
            padding: 2.5rem;
            border-radius: 1.5rem;
            border: 2px solid #e0e0e0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 2rem;
            text-align: center;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .instrument-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #2196f3, #1976d2);
        }
        
        .instrument-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            border-color: #2196f3;
        }
        
        .instrument-card h3 {
            margin: 0 0 1rem 0;
            font-size: 1.5rem;
            font-weight: bold;
            color: #000000;
        }
        
        .instrument-card p {
            margin: 0.25rem 0;
            font-size: 1rem;
            color: #000000;
        }
            
            .instrument-card.danger {
                background-color: #ffebee;
                border-color: #f44336;
                color: #c62828;
            }
            
            .instrument-card.warning {
                background-color: #fff3e0;
                border-color: #ff9800;
                color: #ef6c00;
            }
            
            .instrument-card.success {
                background-color: #e8f5e8;
                border-color: #4caf50;
                color: #2e7d32;
            }
            
            .status-icon {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
            
            /* Light theme for Streamlit elements */
            .stSelectbox > div > div {
                background-color: #ffffff !important;
                color: #000000 !important;
            }
            
            .stTextInput > div > div > input {
                background-color: #ffffff !important;
                color: #000000 !important;
                border-color: #e0e0e0 !important;
            }
            
            /* Light theme for text input labels */
            .stTextInput label {
                color: #000000 !important;
                font-weight: bold !important;
                font-size: 1rem !important;
                margin-bottom: 0.5rem !important;
                display: block !important;
            }
            
            .stDataFrame {
                background-color: #ffffff !important;
                color: #000000 !important;
            }
            
                            /* Light theme for tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4 !important;
            color: #ffffff !important;
        }
        
        /* Make numbers in tabs and headers red */
        .stTabs [data-baseweb="tab"] {
            color: #000000 !important;
        }
        
        /* Custom class for red numbers */
        .red-number {
            color: #ff0000 !important;
            font-weight: bold !important;
        }
        

            
            /* Light theme for buttons */
            .stButton > button {
                background-color: #1f77b4 !important;
                color: #ffffff !important;
                border-color: #1f77b4 !important;
            }
            
            .stButton > button:hover {
                background-color: #1565c0 !important;
            }
            
                    /* Light theme for sidebar */
        .css-1d391kg {
            background-color: #ffffff !important;
        }
        
        /* Light theme for app background */
        .stApp {
            background-color: #ffffff !important;
        }
            
                    /* Light theme for main content */
        .main .block-container {
            background-color: #ffffff !important;
        }
        
        /* Light theme for text elements */
        .stMarkdown {
            color: #000000 !important;
        }
        
        /* Light theme for success/error messages */
        .stAlert {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        /* Faculty card styling for light theme */
        .faculty-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
            border: 2px solid #e0e0e0 !important;
            border-radius: 1rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        
        .faculty-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
            border-color: #2196f3 !important;
        }
        
        /* Light theme for success messages specifically */
        .stAlert[data-baseweb="notification"] {
            background-color: #e8f5e8 !important;
            color: #2e7d32 !important;
            border-color: #4caf50 !important;
        }
        
        /* Light theme for all success messages - more specific */
        .stAlert, .stAlert * {
            color: #2e7d32 !important;
        }
        
        /* Light theme for success message text specifically */
        .stAlert div, .stAlert span, .stAlert p {
            color: #2e7d32 !important;
        }
        
        /* Light theme for all text elements */
        .stText, .stMarkdown, .stSubheader, .stHeader, .stTitle {
            color: #000000 !important;
        }
        
        /* Light theme for all heading elements */
        h1, h2, h3, h4, h5, h6 {
            color: #000000 !important;
        }
        
        /* Light theme for Streamlit headings */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #000000 !important;
        }
        
        /* Light theme for sidebar text */
        .css-1d391kg .stMarkdown {
            color: #000000 !important;
        }
            
            /* Light theme for critical alert headers */
            .critical-alert-header {
                color: #d32f2f !important;
                font-weight: bold !important;
            }
            
            /* Light theme for critical alerts section */
            .critical-alerts-section {
                color: #000000 !important;
            }
            
            .critical-alerts-section h3 {
                color: #d32f2f !important;
            }
            
            .critical-alerts-section .stMarkdown {
                color: #000000 !important;
            }
            
            /* Light theme for success messages in critical alerts section */
            .critical-alerts-section .stAlert {
                background-color: #e8f5e8 !important;
                color: #2e7d32 !important;
                border-color: #4caf50 !important;
            }
            
            /* Light theme for success message text in critical alerts section - very specific */
            .critical-alerts-section .stAlert *,
            .critical-alerts-section .stAlert div,
            .critical-alerts-section .stAlert span,
            .critical-alerts-section .stAlert p {
                color: #2e7d32 !important;
                font-weight: bold !important;
            }
            
            /* Light theme for custom success message */
            .critical-alerts-section div[style*="background-color: #e8f5e8"] {
                background-color: #e8f5e8 !important;
                color: #2e7d32 !important;
                border-left-color: #4caf50 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Main content - Metrics in card style
    st.markdown("""
    <div style="margin: 2rem 0;">
        <div style="display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 2rem;">
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Total Ensembles</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin: 0.5rem 0;">""" + str(len(filtered_df)) + """</div>
            </div>
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Total Seats</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin: 0.5rem 0;">""" + str(int(filtered_df['secInstrumentation_seatscap'].sum())) + """</div>
            </div>
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Enrolled Students</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin: 0.5rem 0;">""" + str(int(filtered_df['secInstrumentation_activestucount'].sum())) + """</div>
            </div>
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Open Seats</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin: 0.5rem 0;">""" + str(int(filtered_df['open_seats'].sum())) + """</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Instrument status overview
    st.subheader("🎸 Instrument Status Overview")
    

    
    # Create instrument status summary
    instrument_summary = []
    for instrument in ['GUIT', 'PNO', 'BASS', 'DRUMS', 'VOICE']:
        needed = filtered_df[f'{instrument}_needed'].sum()
        enrolled = filtered_df[f'{instrument}_enrolled'].sum()
        filled = filtered_df[filtered_df[f'{instrument}_status'] == 'Filled'].shape[0]
        total_ensembles_with_instrument = filtered_df[filtered_df[f'{instrument}_needed'] > 0].shape[0]
        
        instrument_summary.append({
            'Instrument': instrument,
            'Needed': needed,
            'Enrolled': enrolled,
            'Filled Ensembles': filled,
            'Total Ensembles': total_ensembles_with_instrument,
            'Fill Rate': (filled / total_ensembles_with_instrument * 100) if total_ensembles_with_instrument > 0 else 0
        })
    
    instrument_df = pd.DataFrame(instrument_summary)
    
    # Prepare class data for each instrument
    instrument_classes_data = {}
    for instrument in ['GUIT', 'PNO', 'BASS', 'DRUMS', 'VOICE']:
        instrument_classes = []
        for _, ensemble in filtered_df.iterrows():
            if ensemble[f'{instrument}_needed'] > 0:
                section_name = ensemble['secInstrumentation_sectionname']
                course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
                faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
                days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
                time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
                enrolled_count = ensemble['secInstrumentation_activestucount']
                total_capacity = ensemble['secInstrumentation_seatscap']
                enrollment_rate = ensemble['enrollment_rate']
                style = ensemble['style']
                rating = ensemble['ratingOverall']
                
                instrument_classes.append({
                    'section_name': section_name,
                    'course_title': course_title,
                    'faculty': faculty,
                    'days': days,
                    'time': time,
                    'enrolled_count': enrolled_count,
                    'total_capacity': total_capacity,
                    'enrollment_rate': enrollment_rate,
                    'style': style,
                    'rating': rating,
                    'instrument': instrument,
                    'status': ensemble[f'{instrument}_status']
                })
        instrument_classes_data[instrument] = instrument_classes
    
    # Display instrument status with color coding and clickable functionality
    cols = st.columns(5)
    for i, (_, row) in enumerate(instrument_df.iterrows()):
        with cols[i]:
            if row['Fill Rate'] == 100:
                status_class = "success"
                status_icon = "✅"
            elif row['Fill Rate'] >= 50:
                status_class = "warning"
                status_icon = "⚠️"
            else:
                status_class = "danger"
                status_icon = "❌"
            
            instrument = row['Instrument']
            classes_data = instrument_classes_data.get(instrument, [])
            
            # Create a unique ID for this card
            card_id = f"card_{instrument.lower()}"
            
            # Map instrument codes to full names
            instrument_names = {
                'GUIT': 'Guitar',
                'PNO': 'Piano', 
                'BASS': 'Bass',
                'DRUMS': 'Drums',
                'VOICE': 'Voice'
            }
            instrument_name = instrument_names.get(instrument, instrument)
            
            # Use a button approach that works better with Streamlit
            if st.button(f"View {len(classes_data)} {instrument_name} Classes", key=f"btn_{instrument.lower()}"):
                st.session_state['selected_instrument'] = instrument
                st.session_state['show_modal'] = True
                st.session_state['modal_data'] = classes_data
            
            st.markdown(f"""
            <div class="instrument-card {status_class}">
                <div class="status-icon">{status_icon}</div>
                <h3>{row['Instrument']}</h3>
                <p><strong>Needed:</strong> {row['Needed']}</p>
                <p><strong>Enrolled:</strong> {row['Enrolled']}</p>
                <p><strong>Fill Rate:</strong> {row['Fill Rate']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Display modal if triggered
    if st.session_state.get('show_modal', False):
        instrument = st.session_state.get('selected_instrument', 'Unknown')
        classes_data = st.session_state.get('modal_data', [])
        
        st.markdown("---")
        st.markdown(f"### {instrument} - All Classes ({len(classes_data)} classes)")
        
        # Close button
        if st.button("❌ Close", key="close_modal"):
            st.session_state['show_modal'] = False
            st.rerun()
        
        if classes_data:
            # Display classes in a nice format
            for i, class_info in enumerate(classes_data):
                status_class = "status-needed" if class_info['status'] == 'Needed' else "status-filled"
                status_text = f"NEEDS {class_info['instrument']}" if class_info['status'] == 'Needed' else "FILLED"
                
                st.markdown(f"""
                <div class="class-item" style="margin-bottom: 1rem; padding: 1rem; border: 1px solid #ddd; border-radius: 0.5rem; background-color: #f9f9f9;">
                    <div class="class-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div class="class-name" style="font-weight: bold; font-size: 1.1rem;">{class_info['section_name']}</div>
                        <div class="class-status {status_class}" style="padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; font-weight: bold; background-color: {'#ff6b6b' if class_info['status'] == 'Needed' else '#51cf66'}; color: white;">{status_text}</div>
                    </div>
                    <div class="class-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.9rem;">
                        <div><strong>Course:</strong> {class_info['course_title']}</div>
                        <div><strong>Faculty:</strong> {class_info['faculty']}</div>
                        <div><strong>Schedule:</strong> {class_info['days']} at {class_info['time']}</div>
                        <div><strong>Enrollment:</strong> {class_info['enrolled_count']} / {class_info['total_capacity']} ({class_info['enrollment_rate']:.1f}%)</div>
                        <div><strong>Style:</strong> {class_info['style']}</div>
                        <div><strong>Rating:</strong> {class_info['rating']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No classes found for this instrument.")
        
        st.markdown("---")
    

    
    # Charts section
    st.subheader("📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enrollment rate distribution as pie chart
        # Create enrollment rate categories
        def categorize_enrollment_rate(rate):
            if rate == 0:
                return "0% (No Students)"
            elif rate <= 25:
                return "1-25% (Low)"
            elif rate <= 50:
                return "26-50% (Medium)"
            elif rate <= 75:
                return "51-75% (Good)"
            elif rate <= 99:
                return "76-99% (High)"
            else:
                return "100% (Full)"
        
        # Add enrollment category to dataframe
        filtered_df['enrollment_category'] = filtered_df['enrollment_rate'].apply(categorize_enrollment_rate)
        
        # Count classes in each category
        enrollment_counts = filtered_df['enrollment_category'].value_counts()
        
        # Create pie chart
        fig_enrollment = px.pie(
            values=enrollment_counts.values,
            names=enrollment_counts.index,
            title="Enrollment Rate Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Update layout for better appearance
        fig_enrollment.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        # Add percentage labels
        fig_enrollment.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12
        )
        
        st.plotly_chart(fig_enrollment, use_container_width=True)
    
    with col2:
        # Instrument needs chart
        fig_instruments = px.bar(
            instrument_df,
            x='Instrument',
            y=['Needed', 'Enrolled'],
            title="Instrument Needs vs Enrolled",
            barmode='group'
        )
        st.plotly_chart(fig_instruments, use_container_width=True)
    
    # Additional Analytics Charts
    st.subheader("📊 Additional Analytics")
    
    # Create two columns for additional charts
    col3, col4 = st.columns(2)
    
    with col3:
        # Ensemble Performance by Style
        style_performance = filtered_df.groupby('style').agg({
            'enrollment_rate': 'mean',
            'secInstrumentation_sectionname': 'count'
        }).reset_index()
        style_performance.columns = ['Style', 'Avg Enrollment Rate (%)', 'Number of Classes']
        
        fig_style = px.bar(
            style_performance,
            x='Style',
            y='Avg Enrollment Rate (%)',
            title="Average Enrollment Rate by Style",
            color='Avg Enrollment Rate (%)',
            color_continuous_scale='RdYlGn'
        )
        fig_style.update_layout(showlegend=False)
        st.plotly_chart(fig_style, use_container_width=True)
    
    with col4:
        # Time Slot Analysis
        def extract_time_slot(time_str):
            if isinstance(time_str, list) and len(time_str) > 0:
                time = time_str[0]
                if 'AM' in time:
                    return 'Morning'
                elif 'PM' in time:
                    if '12:' in time or '1:' in time or '2:' in time or '3:' in time:
                        return 'Afternoon'
                    else:
                        return 'Evening'
            return 'Unknown'
        
        filtered_df['time_slot'] = filtered_df['bSinCsmStartTime'].apply(extract_time_slot)
        time_analysis = filtered_df.groupby('time_slot').agg({
            'enrollment_rate': 'mean',
            'secInstrumentation_sectionname': 'count'
        }).reset_index()
        time_analysis.columns = ['Time Slot', 'Avg Enrollment Rate (%)', 'Number of Classes']
        
        fig_time = px.bar(
            time_analysis,
            x='Time Slot',
            y='Avg Enrollment Rate (%)',
            title="Average Enrollment Rate by Time Slot",
            color='Avg Enrollment Rate (%)',
            color_continuous_scale='Blues'
        )
        fig_time.update_layout(showlegend=False)
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Faculty Workload Analysis
    st.subheader("Faculty Workload Analysis")
    
    # Extract faculty names and analyze their workload
    faculty_data = []
    for _, ensemble in filtered_df.iterrows():
        if isinstance(ensemble['secInstrumentation_facnamepreffml'], list):
            for faculty in ensemble['secInstrumentation_facnamepreffml']:
                faculty_data.append({
                    'Faculty': faculty,
                    'Enrollment Rate': ensemble['enrollment_rate'],
                    'Class': ensemble['secInstrumentation_sectionname'],
                    'Style': ensemble['style']
                })
    
    if faculty_data:
        faculty_df = pd.DataFrame(faculty_data)
        faculty_summary = faculty_df.groupby('Faculty').agg({
            'Enrollment Rate': 'mean',
            'Class': 'count'
        }).reset_index()
        faculty_summary.columns = ['Faculty', 'Avg Enrollment Rate (%)', 'Number of Classes']
        
        # Create faculty workload chart
        fig_faculty = px.scatter(
            faculty_summary,
            x='Number of Classes',
            y='Avg Enrollment Rate (%)',
            size='Number of Classes',
            color='Avg Enrollment Rate (%)',
            hover_name='Faculty',
            title="Faculty Workload vs Performance",
            color_continuous_scale='RdYlGn',
            size_max=20
        )
        
        # Add trend line
        fig_faculty.add_trace(
            px.scatter(faculty_summary, x='Number of Classes', y='Avg Enrollment Rate (%)').data[0]
        )
        
        st.plotly_chart(fig_faculty, use_container_width=True)
        
        # Faculty details table
        st.markdown("**Faculty Performance Details:**")
        faculty_display = faculty_summary.sort_values('Avg Enrollment Rate (%)', ascending=False)
        st.dataframe(
            faculty_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No faculty data available for analysis.")
    
    # Ensemble details table
    st.subheader("📋 Ensemble Details")
    
    # Search functionality
    search_term = st.text_input("🔍 Search ensembles by name, faculty, or course title:", placeholder="Search", key="search_input")
    
    if search_term:
        search_filter = (
            filtered_df['secInstrumentation_sectionname'].str.contains(search_term, case=False, na=False) |
            filtered_df['secInstrumentation_facnamepreffml'].apply(lambda x: any(search_term.lower() in str(name).lower() for name in x) if isinstance(x, list) else False) |
            filtered_df['secInstrumentation_titlelongcrs'].apply(lambda x: any(search_term.lower() in str(title).lower() for title in x) if isinstance(x, list) else False)
        )
        display_df = filtered_df[search_filter]
    else:
        display_df = filtered_df
    
    # Create a more detailed display table
    if not display_df.empty:
        # Select columns for display
        display_columns = [
            'secInstrumentation_sectionname',
            'secInstrumentation_titlelongcrs',
            'secInstrumentation_facnamepreffml',
            'secInstrumentation_seatsavail',
            'secInstrumentation_activestucount',
            'secInstrumentation_seatscap',
            'enrollment_rate',
            'style',
            'ratingOverall',
            'bSinCsmDays',
            'bSinCsmStartTime',
            'bSinCsmEndTime'
        ]
        
        # Create display dataframe
        table_df = display_df[display_columns].copy()
        
        # Clean up the data for display
        table_df['Course Title'] = table_df['secInstrumentation_titlelongcrs'].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 'N/A'
        )
        table_df['Faculty'] = table_df['secInstrumentation_facnamepreffml'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else 'N/A'
        )
        table_df['Days'] = table_df['bSinCsmDays'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else 'N/A'
        )
        table_df['Time'] = table_df.apply(
            lambda row: f"{row['bSinCsmStartTime'][0] if isinstance(row['bSinCsmStartTime'], list) else 'N/A'} - {row['bSinCsmEndTime'][0] if isinstance(row['bSinCsmEndTime'], list) else 'N/A'}",
            axis=1
        )
        table_df['Enrollment Rate (%)'] = table_df['enrollment_rate'].round(1)
        
        # Final display columns
        final_columns = [
            'secInstrumentation_sectionname',
            'Course Title',
            'Faculty',
            'secInstrumentation_seatsavail',
            'secInstrumentation_activestucount',
            'secInstrumentation_seatscap',
            'Enrollment Rate (%)',
            'style',
            'ratingOverall',
            'Days',
            'Time'
        ]
        
        # Rename columns for better display
        column_mapping = {
            'secInstrumentation_sectionname': 'Section',
            'secInstrumentation_seatsavail': 'Available Seats',
            'secInstrumentation_activestucount': 'Enrolled',
            'secInstrumentation_seatscap': 'Capacity',
            'style': 'Style',
            'ratingOverall': 'Rating',
            'Days': 'Days',
            'Time': 'Time'
        }
        
        final_df = table_df[final_columns].rename(columns=column_mapping)
        
        # Display the table with styling
        st.dataframe(
            final_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = final_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Ensemble Data (CSV)",
            data=csv,
            file_name=f"ensemble_data_{selected_term}.csv",
            mime="text/csv",
            key="download_ensemble_data"
        )
    else:
        st.info("No ensembles found matching the search criteria.")
    
    # Specific Instrument Needs Section
    st.subheader("🎯 Classes Needing Specific Instruments")
    
    # Calculate counts for each instrument
    bass_count = len(filtered_df[filtered_df['BASS_needed'] > 0])
    piano_count = len(filtered_df[filtered_df['PNO_needed'] > 0])
    drums_count = len(filtered_df[filtered_df['DRUMS_needed'] > 0])
    
    # Create tabs for different instruments with counts
    tab1, tab2, tab3 = st.tabs([f"🎸 Bass Needed ({bass_count})", f"🎹 Piano Needed ({piano_count})", f"🥁 Drums Needed ({drums_count})"])
    
    with tab1:
        bass_needed = filtered_df[filtered_df['BASS_needed'] > 0].copy()
        if not bass_needed.empty:
            st.markdown(f"### Classes that need Bass players: <span style='color: #ff0000; font-weight: bold;'>{bass_count}</span>", unsafe_allow_html=True)
            
            # Search functionality for Bass classes
            bass_search = st.text_input("🔍 Search Bass classes by name, faculty, or course title:", placeholder="Search", key="bass_search")
            
            if bass_search:
                bass_filter = (
                    bass_needed['secInstrumentation_sectionname'].str.contains(bass_search, case=False, na=False) |
                    bass_needed['secInstrumentation_facnamepreffml'].apply(lambda x: any(bass_search.lower() in str(name).lower() for name in x) if isinstance(x, list) else False) |
                    bass_needed['secInstrumentation_titlelongcrs'].apply(lambda x: any(bass_search.lower() in str(title).lower() for title in x) if isinstance(x, list) else False)
                )
                bass_needed = bass_needed[bass_filter]
                if bass_needed.empty:
                    st.info("No Bass classes found matching the search criteria.")
                    return
            
            # Create dropdown options for bass needed classes
            bass_options = {}
            for _, ensemble in bass_needed.iterrows():
                section_name = ensemble['secInstrumentation_sectionname']
                course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
                faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
                days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
                time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
                bass_needed_count = ensemble['BASS_needed']
                
                display_name = f"🎸 {section_name} - Bass Players Needed: {bass_needed_count}"
                bass_options[display_name] = {
                    'section_name': section_name,
                    'course_title': course_title,
                    'faculty': faculty,
                    'days': days,
                    'time': time,
                    'bass_needed_count': bass_needed_count
                }
            
            # Create dropdown
            selected_bass_class = st.selectbox(
                "Select a class to view details:",
                options=list(bass_options.keys()),
                index=0 if bass_options else None,
                help="Choose a class to see detailed information",
                key="bass_class_selector"
            )
            
            # Display selected class details
            if selected_bass_class and selected_bass_class in bass_options:
                class_info = bass_options[selected_bass_class]
                st.markdown(f"""
                <div class="info-box danger" style="position: relative;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <strong>🎸 {class_info['section_name']}</strong><br>
                            <strong>Course:</strong> {class_info['course_title']}<br>
                            <strong>Faculty:</strong> {class_info['faculty']}<br>
                            <strong>Schedule:</strong> {class_info['days']} at {class_info['time']}<br>
                        </div>
                        <div style="background-color: #ff9800; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-left: 15px; white-space: nowrap;">
                            Bass Players Needed: {class_info['bass_needed_count']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No classes currently need Bass players!")
    
    with tab2:
        piano_needed = filtered_df[filtered_df['PNO_needed'] > 0].copy()
        if not piano_needed.empty:
            st.markdown(f"### Classes that need Piano players: <span style='color: #ff0000; font-weight: bold;'>{piano_count}</span>", unsafe_allow_html=True)
            
            # Search functionality for Piano classes
            piano_search = st.text_input("🔍 Search Piano classes by name, faculty, or course title:", placeholder="Search", key="piano_search")
            
            if piano_search:
                piano_filter = (
                    piano_needed['secInstrumentation_sectionname'].str.contains(piano_search, case=False, na=False) |
                    piano_needed['secInstrumentation_facnamepreffml'].apply(lambda x: any(piano_search.lower() in str(name).lower() for name in x) if isinstance(x, list) else False) |
                    piano_needed['secInstrumentation_titlelongcrs'].apply(lambda x: any(piano_search.lower() in str(title).lower() for title in x) if isinstance(x, list) else False)
                )
                piano_needed = piano_needed[piano_filter]
                if piano_needed.empty:
                    st.info("No Piano classes found matching the search criteria.")
                    return
            
            # Create dropdown options for piano needed classes
            piano_options = {}
            for _, ensemble in piano_needed.iterrows():
                section_name = ensemble['secInstrumentation_sectionname']
                course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
                faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
                days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
                time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
                piano_needed_count = ensemble['PNO_needed']
                
                display_name = f"🎹 {section_name} - Piano Players Needed: {piano_needed_count}"
                piano_options[display_name] = {
                    'section_name': section_name,
                    'course_title': course_title,
                    'faculty': faculty,
                    'days': days,
                    'time': time,
                    'piano_needed_count': piano_needed_count
                }
            
            # Create dropdown
            selected_piano_class = st.selectbox(
                "Select a class to view details:",
                options=list(piano_options.keys()),
                index=0 if piano_options else None,
                help="Choose a class to see detailed information",
                key="piano_class_selector"
            )
            
            # Display selected class details
            if selected_piano_class and selected_piano_class in piano_options:
                class_info = piano_options[selected_piano_class]
                st.markdown(f"""
                <div class="info-box warning" style="position: relative;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <strong>🎹 {class_info['section_name']}</strong><br>
                            <strong>Course:</strong> {class_info['course_title']}<br>
                            <strong>Faculty:</strong> {class_info['faculty']}<br>
                            <strong>Schedule:</strong> {class_info['days']} at {class_info['time']}<br>
                        </div>
                        <div style="background-color: #ff9800; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-left: 15px; white-space: nowrap;">
                            Piano Players Needed: {class_info['piano_needed_count']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No classes currently need Piano players!")
    
    with tab3:
        drums_needed = filtered_df[filtered_df['DRUMS_needed'] > 0].copy()
        if not drums_needed.empty:
            st.markdown(f"### Classes that need Drummers: <span style='color: #ff0000; font-weight: bold;'>{drums_count}</span>", unsafe_allow_html=True)
            
            # Search functionality for Drums classes
            drums_search = st.text_input("🔍 Search Drums classes by name, faculty, or course title:", placeholder="Search", key="drums_search")
            
            if drums_search:
                drums_filter = (
                    drums_needed['secInstrumentation_sectionname'].str.contains(drums_search, case=False, na=False) |
                    drums_needed['secInstrumentation_facnamepreffml'].apply(lambda x: any(drums_search.lower() in str(name).lower() for name in x) if isinstance(x, list) else False) |
                    drums_needed['secInstrumentation_titlelongcrs'].apply(lambda x: any(drums_search.lower() in str(title).lower() for title in x) if isinstance(x, list) else False)
                )
                drums_needed = drums_needed[drums_filter]
                if drums_needed.empty:
                    st.info("No Drums classes found matching the search criteria.")
                    return
            
            # Create dropdown options for drums needed classes
            drums_options = {}
            for _, ensemble in drums_needed.iterrows():
                section_name = ensemble['secInstrumentation_sectionname']
                course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
                faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
                days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
                time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
                drums_needed_count = ensemble['DRUMS_needed']
                
                display_name = f"🥁 {section_name} - Drummers Needed: {drums_needed_count}"
                drums_options[display_name] = {
                    'section_name': section_name,
                    'course_title': course_title,
                    'faculty': faculty,
                    'days': days,
                    'time': time,
                    'drums_needed_count': drums_needed_count
                }
            
            # Create dropdown
            selected_drums_class = st.selectbox(
                "Select a class to view details:",
                options=list(drums_options.keys()),
                index=0 if drums_options else None,
                help="Choose a class to see detailed information",
                key="drums_class_selector"
            )
            
            # Display selected class details
            if selected_drums_class and selected_drums_class in drums_options:
                class_info = drums_options[selected_drums_class]
                st.markdown(f"""
                <div class="info-box danger" style="position: relative;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <strong>🥁 {class_info['section_name']}</strong><br>
                            <strong>Course:</strong> {class_info['course_title']}<br>
                            <strong>Faculty:</strong> {class_info['faculty']}<br>
                            <strong>Schedule:</strong> {class_info['days']} at {class_info['time']}<br>
                        </div>
                        <div style="background-color: #ff9800; color: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; margin-left: 15px; white-space: nowrap;">
                            Drummers Needed: {class_info['drums_needed_count']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No classes currently need Drummers!")
    
    # Classes with less than 4 students - Potential Drop Alert
    low_enrollment_classes = filtered_df[filtered_df['secInstrumentation_activestucount'] < 4].copy()
    
    if not low_enrollment_classes.empty:
        st.subheader(f"⚠️ Classes with Less Than 4 Students - Potentially Will Be Dropped ({len(low_enrollment_classes)})")
        
        # Search functionality for low enrollment classes
        low_enrollment_search = st.text_input("🔍 Search low enrollment classes by name, faculty, or course title:", placeholder="Search", key="low_enrollment_search")
        
        if low_enrollment_search:
            low_enrollment_filter = (
                low_enrollment_classes['secInstrumentation_sectionname'].str.contains(low_enrollment_search, case=False, na=False) |
                low_enrollment_classes['secInstrumentation_facnamepreffml'].apply(lambda x: any(low_enrollment_search.lower() in str(name).lower() for name in x) if isinstance(x, list) else False) |
                low_enrollment_classes['secInstrumentation_titlelongcrs'].apply(lambda x: any(low_enrollment_search.lower() in str(title).lower() for title in x) if isinstance(x, list) else False)
            )
            low_enrollment_classes = low_enrollment_classes[low_enrollment_filter]
            if low_enrollment_classes.empty:
                st.info("No low enrollment classes found matching the search criteria.")
                return
        
        # Create dropdown options for low enrollment classes
        low_enrollment_options = {}
        for _, ensemble in low_enrollment_classes.iterrows():
            section_name = ensemble['secInstrumentation_sectionname']
            course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
            faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
            days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
            time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
            enrolled_count = ensemble['secInstrumentation_activestucount']
            total_capacity = ensemble['secInstrumentation_seatscap']
            enrollment_rate = ensemble['enrollment_rate']
            
            # Determine severity level
            if enrolled_count == 0:
                severity = "danger"
                icon = "🚨"
                status = "CRITICAL - NO STUDENTS"
            elif enrolled_count == 1:
                severity = "danger"
                icon = "🚨"
                status = "CRITICAL - ONLY 1 STUDENT"
            elif enrolled_count == 2:
                severity = "warning"
                icon = "⚠️"
                status = "WARNING - ONLY 2 STUDENTS"
            else:  # enrolled_count == 3
                severity = "warning"
                icon = "⚠️"
                status = "WARNING - ONLY 3 STUDENTS"
            
            display_name = f"{icon} {section_name} - {enrolled_count} Students ({enrollment_rate:.1f}%)"
            low_enrollment_options[display_name] = {
                'section_name': section_name,
                'course_title': course_title,
                'faculty': faculty,
                'days': days,
                'time': time,
                'enrolled_count': enrolled_count,
                'total_capacity': total_capacity,
                'enrollment_rate': enrollment_rate,
                'severity': severity,
                'icon': icon,
                'status': status
            }
        
        # Create dropdown
        selected_low_enrollment_class = st.selectbox(
            "Select a low enrollment class to view details:",
            options=list(low_enrollment_options.keys()),
            index=0 if low_enrollment_options else None,
            help="Choose a class to see detailed information about low enrollment",
            key="low_enrollment_selector"
        )
        
        # Display selected class details
        if selected_low_enrollment_class and selected_low_enrollment_class in low_enrollment_options:
            class_info = low_enrollment_options[selected_low_enrollment_class]
            st.markdown(f"""
            <div class="info-box {class_info['severity']}" style="border-left: 6px solid #f44336; background-color: #ffebee; position: relative;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{class_info['icon']}</span>
                    <strong style="color: #000000; font-size: 1.2rem;">{class_info['status']}</strong>
                </div>
                <strong style="color: #000000;">{class_info['section_name']}</strong><br>
                <strong style="color: #000000;">Course:</strong> {class_info['course_title']}<br>
                <strong style="color: #000000;">Faculty:</strong> {class_info['faculty']}<br>
                <strong style="color: #000000;">Schedule:</strong> {class_info['days']} at {class_info['time']}<br>
                <div style="text-align: center; margin: 1rem 0;">
                    <h2 style="color: #000000; margin: 0; font-size: 1.5rem; font-weight: bold;">Enrollment: {class_info['enrolled_count']} / {class_info['total_capacity']} students ({class_info['enrollment_rate']:.1f}%)</h2>
                </div>
                <div style="position: absolute; top: 10px; right: 10px; background-color: #d32f2f; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 0.9rem;">
                    ⚠️ POTENTIALLY WILL BE DROPPED
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Summary statistics
        total_low_enrollment = len(low_enrollment_classes)
        zero_students = len(low_enrollment_classes[low_enrollment_classes['secInstrumentation_activestucount'] == 0])
        one_student = len(low_enrollment_classes[low_enrollment_classes['secInstrumentation_activestucount'] == 1])
        two_students = len(low_enrollment_classes[low_enrollment_classes['secInstrumentation_activestucount'] == 2])
        three_students = len(low_enrollment_classes[low_enrollment_classes['secInstrumentation_activestucount'] == 3])
        
        st.markdown(f"""
        <div class="metric-card" style="background-color: #fff3e0; border-color: #ff9800; margin-top: 1rem;">
            <h3 style="color: #ef6c00; margin-bottom: 1rem;">📊 Low Enrollment Summary</h3>
            <p><strong>Total Classes at Risk:</strong> {total_low_enrollment}</p>
            <p><strong>Classes with 0 Students:</strong> {zero_students}</p>
            <p><strong>Classes with 1 Student:</strong> {one_student}</p>
            <p><strong>Classes with 2 Students:</strong> {two_students}</p>
            <p><strong>Classes with 3 Students:</strong> {three_students}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button for low enrollment classes
        st.markdown("---")
        st.subheader("📥 Download Low Enrollment Data")
        
        # Prepare data for download
        download_data = []
        for _, ensemble in low_enrollment_classes.iterrows():
            section_name = ensemble['secInstrumentation_sectionname']
            course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
            faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
            days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
            time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
            enrolled_count = ensemble['secInstrumentation_activestucount']
            total_capacity = ensemble['secInstrumentation_seatscap']
            enrollment_rate = ensemble['enrollment_rate']
            
            # Determine status
            if enrolled_count == 0:
                status = "CRITICAL - NO STUDENTS"
            elif enrolled_count == 1:
                status = "CRITICAL - ONLY 1 STUDENT"
            elif enrolled_count == 2:
                status = "WARNING - ONLY 2 STUDENTS"
            else:  # enrolled_count == 3
                status = "WARNING - ONLY 3 STUDENTS"
            
            download_data.append({
                'Section': section_name,
                'Course_Title': course_title,
                'Faculty': faculty,
                'Schedule_Days': days,
                'Schedule_Time': time,
                'Enrolled_Students': enrolled_count,
                'Total_Capacity': total_capacity,
                'Enrollment_Rate_Percent': round(enrollment_rate, 1),
                'Status': status,
                'Risk_Level': 'POTENTIALLY WILL BE DROPPED'
            })
        
        # Create DataFrame for download
        download_df = pd.DataFrame(download_data)
        
        # Download button
        csv = download_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Low Enrollment Classes (CSV)",
            data=csv,
            file_name=f"low_enrollment_classes_{selected_term}.csv",
            mime="text/csv",
            help="Download all classes with less than 4 students as a CSV file",
            key="download_low_enrollment"
        )
        
    else:
        st.success("✅ No classes with less than 4 students enrolled!")
    
    # Performance Classes Section - Faculty Cannot be Scheduled for Rating Auditions
    performance_classes = identify_performance_classes(filtered_df)
    
    if performance_classes:
        st.subheader(f"PERFORMANCE CLASSES - Faculty Cannot be Scheduled for Rating Auditions ({len(performance_classes)})")
        
        # Search functionality for performance classes
        performance_search = st.text_input("🔍 Search performance classes by name, faculty, or course title:", placeholder="Search", key="performance_search")
        
        if performance_search:
            performance_classes = [
                pc for pc in performance_classes
                if (performance_search.lower() in pc['section_name'].lower() or
                    performance_search.lower() in pc['course_title'].lower() or
                    performance_search.lower() in pc['faculty'].lower())
            ]
            if not performance_classes:
                st.info("No performance classes found matching the search criteria.")
                return
        
        # Create dropdown options for performance classes
        performance_options = {}
        for pc in performance_classes:
            display_name = f"{pc['section_name']} - {pc['faculty']} ({pc['enrollment_rate']:.1f}%)"
            performance_options[display_name] = pc
        
        # Create dropdown
        selected_performance_class = st.selectbox(
            "Select a performance class to view details:",
            options=list(performance_options.keys()),
            index=0 if performance_options else None,
            help="Choose a performance class to see detailed information",
            key="performance_selector"
        )
        
        # Display selected performance class details
        if selected_performance_class and selected_performance_class in performance_options:
            pc_info = performance_options[selected_performance_class]
            st.markdown(f"""
            <div class="info-box warning" style="border-left: 6px solid #ff9800; background-color: #fff3e0; position: relative;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;"></span>
                    <strong style="color: #000000; font-size: 1.2rem;">PERFORMANCE CLASS</strong>
                </div>
                <strong style="color: #000000;">{pc_info['section_name']}</strong><br>
                <strong style="color: #000000;">Course:</strong> {pc_info['course_title']}<br>
                <strong style="color: #000000;">Faculty:</strong> {pc_info['faculty']}<br>
                <strong style="color: #000000;">Schedule:</strong> {pc_info['days']} at {pc_info['time']}<br>
                <div style="text-align: center; margin: 1rem 0;">
                    <h2 style="color: #000000; margin: 0; font-size: 1.5rem; font-weight: bold;">Enrollment: {pc_info['enrolled_count']} / {pc_info['total_capacity']} students ({pc_info['enrollment_rate']:.1f}%)</h2>
                </div>
                <strong style="color: #000000;">Style:</strong> {pc_info['style']}<br>
                <strong style="color: #000000;">Rating:</strong> {pc_info['rating']}<br>
                <div style="position: absolute; top: 10px; right: 10px; background-color: #ff9800; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 0.9rem;">
                    ⚠️ NO RATING AUDITIONS
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display the specific reason
            st.markdown(f"""
            <div class="metric-card" style="background-color: #fff3e0; border-color: #ff9800; margin-top: 1rem;">
                <h3 style="color: #ef6c00; margin-bottom: 1rem;">📋 Performance Class Details</h3>
                <p><strong>Reason:</strong> {pc_info['performance_reason']}</p>
                <p><strong>Faculty Scheduling:</strong> Cannot be scheduled for rating auditions</p>
                <p><strong>Class Type:</strong> Performance/Ensemble Class</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Summary statistics
        enmx_100_count = len([pc for pc in performance_classes if 'ENMX-100' in pc['section_name']])
        faculty_pisj_count = len([pc for pc in performance_classes if 'PISJ' in pc['faculty']])
        faculty_ends_count = len([pc for pc in performance_classes if 'ENDS' in pc['faculty']])
        other_performance_count = len([pc for pc in performance_classes if 'ENMX-100' not in pc['section_name'] and 'PISJ' not in pc['faculty'] and 'ENDS' not in pc['faculty']])
        
        st.markdown(f"""
        <div class="metric-card" style="background-color: #fff3e0; border-color: #ff9800; margin-top: 1rem;">
            <h3 style="color: #ef6c00; margin-bottom: 1rem;">📊 Performance Classes Summary</h3>
            <p><strong>Total Performance Classes:</strong> {len(performance_classes)}</p>
            <p><strong>ENMX-100 Classes:</strong> {enmx_100_count}</p>
            <p><strong>Faculty PISJ Classes:</strong> {faculty_pisj_count}</p>
            <p><strong>Faculty ENDS Classes:</strong> {faculty_ends_count}</p>
            <p><strong>Other Performance Classes:</strong> {other_performance_count}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button for performance classes
        st.markdown("---")
        st.subheader("📥 Download Performance Classes Data")
        
        # Prepare data for download
        performance_download_data = []
        for pc in performance_classes:
            performance_download_data.append({
                'Section': pc['section_name'],
                'Course_Title': pc['course_title'],
                'Faculty': pc['faculty'],
                'Schedule_Days': pc['days'],
                'Schedule_Time': pc['time'],
                'Enrolled_Students': pc['enrolled_count'],
                'Total_Capacity': pc['total_capacity'],
                'Enrollment_Rate_Percent': round(pc['enrollment_rate'], 1),
                'Style': pc['style'],
                'Rating': pc['rating'],
                'Performance_Reason': pc['performance_reason'],
                'Scheduling_Note': 'Cannot be scheduled for rating auditions'
            })
        
        # Create DataFrame for download
        performance_download_df = pd.DataFrame(performance_download_data)
        
        # Download button
        csv = performance_download_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Performance Classes (CSV)",
            data=csv,
            file_name=f"performance_classes_{selected_term}.csv",
            mime="text/csv",
            help="Download all performance classes as a CSV file",
            key="download_performance_classes"
        )
        
    else:
        st.success("✅ No performance classes found!")
    
    # Registration Preferences Section - Staff Placement Priority
    st.markdown("---")
    st.subheader("🎯 Registration Preferences - Staff Placement Priority")
    
    # Analyze registration preferences
    registration_data = analyze_registration_preferences(filtered_df)
    
    if registration_data:
        # Search functionality for registration preferences
        registration_search = st.text_input("🔍 Search registration preferences by class name, faculty, or course title:", placeholder="Search", key="registration_search")
        
        if registration_search:
            registration_data = [
                rd for rd in registration_data
                if (registration_search.lower() in rd['section_name'].lower() or
                    registration_search.lower() in rd['course_title'].lower() or
                    registration_search.lower() in rd['faculty'].lower())
            ]
            if not registration_data:
                st.info("No classes found matching the search criteria.")
                return
        
        # Filter by priority level
        priority_filter = st.selectbox(
            "Filter by Priority Level:",
            ["All Priorities", "HIGHEST - 3 Students", "HIGH - 2 Students", "MEDIUM - 1 Student", "LOW - 0 Students"],
            key="priority_filter"
        )
        
        if priority_filter != "All Priorities":
            registration_data = [rd for rd in registration_data if rd['priority_level'] == priority_filter]
        
        # Filter by contract type
        contract_filter = st.selectbox(
            "Filter by Faculty Contract Type:",
            ["All Contracts", "FT", "PT3yr", "PT_special", "adjunct", "Unknown"],
            key="registration_contract_filter"
        )
        
        if contract_filter != "All Contracts":
            registration_data = [rd for rd in registration_data if rd['contract_type'] == contract_filter]
        
        # Display registration preferences in priority order
        st.markdown("### 📋 Priority Placement List (Sorted by Registration Preference)")
        
        # Create tabs for different priority levels
        highest_priority = [rd for rd in registration_data if rd['priority_level'] == "HIGHEST - 3 Students"]
        high_priority = [rd for rd in registration_data if rd['priority_level'] == "HIGH - 2 Students"]
        medium_priority = [rd for rd in registration_data if rd['priority_level'] == "MEDIUM - 1 Student"]
        low_priority = [rd for rd in registration_data if rd['priority_level'] == "LOW - 0 Students"]
        
        tab1, tab2, tab3, tab4 = st.tabs([
            f"HIGHEST Priority ({len(highest_priority)})",
            f"HIGH Priority ({len(high_priority)})", 
            f"MEDIUM Priority ({len(medium_priority)})",
            f"LOW Priority ({len(low_priority)})"
        ])
        
        with tab1:
            if highest_priority:
                for rd in highest_priority:
                    contract_color = get_contract_color(rd['contract_type'])
                    st.markdown(f"""
                    <div class="info-box" style="border-left: 6px solid {contract_color}; background-color: #f8f9fa; margin-bottom: 1rem; padding: 1rem; border-radius: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong style="color: #000000; font-size: 1.1rem;">{rd['section_name']}</strong>
                            <span style="background-color: {contract_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; font-weight: bold;">
                                {rd['contract_type']}
                            </span>
                        </div>
                        <div style="color: #000000;">
                            <strong>Course:</strong> {rd['course_title']}<br>
                            <strong>Faculty:</strong> {rd['faculty']}<br>
                            <strong>Schedule:</strong> {rd['days']} at {rd['time']}<br>
                            <div style="text-align: center; margin: 1rem 0;">
                                <h2 style="color: #000000; margin: 0; font-size: 1.5rem; font-weight: bold;">Enrollment: {rd['enrolled_count']} / {rd['total_capacity']} students ({rd['enrollment_rate']:.1f}%)</h2>
                            </div>
                            <strong>Style:</strong> {rd['style']}<br>
                            <strong>Rating:</strong> {rd['rating']}<br>
                            <strong>Instruments Needed:</strong> {rd['instruments_needed']}<br>
                            <strong>Priority Score:</strong> {rd['priority_score']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No classes in HIGHEST priority category.")
        
        with tab2:
            if high_priority:
                for rd in high_priority:
                    contract_color = get_contract_color(rd['contract_type'])
                    st.markdown(f"""
                    <div class="info-box" style="border-left: 6px solid {contract_color}; background-color: #f8f9fa; margin-bottom: 1rem; padding: 1rem; border-radius: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong style="color: #000000; font-size: 1.1rem;">{rd['section_name']}</strong>
                            <span style="background-color: {contract_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; font-weight: bold;">
                                {rd['contract_type']}
                            </span>
                        </div>
                        <div style="color: #000000;">
                            <strong>Course:</strong> {rd['course_title']}<br>
                            <strong>Faculty:</strong> {rd['faculty']}<br>
                            <strong>Schedule:</strong> {rd['days']} at {rd['time']}<br>
                            <div style="text-align: center; margin: 1rem 0;">
                                <h2 style="color: #000000; margin: 0; font-size: 1.5rem; font-weight: bold;">Enrollment: {rd['enrolled_count']} / {rd['total_capacity']} students ({rd['enrollment_rate']:.1f}%)</h2>
                            </div>
                            <strong>Style:</strong> {rd['style']}<br>
                            <strong>Rating:</strong> {rd['rating']}<br>
                            <strong>Instruments Needed:</strong> {rd['instruments_needed']}<br>
                            <strong>Priority Score:</strong> {rd['priority_score']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No classes in HIGH priority category.")
        
        with tab3:
            if medium_priority:
                for rd in medium_priority:
                    contract_color = get_contract_color(rd['contract_type'])
                    st.markdown(f"""
                    <div class="info-box" style="border-left: 6px solid {contract_color}; background-color: #f8f9fa; margin-bottom: 1rem; padding: 1rem; border-radius: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong style="color: #000000; font-size: 1.1rem;">{rd['section_name']}</strong>
                            <span style="background-color: {contract_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; font-weight: bold;">
                                {rd['contract_type']}
                            </span>
                        </div>
                        <div style="color: #000000;">
                            <strong>Course:</strong> {rd['course_title']}<br>
                            <strong>Faculty:</strong> {rd['faculty']}<br>
                            <strong>Schedule:</strong> {rd['days']} at {rd['time']}<br>
                            <div style="text-align: center; margin: 1rem 0;">
                                <h2 style="color: #000000; margin: 0; font-size: 1.5rem; font-weight: bold;">Enrollment: {rd['enrolled_count']} / {rd['total_capacity']} students ({rd['enrollment_rate']:.1f}%)</h2>
                            </div>
                            <strong>Style:</strong> {rd['style']}<br>
                            <strong>Rating:</strong> {rd['rating']}<br>
                            <strong>Instruments Needed:</strong> {rd['instruments_needed']}<br>
                            <strong>Priority Score:</strong> {rd['priority_score']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No classes in MEDIUM priority category.")
        
        with tab4:
            if low_priority:
                for rd in low_priority:
                    contract_color = get_contract_color(rd['contract_type'])
                    st.markdown(f"""
                    <div class="info-box" style="border-left: 6px solid {contract_color}; background-color: #f8f9fa; margin-bottom: 1rem; padding: 1rem; border-radius: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong style="color: #000000; font-size: 1.1rem;">{rd['section_name']}</strong>
                            <span style="background-color: {contract_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; font-weight: bold;">
                                {rd['contract_type']}
                            </span>
                        </div>
                        <div style="color: #000000;">
                            <strong>Course:</strong> {rd['course_title']}<br>
                            <strong>Faculty:</strong> {rd['faculty']}<br>
                            <strong>Schedule:</strong> {rd['days']} at {rd['time']}<br>
                            <div style="text-align: center; margin: 1rem 0;">
                                <h2 style="color: #000000; margin: 0; font-size: 1.5rem; font-weight: bold;">Enrollment: {rd['enrolled_count']} / {rd['total_capacity']} students ({rd['enrollment_rate']:.1f}%)</h2>
                            </div>
                            <strong>Style:</strong> {rd['style']}<br>
                            <strong>Rating:</strong> {rd['rating']}<br>
                            <strong>Instruments Needed:</strong> {rd['instruments_needed']}<br>
                            <strong>Priority Score:</strong> {rd['priority_score']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No classes in LOW priority category.")
        
        # Summary statistics
        ft_count = len([rd for rd in registration_data if rd['contract_type'] == 'FT'])
        pt3yr_count = len([rd for rd in registration_data if rd['contract_type'] == 'PT3yr'])
        pt_special_count = len([rd for rd in registration_data if rd['contract_type'] == 'PT_special'])
        adjunct_count = len([rd for rd in registration_data if rd['contract_type'] == 'adjunct'])
        unknown_count = len([rd for rd in registration_data if rd['contract_type'] == 'Unknown'])
        
        st.markdown(f"""
        <div class="metric-card" style="background-color: #f0f8ff; border-color: #2196f3; margin-top: 1rem;">
            <h3 style="color: #1976d2; margin-bottom: 1rem;">📊 Registration Preferences Summary</h3>
            <p><strong>Total Classes Analyzed:</strong> {len(registration_data)}</p>
            <p><strong>Full Time Faculty Classes:</strong> <span style="color: #ff0000; font-weight: bold;">{ft_count}</span></p>
            <p><strong>Part Time 3-Year Contract Classes:</strong> <span style="color: #0000ff; font-weight: bold;">{pt3yr_count}</span></p>
            <p><strong>Part Time Special Circumstances Classes:</strong> <span style="color: #ffa500; font-weight: bold;">{pt_special_count}</span></p>
            <p><strong>Adjunct Faculty Classes:</strong> <span style="color: #8b4513; font-weight: bold;">{adjunct_count}</span></p>
            <p><strong>Unknown Contract Type:</strong> <span style="color: #808080; font-weight: bold;">{unknown_count}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download button for registration preferences
        st.markdown("---")
        st.subheader("📥 Download Registration Preferences Data")
        
        # Prepare data for download
        registration_download_data = []
        for rd in registration_data:
            registration_download_data.append({
                'Section': rd['section_name'],
                'Course_Title': rd['course_title'],
                'Faculty': rd['faculty'],
                'Contract_Type': rd['contract_type'],
                'Enrolled_Students': rd['enrolled_count'],
                'Total_Capacity': rd['total_capacity'],
                'Enrollment_Rate_Percent': round(rd['enrollment_rate'], 1),
                'Priority_Level': rd['priority_level'],
                'Priority_Score': rd['priority_score'],
                'Schedule_Days': rd['days'],
                'Schedule_Time': rd['time'],
                'Style': rd['style'],
                'Rating': rd['rating'],
                'Instruments_Needed': rd['instruments_needed']
            })
        
        # Create DataFrame for download
        registration_download_df = pd.DataFrame(registration_download_data)
        
        # Download button
        csv = registration_download_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Registration Preferences (CSV)",
            data=csv,
            file_name=f"registration_preferences_{selected_term}.csv",
            mime="text/csv",
            help="Download all registration preferences data as a CSV file",
            key="download_registration_preferences"
        )
        
    else:
        st.info("No registration data available for analysis.")
    
    # Critical alerts section
    st.markdown('<div class="critical-alerts-section">', unsafe_allow_html=True)
    st.subheader("🚨 Other Critical Alerts")
    
    # Find ensembles with other critical issues
    critical_ensembles = filtered_df[
        (filtered_df['enrollment_rate'] < 25) & (filtered_df['secInstrumentation_activestucount'] >= 4) |  # Low enrollment but 4+ students
        (filtered_df['secInstrumentation_seatsavail'] == 0)  # No available seats
    ]
    
    if not critical_ensembles.empty:
        for _, ensemble in critical_ensembles.iterrows():
            section_name = ensemble['secInstrumentation_sectionname']
            enrollment_rate = ensemble['enrollment_rate']
            available_seats = ensemble['secInstrumentation_seatsavail']
            
            if enrollment_rate < 25 and ensemble['secInstrumentation_activestucount'] >= 4:
                st.markdown(f"""
                <div class="info-box warning">
                    <strong>⚠️ Low Enrollment Alert:</strong> {section_name} has only {enrollment_rate:.1f}% enrollment rate (but has 4+ students).
                </div>
                """, unsafe_allow_html=True)
            
            if available_seats == 0:
                st.markdown(f"""
                <div class="info-box warning">
                    <strong>🔒 Full Capacity:</strong> {section_name} has no available seats.
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: #e8f5e8; color: #2e7d32; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #4caf50; margin: 1rem 0; font-weight: bold;">
            ✅ No other critical alerts at this time.
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 