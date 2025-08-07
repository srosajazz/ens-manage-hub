"""
Utility functions for Ensemble Management Dashboard
Helper functions for data processing, calculations, and formatting
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

def load_ensemble_data(file_path: str) -> pd.DataFrame:
    """
    Load and process ensemble data from JSON file
    
    Args:
        file_path (str): Path to the JSON data file
        
    Returns:
        pd.DataFrame: Processed ensemble data
    """
    try:
        with open(file_path, 'r') as file:
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
        
        return df
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")

def process_instrument_data(df: pd.DataFrame, instruments: List[str]) -> pd.DataFrame:
    """
    Process instrument-specific data and create status columns
    
    Args:
        df (pd.DataFrame): Input dataframe
        instruments (List[str]): List of instrument codes
        
    Returns:
        pd.DataFrame: DataFrame with instrument status columns
    """
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

def calculate_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate key metrics for the dashboard
    
    Args:
        df (pd.DataFrame): Filtered ensemble data
        
    Returns:
        Dict[str, float]: Dictionary of calculated metrics
    """
    metrics = {
        'total_ensembles': len(df),
        'total_seats': int(df['secInstrumentation_seatscap'].sum()),
        'enrolled_students': int(df['secInstrumentation_activestucount'].sum()),
        'open_seats': int(df['open_seats'].sum()),
        'avg_enrollment_rate': float(df['enrollment_rate'].mean()),
        'low_enrollment_classes': len(df[df['secInstrumentation_activestucount'] < 4])
    }
    
    return metrics

def get_instrument_summary(df: pd.DataFrame, instruments: List[str]) -> pd.DataFrame:
    """
    Generate instrument status summary
    
    Args:
        df (pd.DataFrame): Filtered ensemble data
        instruments (List[str]): List of instrument codes
        
    Returns:
        pd.DataFrame: Instrument summary statistics
    """
    instrument_summary = []
    
    for instrument in instruments:
        needed = df[f'{instrument}_needed'].sum()
        enrolled = df[f'{instrument}_enrolled'].sum()
        filled = df[df[f'{instrument}_status'] == 'Filled'].shape[0]
        total_ensembles_with_instrument = df[df[f'{instrument}_needed'] > 0].shape[0]
        
        fill_rate = (filled / total_ensembles_with_instrument * 100) if total_ensembles_with_instrument > 0 else 0
        
        instrument_summary.append({
            'Instrument': instrument,
            'Needed': needed,
            'Enrolled': enrolled,
            'Filled Ensembles': filled,
            'Total Ensembles': total_ensembles_with_instrument,
            'Fill Rate': fill_rate
        })
    
    return pd.DataFrame(instrument_summary)

def get_status_color(status: str) -> str:
    """
    Get color for status indicators
    
    Args:
        status (str): Status string
        
    Returns:
        str: Color hex code
    """
    color_map = {
        'Filled': '#4caf50',  # Green
        'Needed': '#f44336',  # Red
        'Not Required': '#ff9800',  # Orange
        'critical': '#d32f2f',
        'warning': '#f57c00',
        'success': '#388e3c',
        'info': '#1976d2'
    }
    
    return color_map.get(status, '#757575')  # Default gray

def format_time_range(start_time: List[str], end_time: List[str]) -> str:
    """
    Format time range for display
    
    Args:
        start_time (List[str]): Start time list
        end_time (List[str]): End time list
        
    Returns:
        str: Formatted time range
    """
    start = start_time[0] if isinstance(start_time, list) and len(start_time) > 0 else 'N/A'
    end = end_time[0] if isinstance(end_time, list) and len(end_time) > 0 else 'N/A'
    return f"{start} - {end}"

def format_faculty_names(faculty_list: List[str]) -> str:
    """
    Format faculty names for display
    
    Args:
        faculty_list (List[str]): List of faculty names
        
    Returns:
        str: Formatted faculty string
    """
    if isinstance(faculty_list, list):
        return ', '.join(faculty_list)
    return 'N/A'

