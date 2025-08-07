"""
UI Components for Ensemble Management Dashboard
Reusable components for charts, metrics, and displays
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Tuple
from config import COLORS, STATUS_COLORS

def display_metrics_cards(metrics: Dict[str, float]) -> None:
    """
    Display main metrics in card style
    
    Args:
        metrics (Dict[str, float]): Dictionary of metrics to display
    """
    st.markdown(f"""
    <div style="margin: 2rem 0;">
        <div style="display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 2rem;">
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Total Ensembles</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['primary']}; margin: 0.5rem 0;">{metrics['total_ensembles']}</div>
            </div>
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Total Seats</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['primary']}; margin: 0.5rem 0;">{metrics['total_seats']}</div>
            </div>
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Enrolled Students</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['primary']}; margin: 0.5rem 0;">{metrics['enrolled_students']}</div>
            </div>
            <div class="metric-card" style="flex: 1; text-align: center;">
                <h3 style="margin: 0; color: #666; font-size: 1rem;">Open Seats</h3>
                <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['primary']}; margin: 0.5rem 0;">{metrics['open_seats']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_instrument_status_cards(instrument_df: pd.DataFrame) -> None:
    """
    Display instrument status overview cards
    
    Args:
        instrument_df (pd.DataFrame): Instrument summary data
    """
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
            
            st.markdown(f"""
            <div class="instrument-card {status_class}">
                <div class="status-icon">{status_icon}</div>
                <h3>{row['Instrument']}</h3>
                <p><strong>Needed:</strong> {row['Needed']}</p>
                <p><strong>Enrolled:</strong> {row['Enrolled']}</p>
                <p><strong>Fill Rate:</strong> {row['Fill Rate']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

def create_enrollment_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create enrollment rate distribution histogram
    
    Args:
        df (pd.DataFrame): Filtered ensemble data
        
    Returns:
        go.Figure: Plotly figure object
    """
    fig = px.histogram(
        df, 
        x='enrollment_rate',
        nbins=20,
        title="Enrollment Rate Distribution",
        labels={'enrollment_rate': 'Enrollment Rate (%)', 'count': 'Number of Ensembles'},
        color_discrete_sequence=[COLORS['primary']]
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    fig.update_xaxes(gridcolor='lightgray', gridwidth=0.5)
    fig.update_yaxes(gridcolor='lightgray', gridwidth=0.5)
    return fig

def create_instrument_needs_chart(instrument_df: pd.DataFrame) -> go.Figure:
    """
    Create instrument needs vs enrolled bar chart
    
    Args:
        instrument_df (pd.DataFrame): Instrument summary data
        
    Returns:
        go.Figure: Plotly figure object
    """
    fig = px.bar(
        instrument_df,
        x='Instrument',
        y=['Needed', 'Enrolled'],
        title="Instrument Needs vs Enrolled",
        barmode='group',
        color_discrete_map={
            'Needed': COLORS['danger'],
            'Enrolled': COLORS['success']
        }
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    fig.update_xaxes(gridcolor='lightgray', gridwidth=0.5)
    fig.update_yaxes(gridcolor='lightgray', gridwidth=0.5)
    return fig

def create_enrollment_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create enrollment trend over time (if time data available)
    
    Args:
        df (pd.DataFrame): Filtered ensemble data
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Group by style and calculate average enrollment rate
    style_enrollment = df.groupby('style')['enrollment_rate'].mean().reset_index()
    
    fig = px.bar(
        style_enrollment,
        x='style',
        y='enrollment_rate',
        title="Average Enrollment Rate by Style",
        labels={'enrollment_rate': 'Average Enrollment Rate (%)', 'style': 'Ensemble Style'},
        color='enrollment_rate',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    fig.update_xaxes(gridcolor='lightgray', gridwidth=0.5)
    fig.update_yaxes(gridcolor='lightgray', gridwidth=0.5)
    return fig

def display_ensemble_card(ensemble: pd.Series, card_type: str = "info") -> None:
    """
    Display individual ensemble information card
    
    Args:
        ensemble (pd.Series): Ensemble data
        card_type (str): Type of card styling
    """
    section_name = ensemble['secInstrumentation_sectionname']
    course_title = ensemble['secInstrumentation_titlelongcrs'][0] if isinstance(ensemble['secInstrumentation_titlelongcrs'], list) and len(ensemble['secInstrumentation_titlelongcrs']) > 0 else 'N/A'
    faculty = ', '.join(ensemble['secInstrumentation_facnamepreffml']) if isinstance(ensemble['secInstrumentation_facnamepreffml'], list) else 'N/A'
    days = ', '.join(ensemble['bSinCsmDays']) if isinstance(ensemble['bSinCsmDays'], list) else 'N/A'
    time = f"{ensemble['bSinCsmStartTime'][0] if isinstance(ensemble['bSinCsmStartTime'], list) else 'N/A'} - {ensemble['bSinCsmEndTime'][0] if isinstance(ensemble['bSinCsmEndTime'], list) else 'N/A'}"
    
    if card_type == "danger":
        st.markdown(f"""
        <div class="info-box danger">
            <strong>🎵 {section_name}</strong><br>
            <strong>Course:</strong> {course_title}<br>
            <strong>Faculty:</strong> {faculty}<br>
            <strong>Schedule:</strong> {days} at {time}<br>
        </div>
        """, unsafe_allow_html=True)
    elif card_type == "warning":
        st.markdown(f"""
        <div class="info-box warning">
            <strong>🎵 {section_name}</strong><br>
            <strong>Course:</strong> {course_title}<br>
            <strong>Faculty:</strong> {faculty}<br>
            <strong>Schedule:</strong> {days} at {time}<br>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            <strong>🎵 {section_name}</strong><br>
            <strong>Course:</strong> {course_title}<br>
            <strong>Faculty:</strong> {faculty}<br>
            <strong>Schedule:</strong> {days} at {time}<br>
        </div>
        """, unsafe_allow_html=True)

def display_low_enrollment_alert(ensemble: pd.Series) -> None:
    """
    Display low enrollment alert card
    
    Args:
        ensemble (pd.Series): Ensemble data
    """
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
    
    st.markdown(f"""
    <div class="info-box {severity}" style="border-left: 6px solid #f44336; background-color: #ffebee; position: relative;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <strong style="color: #000000; font-size: 1.2rem;">{status}</strong>
        </div>
        <strong style="color: #000000;">🎵 {section_name}</strong><br>
        <strong style="color: #000000;">Course:</strong> {course_title}<br>
        <strong style="color: #000000;">Faculty:</strong> {faculty}<br>
        <strong style="color: #000000;">Schedule:</strong> {days} at {time}<br>
        <strong style="color: #000000;">Enrollment:</strong> {enrolled_count} / {total_capacity} students ({enrollment_rate:.1f}%)<br>
        <div style="position: absolute; top: 10px; right: 10px; background-color: #d32f2f; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 0.9rem;">
            ⚠️ POTENTIALLY WILL BE DROPPED
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_low_enrollment_summary(low_enrollment_classes: pd.DataFrame) -> None:
    """
    Display low enrollment summary statistics
    
    Args:
        low_enrollment_classes (pd.DataFrame): Low enrollment classes data
    """
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

def create_download_section(df: pd.DataFrame, term: str, data_type: str = "ensemble") -> None:
    """
    Create download section with CSV export
    
    Args:
        df (pd.DataFrame): Data to export
        term (str): Academic term
        data_type (str): Type of data being exported
    """
    from utils import prepare_download_data, generate_filename
    
    st.markdown("---")
    st.subheader("📥 Download Data")
    
    # Prepare data for download
    download_df = prepare_download_data(df, data_type)
    
    # Generate filename
    filename = generate_filename("ensemble_dashboard", term, data_type)
    
    # Download button
    csv = download_df.to_csv(index=False)
    st.download_button(
        label=f"📥 Download {data_type.replace('_', ' ').title()} Data (CSV)",
        data=csv,
        file_name=filename,
        mime="text/csv",
        help=f"Download {data_type.replace('_', ' ')} data as a CSV file"
    )

def display_analytics_section(df: pd.DataFrame, instrument_df: pd.DataFrame) -> None:
    """
    Display analytics section with charts
    
    Args:
        df (pd.DataFrame): Filtered ensemble data
        instrument_df (pd.DataFrame): Instrument summary data
    """
    st.subheader("📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_enrollment = create_enrollment_distribution_chart(df)
        st.plotly_chart(fig_enrollment, use_container_width=True)
    
    with col2:
        fig_instruments = create_instrument_needs_chart(instrument_df)
        st.plotly_chart(fig_instruments, use_container_width=True)
    
    # Additional chart
    col3, col4 = st.columns(2)
    
    with col3:
        fig_trend = create_enrollment_trend_chart(df)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col4:
        # Capacity utilization chart
        capacity_data = df[['secInstrumentation_activestucount', 'secInstrumentation_seatscap']].copy()
        capacity_data['utilization'] = (capacity_data['secInstrumentation_activestucount'] / capacity_data['secInstrumentation_seatscap'] * 100).fillna(0)
        
        fig_capacity = px.histogram(
            capacity_data,
            x='utilization',
            nbins=15,
            title="Capacity Utilization Distribution",
            labels={'utilization': 'Capacity Utilization (%)', 'count': 'Number of Ensembles'},
            color_discrete_sequence=[COLORS['secondary']]
        )
        fig_capacity.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        fig_capacity.update_xaxes(gridcolor='lightgray', gridwidth=0.5)
        fig_capacity.update_yaxes(gridcolor='lightgray', gridwidth=0.5)
        st.plotly_chart(fig_capacity, use_container_width=True) 