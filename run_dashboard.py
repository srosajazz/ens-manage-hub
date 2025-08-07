#!/usr/bin/env python3
"""
Ensemble Management Dashboard Launcher
This script checks dependencies and launches the Streamlit dashboard.
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'pandas', 'plotly', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
        return False

def check_data_file():
    """Check if the JSON data file exists"""
    data_file = 'Find_Ensembles_ with Open Seats_ _(RE).json'
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Please ensure the JSON file is in the same directory as this script.")
        return False
    return True

def main():
    print("🎵 Ensemble Management Dashboard Launcher")
    print("=" * 50)
    
    # Check if data file exists
    if not check_data_file():
        return
    
    # Check dependencies
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        response = input("Would you like to install them now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_dependencies():
                return
        else:
            print("Please install the missing packages manually:")
            print("pip install -r requirements.txt")
            return
    
    print("✅ All dependencies are installed!")
    print("🚀 Starting the dashboard...")
    print("📱 The dashboard will open in your browser automatically.")
    print("🔗 If it doesn't open, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the dashboard.")
    print("=" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

if __name__ == "__main__":
    main() 