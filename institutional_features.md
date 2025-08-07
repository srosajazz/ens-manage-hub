# 🏛️ Institutional Features Enhancement Guide

Comprehensive guide for enhancing the Ensemble Management Dashboard with institutional-grade features.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication & Authorization](#authentication--authorization)
- [Multi-User Support](#multi-user-support)
- [Advanced Analytics](#advanced-analytics)
- [Reporting & Export](#reporting--export)
- [Integration Capabilities](#integration-capabilities)
- [Administrative Features](#administrative-features)
- [Compliance & Security](#compliance--security)
- [Implementation Roadmap](#implementation-roadmap)

## 🎯 Overview

This document outlines advanced features that can transform the Ensemble Management Dashboard into a comprehensive institutional management system. These enhancements focus on scalability, security, compliance, and administrative efficiency.

## 🔐 Authentication & Authorization

### Role-Based Access Control (RBAC)

```python
# roles.py
from enum import Enum
from typing import List, Dict

class UserRole(Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"
    DEPARTMENT_HEAD = "department_head"
    REGISTRAR = "registrar"

class Permission(Enum):
    VIEW_ENSEMBLES = "view_ensembles"
    EDIT_ENSEMBLES = "edit_ensembles"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    MANAGE_USERS = "manage_users"
    VIEW_SENSITIVE_DATA = "view_sensitive_data"

ROLE_PERMISSIONS = {
    UserRole.STUDENT: [Permission.VIEW_ENSEMBLES],
    UserRole.FACULTY: [
        Permission.VIEW_ENSEMBLES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA
    ],
    UserRole.ADMIN: [
        Permission.VIEW_ENSEMBLES,
        Permission.EDIT_ENSEMBLES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
        Permission.MANAGE_USERS
    ],
    UserRole.DEPARTMENT_HEAD: [
        Permission.VIEW_ENSEMBLES,
        Permission.EDIT_ENSEMBLES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
        Permission.VIEW_SENSITIVE_DATA
    ],
    UserRole.REGISTRAR: [
        Permission.VIEW_ENSEMBLES,
        Permission.EDIT_ENSEMBLES,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_DATA,
        Permission.VIEW_SENSITIVE_DATA,
        Permission.MANAGE_USERS
    ]
}
```

### Single Sign-On (SSO) Integration

```python
# sso_integration.py
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import jwt

class SSOIntegration:
    def __init__(self, client_id: str, client_secret: str, issuer_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.issuer_url = issuer_url
        
    def authenticate_user(self):
        """Authenticate user via SSO"""
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri="http://localhost:8501/callback"
        )
        
        authorization_url, state = oauth.create_authorization_url(
            f"{self.issuer_url}/auth"
        )
        
        return authorization_url, state
    
    def verify_token(self, token: str) -> Dict:
        """Verify JWT token from SSO provider"""
        try:
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return decoded
        except jwt.InvalidTokenError:
            return None
```

### Session Management

```python
# session_manager.py
import streamlit as st
from datetime import datetime, timedelta
import hashlib

class SessionManager:
    def __init__(self):
        self.session_timeout = timedelta(hours=8)
    
    def create_session(self, user_id: str, role: str) -> str:
        """Create a new user session"""
        session_data = {
            'user_id': user_id,
            'role': role,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + self.session_timeout).isoformat()
        }
        
        session_token = hashlib.sha256(
            f"{user_id}{datetime.now()}".encode()
        ).hexdigest()
        
        st.session_state['session_token'] = session_token
        st.session_state['session_data'] = session_data
        
        return session_token
    
    def validate_session(self) -> bool:
        """Validate current session"""
        if 'session_data' not in st.session_state:
            return False
        
        session_data = st.session_state['session_data']
        expires_at = datetime.fromisoformat(session_data['expires_at'])
        
        if datetime.now() > expires_at:
            self.clear_session()
            return False
        
        return True
    
    def clear_session(self):
        """Clear current session"""
        if 'session_token' in st.session_state:
            del st.session_state['session_token']
        if 'session_data' in st.session_state:
            del st.session_state['session_data']
```

## 👥 Multi-User Support

### User Management System

```python
# user_management.py
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional

class UserManagement:
    def __init__(self):
        self.users_file = "data/users.json"
        self.users = self.load_users()
    
    def load_users(self) -> List[Dict]:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def add_user(self, username: str, email: str, role: str, 
                 department: str = None) -> bool:
        """Add a new user"""
        user = {
            'id': len(self.users) + 1,
            'username': username,
            'email': email,
            'role': role,
            'department': department,
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        self.users.append(user)
        self.save_users()
        return True
    
    def update_user(self, user_id: int, updates: Dict) -> bool:
        """Update user information"""
        for user in self.users:
            if user['id'] == user_id:
                user.update(updates)
                self.save_users()
                return True
        return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user"""
        return self.update_user(user_id, {'is_active': False})
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """Get all users with a specific role"""
        return [user for user in self.users if user['role'] == role]
    
    def get_users_by_department(self, department: str) -> List[Dict]:
        """Get all users in a specific department"""
        return [user for user in self.users if user['department'] == department]
```

### Department Management

```python
# department_management.py
class DepartmentManagement:
    def __init__(self):
        self.departments = {
            'MUSIC': {
                'name': 'Music Department',
                'head': 'Dr. Smith',
                'ensembles': ['JAZZ', 'CLASSICAL', 'MIXED'],
                'faculty': []
            },
            'THEATER': {
                'name': 'Theater Department',
                'head': 'Dr. Johnson',
                'ensembles': ['MUSICAL', 'DRAMA'],
                'faculty': []
            }
        }
    
    def get_department_ensembles(self, department: str) -> List[str]:
        """Get ensembles for a specific department"""
        return self.departments.get(department, {}).get('ensembles', [])
    
    def get_department_faculty(self, department: str) -> List[str]:
        """Get faculty for a specific department"""
        return self.departments.get(department, {}).get('faculty', [])
    
    def add_department(self, dept_code: str, dept_name: str, 
                      head: str, ensembles: List[str]):
        """Add a new department"""
        self.departments[dept_code] = {
            'name': dept_name,
            'head': head,
            'ensembles': ensembles,
            'faculty': []
        }
```

## 📊 Advanced Analytics

### Predictive Analytics

```python
# predictive_analytics.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

class PredictiveAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.model = None
    
    def prepare_features(self) -> pd.DataFrame:
        """Prepare features for prediction"""
        features = self.df.copy()
        
        # Create time-based features
        features['term_year'] = features['bSecTerm'].str[:4].astype(int)
        features['term_semester'] = features['bSecTerm'].str[4:].map({
            'FA': 1, 'SP': 2, 'SU': 3
        })
        
        # Create ensemble features
        features['total_instruments'] = features['rhythminstrument'].apply(len)
        features['enrolled_instruments'] = features['rhythmenrolled'].apply(
            lambda x: sum(int(i) for i in x)
        )
        
        # Create faculty features
        features['faculty_count'] = features['secInstrumentation_facnamepreffml'].apply(
            lambda x: len(x) if isinstance(x, list) else 1
        )
        
        return features
    
    def predict_enrollment(self, ensemble_data: Dict) -> float:
        """Predict enrollment for a new ensemble"""
        if self.model is None:
            self.train_model()
        
        # Prepare features for prediction
        features = self.prepare_features()
        feature_columns = [
            'term_year', 'term_semester', 'total_instruments',
            'faculty_count', 'secInstrumentation_seatscap'
        ]
        
        X = features[feature_columns].dropna()
        y = features['secInstrumentation_activestucount'].dropna()
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Make prediction
        prediction_features = np.array([
            ensemble_data['term_year'],
            ensemble_data['term_semester'],
            ensemble_data['total_instruments'],
            ensemble_data['faculty_count'],
            ensemble_data['capacity']
        ]).reshape(1, -1)
        
        return self.model.predict(prediction_features)[0]
    
    def get_enrollment_trends(self) -> Dict:
        """Analyze enrollment trends over time"""
        features = self.prepare_features()
        
        trends = {}
        for style in features['style'].unique():
            style_data = features[features['style'] == style]
            trends[style] = {
                'avg_enrollment': style_data['secInstrumentation_activestucount'].mean(),
                'enrollment_trend': style_data.groupby('term_year')[
                    'secInstrumentation_activestucount'
                ].mean().to_dict(),
                'capacity_utilization': (
                    style_data['secInstrumentation_activestucount'].sum() /
                    style_data['secInstrumentation_seatscap'].sum() * 100
                )
            }
        
        return trends
```

### Advanced Visualizations

```python
# advanced_visualizations.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class AdvancedVisualizations:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def create_enrollment_heatmap(self) -> go.Figure:
        """Create enrollment heatmap by style and term"""
        pivot_data = self.df.pivot_table(
            values='enrollment_rate',
            index='style',
            columns='bSecTerm',
            aggfunc='mean'
        ).fillna(0)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='RdYlGn',
            text=pivot_data.values.round(1),
            texttemplate="%{text}%",
            textfont={"size": 10},
            colorbar=dict(title="Enrollment Rate (%)")
        ))
        
        fig.update_layout(
            title="Enrollment Rate Heatmap by Style and Term",
            xaxis_title="Academic Term",
            yaxis_title="Ensemble Style",
            height=500
        )
        
        return fig
    
    def create_instrument_network(self) -> go.Figure:
        """Create instrument co-occurrence network"""
        # Analyze instrument combinations
        instrument_combinations = []
        for _, row in self.df.iterrows():
            instruments = row['rhythminstrument']
            if isinstance(instruments, list):
                for i in range(len(instruments)):
                    for j in range(i+1, len(instruments)):
                        instrument_combinations.append(
                            (instruments[i], instruments[j])
                        )
        
        # Count combinations
        from collections import Counter
        combo_counts = Counter(instrument_combinations)
        
        # Create network
        nodes = set()
        for combo in combo_counts.keys():
            nodes.add(combo[0])
            nodes.add(combo[1])
        
        node_trace = go.Scatter(
            x=[], y=[], text=[], mode='markers+text',
            hoverinfo='text', textposition="top center",
            marker=dict(size=20, color='lightblue')
        )
        
        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0.5, color='#888'),
            hoverinfo='none', mode='lines'
        )
        
        # Add nodes and edges
        for node in nodes:
            node_trace['x'] += (np.random.randn(1) * 10,)
            node_trace['y'] += (np.random.randn(1) * 10,)
            node_trace['text'] += (node,)
        
        for (src, dst), weight in combo_counts.items():
            edge_trace['x'] += (node_trace['x'][list(nodes).index(src)],
                              node_trace['x'][list(nodes).index(dst)], None)
            edge_trace['y'] += (node_trace['y'][list(nodes).index(src)],
                              node_trace['y'][list(nodes).index(dst)], None)
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title="Instrument Co-occurrence Network",
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40)
                       ))
        
        return fig
    
    def create_enrollment_forecast(self) -> go.Figure:
        """Create enrollment forecast chart"""
        # Group by term and calculate trends
        term_data = self.df.groupby('bSecTerm').agg({
            'secInstrumentation_activestucount': 'sum',
            'secInstrumentation_seatscap': 'sum'
        }).reset_index()
        
        term_data['enrollment_rate'] = (
            term_data['secInstrumentation_activestucount'] /
            term_data['secInstrumentation_seatscap'] * 100
        )
        
        # Create forecast
        x = np.arange(len(term_data))
        z = np.polyfit(x, term_data['enrollment_rate'], 1)
        p = np.poly1d(z)
        
        # Future terms
        future_terms = 3
        future_x = np.arange(len(term_data), len(term_data) + future_terms)
        future_y = p(future_x)
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=term_data['bSecTerm'],
            y=term_data['enrollment_rate'],
            mode='lines+markers',
            name='Historical',
            line=dict(color='blue', width=2)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=[f"Future_{i+1}" for i in range(future_terms)],
            y=future_y,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="Enrollment Rate Forecast",
            xaxis_title="Academic Term",
            yaxis_title="Enrollment Rate (%)",
            height=400
        )
        
        return fig
```

## 📄 Reporting & Export

### Advanced Reporting System

```python
# reporting_system.py
import pandas as pd
from datetime import datetime
import json
from typing import Dict, List

class ReportingSystem:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def generate_executive_summary(self) -> Dict:
        """Generate executive summary report"""
        summary = {
            'report_date': datetime.now().isoformat(),
            'total_ensembles': len(self.df),
            'total_capacity': int(self.df['secInstrumentation_seatscap'].sum()),
            'total_enrolled': int(self.df['secInstrumentation_activestucount'].sum()),
            'overall_enrollment_rate': float(
                self.df['secInstrumentation_activestucount'].sum() /
                self.df['secInstrumentation_seatscap'].sum() * 100
            ),
            'low_enrollment_classes': len(
                self.df[self.df['secInstrumentation_activestucount'] < 4]
            ),
            'full_capacity_classes': len(
                self.df[self.df['secInstrumentation_seatsavail'] == 0]
            ),
            'style_breakdown': self.df['style'].value_counts().to_dict(),
            'term_summary': self.df['bSecTerm'].value_counts().to_dict()
        }
        
        return summary
    
    def generate_department_report(self, department: str) -> Dict:
        """Generate department-specific report"""
        dept_data = self.df[self.df['style'].str.contains(department, case=False)]
        
        report = {
            'department': department,
            'report_date': datetime.now().isoformat(),
            'total_ensembles': len(dept_data),
            'enrollment_summary': {
                'total_capacity': int(dept_data['secInstrumentation_seatscap'].sum()),
                'total_enrolled': int(dept_data['secInstrumentation_activestucount'].sum()),
                'enrollment_rate': float(
                    dept_data['secInstrumentation_activestucount'].sum() /
                    dept_data['secInstrumentation_seatscap'].sum() * 100
                )
            },
            'faculty_summary': self._get_faculty_summary(dept_data),
            'instrument_needs': self._get_instrument_needs(dept_data),
            'risk_assessment': self._get_risk_assessment(dept_data)
        }
        
        return report
    
    def generate_faculty_report(self, faculty_name: str) -> Dict:
        """Generate faculty-specific report"""
        faculty_data = self.df[
            self.df['secInstrumentation_facnamepreffml'].apply(
                lambda x: faculty_name in x if isinstance(x, list) else False
            )
        ]
        
        report = {
            'faculty_name': faculty_name,
            'report_date': datetime.now().isoformat(),
            'ensembles_taught': len(faculty_data),
            'total_students': int(faculty_data['secInstrumentation_activestucount'].sum()),
            'avg_enrollment_rate': float(faculty_data['enrollment_rate'].mean()),
            'ensemble_details': faculty_data[[
                'secInstrumentation_sectionname',
                'secInstrumentation_titlelongcrs',
                'secInstrumentation_activestucount',
                'secInstrumentation_seatscap',
                'enrollment_rate'
            ]].to_dict('records')
        }
        
        return report
    
    def export_to_pdf(self, report_data: Dict, filename: str):
        """Export report to PDF format"""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph(f"Ensemble Management Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Date
        date_text = Paragraph(f"Generated: {report_data.get('report_date', 'N/A')}", 
                             styles['Normal'])
        story.append(date_text)
        story.append(Spacer(1, 12))
        
        # Content
        for key, value in report_data.items():
            if key != 'report_date':
                if isinstance(value, dict):
                    story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", 
                                         styles['Heading2']))
                    for sub_key, sub_value in value.items():
                        story.append(Paragraph(f"  {sub_key}: {sub_value}", 
                                             styles['Normal']))
                else:
                    story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", 
                                         styles['Normal']))
                story.append(Spacer(1, 6))
        
        doc.build(story)
    
    def _get_faculty_summary(self, data: pd.DataFrame) -> Dict:
        """Get faculty summary for department"""
        faculty_counts = {}
        for faculty_list in data['secInstrumentation_facnamepreffml']:
            if isinstance(faculty_list, list):
                for faculty in faculty_list:
                    faculty_counts[faculty] = faculty_counts.get(faculty, 0) + 1
        
        return faculty_counts
    
    def _get_instrument_needs(self, data: pd.DataFrame) -> Dict:
        """Get instrument needs summary"""
        instrument_needs = {}
        for instruments in data['rhythminstrument']:
            if isinstance(instruments, list):
                for instrument in instruments:
                    instrument_needs[instrument] = instrument_needs.get(instrument, 0) + 1
        
        return instrument_needs
    
    def _get_risk_assessment(self, data: pd.DataFrame) -> Dict:
        """Get risk assessment for department"""
        low_enrollment = len(data[data['secInstrumentation_activestucount'] < 4])
        no_students = len(data[data['secInstrumentation_activestucount'] == 0])
        full_capacity = len(data[data['secInstrumentation_seatsavail'] == 0])
        
        return {
            'low_enrollment_classes': low_enrollment,
            'classes_with_no_students': no_students,
            'full_capacity_classes': full_capacity,
            'risk_level': 'HIGH' if low_enrollment > len(data) * 0.3 else 'MEDIUM'
        }
```

## 🔗 Integration Capabilities

### Student Information System (SIS) Integration

```python
# sis_integration.py
import requests
from typing import Dict, List

class SISIntegration:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_student_enrollment(self, student_id: str) -> Dict:
        """Get student enrollment information from SIS"""
        response = requests.get(
            f"{self.api_url}/students/{student_id}/enrollment",
            headers=self.headers
        )
        return response.json()
    
    def get_course_roster(self, course_id: str) -> List[Dict]:
        """Get course roster from SIS"""
        response = requests.get(
            f"{self.api_url}/courses/{course_id}/roster",
            headers=self.headers
        )
        return response.json()
    
    def update_enrollment(self, course_id: str, student_id: str, 
                         action: str) -> bool:
        """Update enrollment in SIS"""
        data = {
            'course_id': course_id,
            'student_id': student_id,
            'action': action  # 'add' or 'drop'
        }
        
        response = requests.post(
            f"{self.api_url}/enrollment/update",
            headers=self.headers,
            json=data
        )
        
        return response.status_code == 200
```

### Learning Management System (LMS) Integration

```python
# lms_integration.py
class LMSIntegration:
    def __init__(self, lms_url: str, api_key: str):
        self.lms_url = lms_url
        self.api_key = api_key
    
    def sync_ensemble_data(self, ensemble_data: Dict) -> bool:
        """Sync ensemble data with LMS"""
        # Implementation for specific LMS (Canvas, Blackboard, etc.)
        pass
    
    def create_assignment(self, ensemble_id: str, assignment_data: Dict) -> str:
        """Create assignment in LMS"""
        pass
    
    def get_student_submissions(self, assignment_id: str) -> List[Dict]:
        """Get student submissions from LMS"""
        pass
```

### Email Integration

```python
# email_integration.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

class EmailIntegration:
    def __init__(self, smtp_server: str, smtp_port: int, 
                 username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_low_enrollment_alert(self, ensemble_data: Dict, 
                                 recipients: List[str]):
        """Send low enrollment alert email"""
        subject = f"Low Enrollment Alert: {ensemble_data['section_name']}"
        
        body = f"""
        <html>
        <body>
        <h2>Low Enrollment Alert</h2>
        <p>The following ensemble has low enrollment and may be at risk of cancellation:</p>
        
        <table border="1">
        <tr><td><strong>Section:</strong></td><td>{ensemble_data['section_name']}</td></tr>
        <tr><td><strong>Course:</strong></td><td>{ensemble_data['course_title']}</td></tr>
        <tr><td><strong>Faculty:</strong></td><td>{ensemble_data['faculty']}</td></tr>
        <tr><td><strong>Enrolled:</strong></td><td>{ensemble_data['enrolled']}</td></tr>
        <tr><td><strong>Capacity:</strong></td><td>{ensemble_data['capacity']}</td></tr>
        <tr><td><strong>Enrollment Rate:</strong></td><td>{ensemble_data['enrollment_rate']:.1f}%</td></tr>
        </table>
        
        <p>Please review this ensemble and take appropriate action.</p>
        </body>
        </html>
        """
        
        self._send_email(recipients, subject, body)
    
    def send_weekly_report(self, report_data: Dict, recipients: List[str]):
        """Send weekly enrollment report"""
        subject = "Weekly Ensemble Enrollment Report"
        
        body = f"""
        <html>
        <body>
        <h2>Weekly Ensemble Enrollment Report</h2>
        
        <h3>Summary</h3>
        <ul>
        <li>Total Ensembles: {report_data['total_ensembles']}</li>
        <li>Total Enrolled: {report_data['total_enrolled']}</li>
        <li>Overall Enrollment Rate: {report_data['overall_enrollment_rate']:.1f}%</li>
        <li>Low Enrollment Classes: {report_data['low_enrollment_classes']}</li>
        </ul>
        
        <h3>Style Breakdown</h3>
        <ul>
        """
        
        for style, count in report_data['style_breakdown'].items():
            body += f"<li>{style}: {count} ensembles</li>"
        
        body += """
        </ul>
        
        <p>Please review the attached detailed report for more information.</p>
        </body>
        </html>
        """
        
        self._send_email(recipients, subject, body)
    
    def _send_email(self, recipients: List[str], subject: str, body: str):
        """Send email to recipients"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = ', '.join(recipients)
        
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
```

## ⚙️ Administrative Features

### Audit Trail System

```python
# audit_trail.py
import json
from datetime import datetime
from typing import Dict, List

class AuditTrail:
    def __init__(self, log_file: str = "audit_trail.json"):
        self.log_file = log_file
        self.audit_log = self.load_audit_log()
    
    def load_audit_log(self) -> List[Dict]:
        """Load audit log from file"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_audit_log(self):
        """Save audit log to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
    
    def log_action(self, user_id: str, action: str, resource: str, 
                   details: Dict = None):
        """Log an action in the audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': details or {},
            'ip_address': self._get_client_ip()
        }
        
        self.audit_log.append(log_entry)
        self.save_audit_log()
    
    def get_user_actions(self, user_id: str) -> List[Dict]:
        """Get all actions performed by a user"""
        return [entry for entry in self.audit_log if entry['user_id'] == user_id]
    
    def get_resource_actions(self, resource: str) -> List[Dict]:
        """Get all actions performed on a resource"""
        return [entry for entry in self.audit_log if entry['resource'] == resource]
    
    def get_actions_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get actions within a date range"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        return [
            entry for entry in self.audit_log
            if start <= datetime.fromisoformat(entry['timestamp']) <= end
        ]
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Implementation depends on web framework
        return "127.0.0.1"
```

### Configuration Management

```python
# config_management.py
import json
import yaml
from typing import Dict, Any

class ConfigurationManagement:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a configuration setting"""
        self.config[key] = value
        self.save_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'dashboard': {
                'title': 'Ensemble Management Dashboard',
                'theme': 'light',
                'refresh_interval': 300
            },
            'alerts': {
                'low_enrollment_threshold': 4,
                'critical_enrollment_rate': 25,
                'email_notifications': True
            },
            'export': {
                'default_format': 'csv',
                'include_timestamp': True,
                'max_file_size': 10485760
            },
            'security': {
                'session_timeout': 28800,
                'max_login_attempts': 5,
                'password_expiry_days': 90
            }
        }
    
    def export_config(self, format: str = 'json') -> str:
        """Export configuration in specified format"""
        if format == 'yaml':
            return yaml.dump(self.config, default_flow_style=False)
        else:
            return json.dumps(self.config, indent=2)
    
    def import_config(self, config_data: str, format: str = 'json'):
        """Import configuration from string"""
        if format == 'yaml':
            self.config = yaml.safe_load(config_data)
        else:
            self.config = json.loads(config_data)
        
        self.save_config()
```

## 🔒 Compliance & Security

### Data Privacy Compliance

```python
# privacy_compliance.py
from typing import Dict, List
import hashlib

class PrivacyCompliance:
    def __init__(self):
        self.pii_fields = [
            'student_id', 'email', 'phone', 'address',
            'social_security_number', 'date_of_birth'
        ]
    
    def anonymize_data(self, data: Dict) -> Dict:
        """Anonymize personally identifiable information"""
        anonymized = data.copy()
        
        for field in self.pii_fields:
            if field in anonymized:
                anonymized[field] = self._hash_value(anonymized[field])
        
        return anonymized
    
    def _hash_value(self, value: str) -> str:
        """Hash a value for anonymization"""
        return hashlib.sha256(value.encode()).hexdigest()[:8]
    
    def check_data_retention(self, data_age_days: int) -> bool:
        """Check if data should be retained based on retention policy"""
        max_retention_days = 2555  # 7 years
        return data_age_days <= max_retention_days
    
    def generate_privacy_report(self) -> Dict:
        """Generate privacy compliance report"""
        return {
            'data_retention_policy': '7 years',
            'pii_fields_handled': self.pii_fields,
            'anonymization_enabled': True,
            'audit_trail_enabled': True,
            'access_controls_enabled': True
        }
```

### Security Monitoring

```python
# security_monitoring.py
import logging
from datetime import datetime, timedelta
from typing import List, Dict

class SecurityMonitoring:
    def __init__(self):
        self.security_log = []
        self.suspicious_activities = []
        self.blocked_ips = set()
    
    def log_login_attempt(self, user_id: str, ip_address: str, 
                         success: bool, user_agent: str):
        """Log login attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'login_attempt',
            'user_id': user_id,
            'ip_address': ip_address,
            'success': success,
            'user_agent': user_agent
        }
        
        self.security_log.append(log_entry)
        
        if not success:
            self._check_suspicious_activity(ip_address, user_id)
    
    def log_data_access(self, user_id: str, resource: str, 
                       action: str, ip_address: str):
        """Log data access"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'data_access',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'ip_address': ip_address
        }
        
        self.security_log.append(log_entry)
    
    def _check_suspicious_activity(self, ip_address: str, user_id: str):
        """Check for suspicious activity patterns"""
        recent_attempts = [
            entry for entry in self.security_log
            if entry['ip_address'] == ip_address
            and entry['event_type'] == 'login_attempt'
            and not entry['success']
            and datetime.fromisoformat(entry['timestamp']) > 
            datetime.now() - timedelta(minutes=15)
        ]
        
        if len(recent_attempts) >= 5:
            self.blocked_ips.add(ip_address)
            self.suspicious_activities.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'multiple_failed_logins',
                'ip_address': ip_address,
                'user_id': user_id,
                'attempts': len(recent_attempts)
            })
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def get_security_report(self) -> Dict:
        """Generate security report"""
        recent_logs = [
            entry for entry in self.security_log
            if datetime.fromisoformat(entry['timestamp']) > 
            datetime.now() - timedelta(days=7)
        ]
        
        return {
            'total_events': len(recent_logs),
            'failed_logins': len([
                entry for entry in recent_logs
                if entry['event_type'] == 'login_attempt' and not entry['success']
            ]),
            'suspicious_activities': len(self.suspicious_activities),
            'blocked_ips': len(self.blocked_ips),
            'data_access_events': len([
                entry for entry in recent_logs
                if entry['event_type'] == 'data_access'
            ])
        }
```

## 🗺️ Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Authentication system implementation
- [ ] Basic user management
- [ ] Role-based access control
- [ ] Audit trail system

### Phase 2: Analytics (Weeks 3-4)
- [ ] Advanced analytics implementation
- [ ] Predictive modeling
- [ ] Enhanced visualizations
- [ ] Reporting system

### Phase 3: Integration (Weeks 5-6)
- [ ] SIS integration
- [ ] Email notifications
- [ ] Export enhancements
- [ ] Configuration management

### Phase 4: Security & Compliance (Weeks 7-8)
- [ ] Security monitoring
- [ ] Privacy compliance
- [ ] Data retention policies
- [ ] Security testing

### Phase 5: Deployment & Testing (Weeks 9-10)
- [ ] Production deployment
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Documentation completion

## 📞 Support & Implementation

For implementation support:
- **Technical Lead**: [Your Name]
- **Email**: [your-email@institution.edu]
- **Department**: Music Department
- **Institution**: [Your Institution]

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Compatibility**: Python 3.8+, Streamlit 1.32.0+ 