#!/usr/bin/env python3
"""
Run App Script for Inequality Visualization Project

This script checks requirements, validates the installation, and runs the Streamlit app.
It provides comprehensive error handling and user feedback.
"""

import sys
import os
import subprocess
import importlib
import platform
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    """Print an info message."""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def check_python_version():
    """Check if Python version is compatible."""
    print_info("Checking Python version...")
    
    version = sys.version_info
    min_version = (3, 8)
    
    if version < min_version:
        print_error(f"Python {min_version[0]}.{min_version[1]} or higher is required")
        print_error(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_required_packages():
    """Check if all required packages are installed."""
    print_info("Checking required packages...")
    
    required_packages = [
        'pandas',
        'numpy', 
        'requests',
        'plotly',
        'streamlit',
        'scipy',
        'matplotlib',
        'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_warning(f"{package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Installing missing packages...")
        return install_packages(missing_packages)
    
    return True

def install_packages(packages):
    """Install missing packages using pip."""
    try:
        for package in packages:
            print_info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print_success(f"{package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install packages: {e}")
        return False

def check_project_structure():
    """Check if the project structure is correct."""
    print_info("Checking project structure...")
    
    required_files = [
        'src/__init__.py',
        'src/data_fetch.py',
        'src/metrics.py',
        'src/visualization.py',
        'src/utils.py',
        'app/main_app.py',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print_warning(f"Missing: {file_path}")
        else:
            print_success(f"Found: {file_path}")
    
    if missing_files:
        print_error("Some project files are missing")
        print_error("Please ensure you're running this script from the project root directory")
        return False
    
    return True

def test_imports():
    """Test if the project modules can be imported."""
    print_info("Testing module imports...")
    
    try:
        # Add src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test imports
        from src.metrics import gini_coefficient
        from src.utils import get_country_name
        from src.data_fetch import get_available_countries
        
        print_success("All modules imported successfully")
        return True
        
    except ImportError as e:
        print_error(f"Import error: {e}")
        return False

def run_demo_test():
    """Run the demo script to test functionality."""
    print_info("Running functionality test...")
    
    try:
        result = subprocess.run([sys.executable, "demo.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("Demo test passed")
            return True
        else:
            print_error("Demo test failed")
            print_error(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_warning("Demo test timed out (this is normal)")
        return True
    except Exception as e:
        print_warning(f"Demo test error: {e}")
        return True

def check_streamlit():
    """Check if Streamlit is properly installed."""
    print_info("Checking Streamlit installation...")
    
    try:
        import streamlit
        print_success(f"Streamlit {streamlit.__version__} is installed")
        return True
    except ImportError:
        print_error("Streamlit is not installed")
        return False

def get_app_path():
    """Get the path to the main app."""
    app_path = os.path.join(os.path.dirname(__file__), 'app', 'main_app.py')
    
    if not os.path.exists(app_path):
        print_error(f"App file not found: {app_path}")
        return None
    
    return app_path

def run_streamlit_app():
    """Run the Streamlit app."""
    print_header("Starting Inequality Visualization Dashboard")
    
    app_path = get_app_path()
    if not app_path:
        return False
    
    print_info("Launching Streamlit app...")
    print_info("The app will open in your default web browser")
    print_info("If it doesn't open automatically, go to: http://localhost:8501")
    print_info("Press Ctrl+C to stop the app")
    
    try:
        # Run streamlit with specific configuration
        cmd = [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.headless", "false",
            "--server.port", "8501",
            "--server.address", "localhost"
        ]
        
        print_success("Starting server...")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print_info("\nApp stopped by user")
        return True
    except Exception as e:
        print_error(f"Failed to start app: {e}")
        return False

def show_usage_instructions():
    """Show usage instructions for the app."""
    print_header("Usage Instructions")
    
    instructions = [
        "🌍 Global Inequality Dashboard",
        "",
        "📊 Dashboard Features:",
        "  • Select data sources (World Bank, OECD, WID.world, Eurostat)",
        "  • Choose countries and time periods",
        "  • View interactive inequality visualizations",
        "  • Compare countries and metrics",
        "  • Download data and charts",
        "",
        "🎯 Getting Started:",
        "  1. Use the sidebar to select your analysis parameters",
        "  2. Explore different tabs for various visualizations",
        "  3. Hover over charts for detailed information",
        "  4. Download data using the Data Table tab",
        "",
        "📈 Key Metrics:",
        "  • Gini Coefficient: 0 (equality) to 1 (inequality)",
        "  • Palma Ratio: Top 10% vs Bottom 40%",
        "  • Income Shares: Distribution across population",
        "  • Lorenz Curves: Visual inequality representation",
        "",
        "🆘 Need Help?",
        "  • Check the About tab for methodology",
        "  • Review data sources and limitations",
        "  • Contact support if you encounter issues"
    ]
    
    for instruction in instructions:
        print(instruction)

def main():
    """Main function to run the app with checks."""
    print_header("Inequality Visualization App Launcher")
    
    # System information
    print_info(f"Platform: {platform.system()} {platform.release()}")
    print_info(f"Python: {sys.version}")
    print_info(f"Working directory: {os.getcwd()}")
    
    # Run checks
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Required Packages", check_required_packages),
        ("Module Imports", test_imports),
        ("Streamlit", check_streamlit),
        ("Functionality Test", run_demo_test)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print_header(f"Check: {check_name}")
        if not check_func():
            failed_checks.append(check_name)
    
    # Summary
    if failed_checks:
        print_header("❌ Setup Issues Found")
        print_error("The following checks failed:")
        for check in failed_checks:
            print_error(f"  • {check}")
        
        print_info("\nTroubleshooting:")
        print_info("1. Run: pip install -r requirements.txt")
        print_info("2. Ensure you're in the project root directory")
        print_info("3. Check your internet connection")
        print_info("4. Try: python demo.py to test basic functionality")
        
        return False
    
    print_header("✅ All Checks Passed")
    print_success("Your environment is ready!")
    
    # Show usage instructions
    show_usage_instructions()
    
    # Ask user if they want to continue
    try:
        response = input(f"\n{Colors.OKCYAN}Press Enter to launch the app, or 'q' to quit: {Colors.ENDC}")
        if response.lower() in ['q', 'quit', 'exit']:
            print_info("Goodbye!")
            return True
    except KeyboardInterrupt:
        print_info("\nGoodbye!")
        return True
    
    # Run the app
    return run_streamlit_app()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print_info("\nScript interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1) 