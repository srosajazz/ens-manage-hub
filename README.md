# 🎵 Ensemble Management Dashboard

A comprehensive, professional-grade dashboard for managing music ensemble enrollment and instrument assignments. Built with Streamlit and designed for institutional use.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Data Structure](#data-structure)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Ensemble Management Dashboard is a sophisticated web application designed to help music departments and institutions manage ensemble enrollment, track instrument assignments, and identify classes at risk of cancellation. The dashboard provides real-time insights into enrollment patterns, instrument needs, and critical alerts for administrative decision-making.

### Key Benefits

- **Real-time Monitoring**: Track enrollment status across all ensembles
- **Critical Alerts**: Identify classes at risk of cancellation
- **Instrument Management**: Monitor instrument assignments and needs
- **Data Export**: Generate reports for administrative use
- **Professional Interface**: Clean, institutional-grade design
- **Responsive Design**: Works on desktop and mobile devices

## ✨ Features

### 📊 **Dashboard Overview**
- **Key Metrics**: Total ensembles, seats, enrolled students, and open seats
- **Real-time Updates**: Live data refresh and calculations
- **Visual Indicators**: Color-coded status cards and alerts

### 🎸 **Instrument Management**
- **Status Overview**: Visual cards showing instrument fill rates
- **Specific Needs**: Filter classes needing specific instruments (Bass, Piano, Drums, Voice)
- **Assignment Tracking**: Monitor enrolled vs. needed instruments

### ⚠️ **Critical Alerts**
- **Low Enrollment Detection**: Classes with less than 4 students
- **Risk Assessment**: Color-coded severity levels
- **Actionable Insights**: Detailed information for decision-making

### 📈 **Analytics & Reporting**
- **Enrollment Distribution**: Histogram of enrollment rates
- **Instrument Analysis**: Bar charts comparing needs vs. enrollment
- **Trend Analysis**: Enrollment patterns by ensemble style
- **Capacity Utilization**: Distribution of seat utilization

### 🔍 **Advanced Filtering**
- **Term Selection**: Filter by academic term
- **Style Filtering**: Filter by ensemble style (JAZZ, MIXED, etc.)
- **Rating Filtering**: Filter by ensemble rating
- **Search Functionality**: Text search across all fields

### 📥 **Data Export**
- **CSV Downloads**: Export filtered data for external analysis
- **Multiple Formats**: Different export types for different use cases
- **Timestamped Files**: Automatic file naming with timestamps

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ensemble-management-dashboard
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv ensemble_dashboard_env

# Activate virtual environment
# On macOS/Linux:
source ensemble_dashboard_env/bin/activate
# On Windows:
ensemble_dashboard_env\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Prepare Data

Ensure your JSON data file is in the project directory:
- File name: `Find_Ensembles_ with Open Seats_ _(RE).json`
- Format: Valid JSON with ensemble data

### Step 5: Run the Application

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## 📖 Usage

### Getting Started

1. **Launch the Dashboard**: Run the application and open in your browser
2. **Select Term**: Choose the academic term from the sidebar
3. **Apply Filters**: Use sidebar filters to narrow down data
4. **Review Metrics**: Check the main metrics cards for overview
5. **Investigate Alerts**: Review critical alerts and low enrollment classes
6. **Export Data**: Download CSV files for external analysis

### Navigation Guide

#### **Main Dashboard**
- **Header**: Application title and branding
- **Metrics Cards**: Key performance indicators
- **Instrument Status**: Visual overview of instrument assignments

#### **Sidebar Filters**
- **Term Selection**: Choose academic term
- **Style Filter**: Filter by ensemble style
- **Rating Filter**: Filter by ensemble rating
- **Instrument Filters**: Show classes needing specific instruments

#### **Analytics Section**
- **Charts**: Interactive visualizations
- **Trends**: Enrollment patterns and distributions
- **Comparisons**: Instrument needs vs. enrollment

#### **Data Tables**
- **Ensemble Details**: Comprehensive class information
- **Search Functionality**: Find specific ensembles
- **Export Options**: Download filtered data

### Best Practices

1. **Regular Monitoring**: Check the dashboard daily during enrollment periods
2. **Alert Response**: Address critical alerts promptly
3. **Data Validation**: Verify exported data before making decisions
4. **Backup Strategy**: Keep regular backups of your data files

## 🏗️ Architecture

### Project Structure

```
ensemble-management-dashboard/
├── app.py                 # Main application file
├── config.py             # Configuration and settings
├── utils.py              # Utility functions
├── components.py         # UI components
├── requirements.txt      # Python dependencies
├── README.md            # Documentation
├── run_dashboard.py     # Launcher script
└── data/
    └── ensemble_data.json # Data file
```

### Code Organization

#### **app.py** - Main Application
- Streamlit application entry point
- Data loading and processing
- UI layout and navigation
- Filter application and data flow

#### **config.py** - Configuration
- Dashboard settings
- Color schemes and styling
- Data processing parameters
- Export configuration

#### **utils.py** - Utilities
- Data processing functions
- Calculation helpers
- Formatting utilities
- Export functions

#### **components.py** - UI Components
- Reusable UI components
- Chart creation functions
- Display helpers
- Interactive elements

### Data Flow

1. **Data Loading**: JSON file → Pandas DataFrame
2. **Processing**: Raw data → Calculated metrics
3. **Filtering**: Full dataset → Filtered views
4. **Display**: Processed data → UI components
5. **Export**: Filtered data → CSV files

## ⚙️ Configuration

### Customization Options

#### **Institutional Branding**
Edit `config.py` to customize:
- Institution name and colors
- Logo URL
- Primary and accent colors
- Dashboard title

#### **Alert Thresholds**
Modify alert settings in `config.py`:
```python
ALERT_CONFIG = {
    'low_enrollment_threshold': 4,
    'critical_enrollment_rate': 25,
    'full_capacity_threshold': 0
}
```

#### **Data Processing**
Adjust data processing parameters:
```python
DATA_CONFIG = {
    'instruments': ['GUIT', 'PNO', 'BASS', 'DRUMS', 'VOICE'],
    'low_enrollment_threshold': 4,
    'critical_enrollment_rate': 25
}
```

### Environment Variables

Set these environment variables for production deployment:
- `STREAMLIT_SERVER_PORT`: Port number (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: localhost)
- `STREAMLIT_SERVER_HEADLESS`: Run in headless mode (default: false)

## 📊 Data Structure

### JSON Data Format

The dashboard expects JSON data with the following structure:

```json
{
  "bSecTerm": "2025FA",
  "secInstrumentation_sectionname": "ENMX-100-001",
  "secInstrumentation_facnamepreffml": ["Faculty Name"],
  "secInstrumentation_titlelongcrs": ["Course Title"],
  "secInstrumentation_seatsavail": "7",
  "secInstrumentation_activestucount": "1",
  "secInstrumentation_seatscap": "8",
  "style": "MIXED",
  "ratingOverall": "1",
  "rhythminstrument": ["GUIT", "PNO", "BASS", "DRUMS", "VOICE"],
  "rhythmenrolled": ["0", "1", "0", "0", "0"],
  "rhythmneeded": [],
  "bSinCsmDays": ["F"],
  "bSinCsmStartTime": ["4:00:00 PM"],
  "bSinCsmEndTime": ["5:50:00 PM"]
}
```

### Required Fields

- **bSecTerm**: Academic term identifier
- **secInstrumentation_sectionname**: Class section number
- **secInstrumentation_facnamepreffml**: Faculty names (array)
- **secInstrumentation_titlelongcrs**: Course titles (array)
- **secInstrumentation_seatsavail**: Available seats
- **secInstrumentation_activestucount**: Enrolled students
- **secInstrumentation_seatscap**: Total capacity
- **style**: Ensemble style
- **ratingOverall**: Ensemble rating
- **rhythminstrument**: Instrument types (array)
- **rhythmenrolled**: Enrolled instruments (array)
- **rhythmneeded**: Needed instruments (array)
- **bSinCsmDays**: Schedule days (array)
- **bSinCsmStartTime**: Start times (array)
- **bSinCsmEndTime**: End times (array)

## 📚 API Documentation

### Core Functions

#### **Data Loading**
```python
from utils import load_ensemble_data

# Load data from JSON file
df = load_ensemble_data('path/to/data.json')
```

#### **Metrics Calculation**
```python
from utils import calculate_metrics

# Calculate key metrics
metrics = calculate_metrics(filtered_df)
```

#### **Instrument Processing**
```python
from utils import process_instrument_data

# Process instrument-specific data
df = process_instrument_data(df, ['GUIT', 'PNO', 'BASS', 'DRUMS', 'VOICE'])
```

#### **Data Export**
```python
from utils import prepare_download_data

# Prepare data for CSV export
export_df = prepare_download_data(df, data_type="ensemble")
```

### UI Components

#### **Metrics Display**
```python
from components import display_metrics_cards

# Display metrics in card format
display_metrics_cards(metrics)
```

#### **Chart Creation**
```python
from components import create_enrollment_distribution_chart

# Create enrollment distribution chart
fig = create_enrollment_distribution_chart(df)
```

## 🚀 Deployment

### Local Development

```bash
# Run in development mode
streamlit run app.py --server.port 8501
```

### Production Deployment

#### **Using Streamlit Cloud**
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Deploy automatically

#### **Using Docker**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### **Using Heroku**
1. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Deploy to Heroku:
```bash
heroku create your-app-name
git push heroku main
```

### Security Considerations

- **Data Protection**: Ensure sensitive data is properly secured
- **Access Control**: Implement authentication if needed
- **HTTPS**: Use HTTPS in production environments
- **Regular Updates**: Keep dependencies updated

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add type hints to functions
- Include docstrings for all functions
- Use meaningful variable names

### Testing

```bash
# Run tests (if implemented)
python -m pytest tests/

# Run linting
flake8 app.py utils.py components.py config.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

### Getting Help

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and ideas

### Contact Information

- **Maintainer**: [Your Name]
- **Email**: [your.email@institution.edu]
- **Department**: Music Department
- **Institution**: [Your Institution]

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Compatibility**: Python 3.8+, Streamlit 1.32.0+ 