def format_course_title(title_list: List[str]) -> str:
    """
    Format course title for display
    
    Args:
        title_list (List[str]): List of course titles
        
    Returns:
        str: Formatted course title
    """
    if isinstance(title_list, list) and len(title_list) > 0:
        return title_list[0]
    return 'N/A'

def format_schedule_days(days_list: List[str]) -> str:
    """
    Format schedule days for display
    
    Args:
        days_list (List[str]): List of days
        
    Returns:
        str: Formatted days string
    """
    if isinstance(days_list, list):
        return ', '.join(days_list)
    return 'N/A'

def get_enrollment_status(enrolled_count: int, total_capacity: int) -> Tuple[str, str, str]:
    """
    Determine enrollment status and styling
    
    Args:
        enrolled_count (int): Number of enrolled students
        total_capacity (int): Total capacity
        
    Returns:
        Tuple[str, str, str]: (severity, icon, status_text)
    """
    if enrolled_count == 0:
        return "danger", "🚨", "CRITICAL - NO STUDENTS"
    elif enrolled_count == 1:
        return "danger", "🚨", "CRITICAL - ONLY 1 STUDENT"
    elif enrolled_count == 2:
        return "warning", "⚠️", "WARNING - ONLY 2 STUDENTS"
    elif enrolled_count == 3:
        return "warning", "⚠️", "WARNING - ONLY 3 STUDENTS"
    else:
        enrollment_rate = (enrolled_count / total_capacity) * 100
        if enrollment_rate < 25:
            return "warning", "⚠️", f"LOW ENROLLMENT - {enrollment_rate:.1f}%"
        else:
            return "success", "✅", f"GOOD ENROLLMENT - {enrollment_rate:.1f}%"

def prepare_download_data(df: pd.DataFrame, data_type: str = "ensemble") -> pd.DataFrame:
    """
    Prepare data for CSV download
    
    Args:
        df (pd.DataFrame): Source dataframe
        data_type (str): Type of data to prepare
        
    Returns:
        pd.DataFrame: Formatted data for download
    """
    if data_type == "low_enrollment":
        download_data = []
        for _, ensemble in df.iterrows():
            section_name = ensemble['secInstrumentation_sectionname']
            course_title = format_course_title(ensemble['secInstrumentation_titlelongcrs'])
            faculty = format_faculty_names(ensemble['secInstrumentation_facnamepreffml'])
            days = format_schedule_days(ensemble['bSinCsmDays'])
            time = format_time_range(ensemble['bSinCsmStartTime'], ensemble['bSinCsmEndTime'])
            enrolled_count = ensemble['secInstrumentation_activestucount']
            total_capacity = ensemble['secInstrumentation_seatscap']
            enrollment_rate = ensemble['enrollment_rate']
            
            _, _, status = get_enrollment_status(enrolled_count, total_capacity)
            
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
        
        return pd.DataFrame(download_data)
    
    else:  # ensemble data
        # Select and format columns for general ensemble export
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
        
        table_df = df[display_columns].copy()
        
        # Clean up the data for display
        table_df['Course Title'] = table_df['secInstrumentation_titlelongcrs'].apply(format_course_title)
        table_df['Faculty'] = table_df['secInstrumentation_facnamepreffml'].apply(format_faculty_names)
        table_df['Days'] = table_df['bSinCsmDays'].apply(format_schedule_days)
        table_df['Time'] = table_df.apply(
            lambda row: format_time_range(row['bSinCsmStartTime'], row['bSinCsmEndTime']),
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
        return final_df

def generate_filename(prefix: str, term: str, data_type: str = "data") -> str:
    """
    Generate standardized filename for downloads
    
    Args:
        prefix (str): File prefix
        term (str): Academic term
        data_type (str): Type of data
        
    Returns:
        str: Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{data_type}_{term}_{timestamp}.csv" 