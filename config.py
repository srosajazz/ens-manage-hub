"""
Configuration file for Ensemble Management Dashboard
Centralized settings for institutional deployment
"""

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'page_title': 'Ensemble Management Dashboard',
    'page_icon': '🎵',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Institutional Branding
INSTITUTION_CONFIG = {
    'name': 'Music Department',
    'logo_url': None,  # Add your institution logo URL
    'primary_color': '#1f77b4',
    'secondary_color': '#ff7f0e',
    'accent_color': '#2ca02c'
}

# Color Scheme for Professional Use
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#ff9800',
    'danger': '#f44336',
    'info': '#2196f3',
    'light_gray': '#f8f9fa',
    'dark_gray': '#343a40',
    'white': '#ffffff',
    'black': '#000000'
}

# Status Colors
STATUS_COLORS = {
    'critical': '#d32f2f',
    'warning': '#f57c00',
    'success': '#388e3c',
    'info': '#1976d2'
}

# CSS Styles for Professional Appearance
CSS_STYLES = """
<style>
    /* Professional Header */
    .main-header {
        font-size: 3.5rem;
        color: #000000;
        text-align: center;
        margin: 3rem 0 4rem 0;
        font-weight: bold;
        padding: 2rem 0;
        border-bottom: 3px solid #1f77b4;
        border-top: 3px solid #1f77b4;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(31, 119, 180, 0.1);
    }
    
    /* Professional Metric Cards */
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 2px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Status Classes */
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
    
    .info {
        background-color: #e3f2fd;
        border-color: #2196f3;
        color: #1565c0;
    }
    
    /* Professional Info Boxes */
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Instrument Cards */
    .instrument-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 2px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
        text-align: center;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: transform 0.2s ease-in-out;
    }
    
    .instrument-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .instrument-card h3 {
        margin: 0 0 1rem 0;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .instrument-card p {
        margin: 0.25rem 0;
        font-size: 1rem;
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
    
    /* Professional Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Professional Tables */
    .dataframe {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-collapse: collapse;
        width: 100%;
    }
    
    .dataframe th {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 12px;
        text-align: left;
    }
    
    .dataframe td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    .dataframe tr:hover {
        background-color: #ddd;
    }
    
    /* Professional Buttons */
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
    }
    
    /* Professional Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
"""

# Data Processing Configuration
DATA_CONFIG = {
    'instruments': ['GUIT', 'PNO', 'BASS', 'DRUMS', 'VOICE'],
    'low_enrollment_threshold': 4,
    'critical_enrollment_rate': 25,
    'date_format': '%Y-%m-%d',
    'time_format': '%I:%M:%S %p'
}

# Export Configuration
EXPORT_CONFIG = {
    'csv_encoding': 'utf-8',
    'include_timestamp': True,
    'file_prefix': 'ensemble_dashboard'
}

# Alert Configuration
ALERT_CONFIG = {
    'low_enrollment_threshold': 4,
    'critical_enrollment_rate': 25,
    'full_capacity_threshold': 0
} 