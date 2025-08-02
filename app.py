"""
Main Streamlit application for Gini Inequality Visualizer.

This module orchestrates the application flow, coordinates data fetching,
processing, and visualization components, and handles comprehensive error
handling and user feedback mechanisms.
"""

import streamlit as st
import pandas as pd
import logging
from typing import Optional, Dict, Any

# Import application components
from utils.data_service import (
    WorldBankClient, WorldBankAPIError, APIConnectionError, 
    APIRateLimitError, DataNotAvailableError, InvalidCountryError
)
from utils.visualization import create_gini_line_plot, create_gini_table
from utils.ui_components import (
    render_sidebar, render_main_dashboard, show_loading_state, 
    show_error_message, show_welcome_message, display_data_summary
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_session_state():
    """
    Initialize Streamlit session state variables for application state management.
    
    Session state persists across Streamlit reruns and allows us to maintain
    application state, cache data, and track user interactions.
    """
    # Generate unique session ID for debugging and logging
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    # Track whether countries data has been loaded from API
    if 'countries_loaded' not in st.session_state:
        st.session_state.countries_loaded = False
    
    # Store the list of available countries from World Bank API
    if 'countries_data' not in st.session_state:
        st.session_state.countries_data = []
    
    # Track currently selected country (ISO code)
    if 'selected_country_code' not in st.session_state:
        st.session_state.selected_country_code = None
    
    # Track currently selected country (display name)
    if 'selected_country_name' not in st.session_state:
        st.session_state.selected_country_name = None
    
    # Store Gini data for the selected country
    if 'gini_data' not in st.session_state:
        st.session_state.gini_data = pd.DataFrame()
    
    # Track loading state for UI feedback
    if 'data_loading' not in st.session_state:
        st.session_state.data_loading = False
    
    # Store last error message for user feedback
    if 'last_error' not in st.session_state:
        st.session_state.last_error = None
    
    # Track error count for debugging
    if 'error_count' not in st.session_state:
        st.session_state.error_count = 0
    
    # Application-level cache for performance optimization
    if 'cache' not in st.session_state:
        st.session_state.cache = {}


def load_countries_data(client: WorldBankClient) -> bool:
    """
    Load countries data from World Bank API with error handling.
    
    Args:
        client: WorldBankClient instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not st.session_state.countries_loaded:
            with st.spinner("Loading countries data..."):
                countries = client.get_countries_dict()
                st.session_state.countries_data = countries
                st.session_state.countries_loaded = True
                logger.info(f"Successfully loaded {len(countries)} countries")
        return True
        
    except APIConnectionError as e:
        error_msg = f"Connection issue loading countries: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(str(e), "error")
        return False
        
    except APIRateLimitError as e:
        error_msg = f"Rate limit exceeded loading countries: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(str(e), "warning")
        return False
        
    except DataNotAvailableError as e:
        error_msg = f"No countries data available: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(str(e), "warning")
        return False
        
    except WorldBankAPIError as e:
        error_msg = f"Failed to load countries data: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(error_msg, "error")
        return False
        
    except Exception as e:
        error_msg = f"Unexpected error loading countries: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(error_msg, "error")
        return False


def load_gini_data(client: WorldBankClient, country_code: str, country_name: str) -> bool:
    """
    Load Gini data for selected country with comprehensive error handling.
    
    Args:
        client: WorldBankClient instance
        country_code: ISO country code
        country_name: Country display name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        st.session_state.data_loading = True
        
        with st.spinner(f"Loading Gini data for {country_name}..."):
            # Fetch Gini data with extended time range
            gini_df = client.get_gini_data(country_code, start_year=1990, end_year=2023)
            
            st.session_state.gini_data = gini_df
            st.session_state.selected_country_code = country_code
            st.session_state.selected_country_name = country_name
            st.session_state.last_error = None
            
            logger.info(f"Successfully loaded {len(gini_df)} Gini data points for {country_name}")
            return True
            
    except APIConnectionError as e:
        error_msg = f"Connection issue loading data for {country_name}: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(str(e), "error")
        return False
        
    except APIRateLimitError as e:
        error_msg = f"Rate limit exceeded for {country_name}: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(str(e), "warning")
        return False
        
    except DataNotAvailableError as e:
        error_msg = f"No data available for {country_name}: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(str(e), "info")
        return False
        
    except InvalidCountryError as e:
        error_msg = f"Invalid country selection {country_name}: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(str(e), "warning")
        return False
        
    except WorldBankAPIError as e:
        error_msg = f"Failed to load Gini data for {country_name}: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(error_msg, "error")
        return False
        
    except ValueError as e:
        error_msg = f"Invalid data for {country_name}: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(error_msg, "warning")
        return False
        
    except Exception as e:
        error_msg = f"Unexpected error loading Gini data for {country_name}: {str(e)}"
        logger.error(error_msg)
        st.session_state.last_error = error_msg
        show_error_message(error_msg, "error")
        return False
        
    finally:
        st.session_state.data_loading = False


def create_visualizations(data: pd.DataFrame, country_name: str) -> Optional[Dict[str, Any]]:
    """
    Create visualization components with error handling.
    
    Args:
        data: Gini data DataFrame
        country_name: Country display name
        
    Returns:
        Dictionary with visualization components or None if failed
    """
    try:
        if data.empty:
            logger.warning(f"No data available for visualization for {country_name}")
            return None
        
        # Create line plot
        line_plot = create_gini_line_plot(data, country_name)
        
        # Create formatted table
        data_table = create_gini_table(data)
        
        return {
            'line_plot': line_plot,
            'data_table': data_table
        }
        
    except Exception as e:
        error_msg = f"Error creating visualizations for {country_name}: {str(e)}"
        logger.error(error_msg)
        show_error_message(error_msg, "error")
        return None


def handle_country_selection(client: WorldBankClient, countries_data: list) -> None:
    """
    Handle country selection and coordinate data loading with comprehensive validation.
    
    Args:
        client: WorldBankClient instance
        countries_data: List of available countries
    """
    # Validate countries_data input
    if not countries_data or not isinstance(countries_data, list):
        logger.error("Invalid countries_data provided to handle_country_selection")
        st.error("❌ Invalid countries data. Please refresh the page.")
        return
    
    # Render sidebar and get selected country
    selected_country_code = render_sidebar(countries_data)
    
    # Handle country selection change
    if selected_country_code and selected_country_code != st.session_state.selected_country_code:
        # Validate country code format
        if not selected_country_code.isalpha() or len(selected_country_code) != 3:
            logger.warning(f"Invalid country code format: {selected_country_code}")
            st.error(f"❌ Invalid country code format: {selected_country_code}")
            return
        
        # Find country name with validation
        selected_country = next(
            (c for c in countries_data if c.get('code') == selected_country_code), 
            None
        )
        
        if selected_country and selected_country.get('name'):
            country_name = selected_country['name']
            
            # Additional validation for country name
            if not country_name.strip():
                logger.error(f"Empty country name for code: {selected_country_code}")
                st.error("❌ Invalid country data. Please try selecting a different country.")
                return
            
            logger.info(f"User selected country: {country_name} ({selected_country_code})")
            
            # Load Gini data for selected country
            success = load_gini_data(client, selected_country_code, country_name)
            
            if success:
                st.rerun()  # Refresh the app to show new data
        else:
            # Country not found in the list
            logger.error(f"Selected country code {selected_country_code} not found in countries list")
            st.error(
                f"❌ **Country not found**: {selected_country_code}\n\n"
                "This shouldn't happen with the dropdown selection. Please:\n"
                "- Refresh the page\n"
                "- Select a country from the dropdown menu only"
            )
    
    elif selected_country_code is None:
        # Clear selection if no country selected
        if st.session_state.selected_country_code is not None:
            logger.info("Clearing country selection")
            st.session_state.selected_country_code = None
            st.session_state.selected_country_name = None
            st.session_state.gini_data = pd.DataFrame()
            st.session_state.last_error = None  # Clear any previous errors


def render_main_content():
    """Render the main content area based on application state."""
    if st.session_state.selected_country_code and not st.session_state.gini_data.empty:
        # Country selected with data - show dashboard
        country_name = st.session_state.selected_country_name
        data = st.session_state.gini_data
        
        # Create visualizations
        visualizations = create_visualizations(data, country_name)
        
        if visualizations:
            # Render main dashboard with chart
            render_main_dashboard(
                data=data,
                country_name=country_name,
                chart_figure=visualizations['line_plot']
            )
            
            # Add data insights
            display_data_summary(data, country_name)
        else:
            st.error("Failed to create visualizations. Please try selecting a different country.")
            
    elif st.session_state.selected_country_code and st.session_state.gini_data.empty:
        # Country selected but no data available
        country_name = st.session_state.selected_country_name or st.session_state.selected_country_code
        st.warning(f"No Gini coefficient data available for **{country_name}**.")
        st.info(
            "This could be because:\n"
            "- The World Bank doesn't have Gini data for this country\n"
            "- Data is not available for the selected time period\n"
            "- There was an issue fetching the data\n\n"
            "Try selecting a different country from the sidebar."
        )
        
    else:
        # No country selected - show welcome message
        show_welcome_message()


def validate_application_state() -> bool:
    """
    Validate the current application state and handle edge cases.
    
    This function performs comprehensive validation of the session state to ensure
    the application is in a consistent state. It checks for missing keys, validates
    data structures, and handles corruption scenarios gracefully.
    
    Returns:
        True if application state is valid, False otherwise
    """
    # Define required session state keys for application functionality
    required_keys = [
        'countries_loaded', 'countries_data', 'selected_country_code',
        'selected_country_name', 'gini_data', 'data_loading', 'last_error'
    ]
    
    # Check for missing session state keys (indicates corruption or initialization failure)
    for key in required_keys:
        if key not in st.session_state:
            logger.error(f"Missing session state key: {key}")
            st.error(f"❌ Application state corrupted. Please refresh the page.")
            return False
    
    # Validate countries data structure
    if st.session_state.countries_loaded and st.session_state.countries_data:
        if not isinstance(st.session_state.countries_data, list):
            logger.error("countries_data is not a list")
            st.session_state.countries_loaded = False
            st.session_state.countries_data = []
            return False
        
        # Check for valid country data structure
        valid_countries = 0
        for country in st.session_state.countries_data:
            if isinstance(country, dict) and 'code' in country and 'name' in country:
                valid_countries += 1
        
        if valid_countries == 0:
            logger.error("No valid countries in countries_data")
            st.session_state.countries_loaded = False
            st.session_state.countries_data = []
            return False
    
    # Validate selected country consistency
    if st.session_state.selected_country_code and not st.session_state.selected_country_name:
        logger.warning("Selected country code without name - clearing selection")
        st.session_state.selected_country_code = None
        st.session_state.gini_data = pd.DataFrame()
    
    # Validate Gini data structure
    if not st.session_state.gini_data.empty:
        required_columns = ['year', 'value']
        if not all(col in st.session_state.gini_data.columns for col in required_columns):
            logger.error("Invalid Gini data structure - missing required columns")
            st.session_state.gini_data = pd.DataFrame()
            st.session_state.selected_country_code = None
            st.session_state.selected_country_name = None
    
    return True


def display_app_status():
    """Display comprehensive application status and debug information in sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.subheader("📊 App Status")
        
        # Show connection status
        if st.session_state.countries_loaded:
            country_count = len(st.session_state.countries_data)
            st.success(f"✅ Connected ({country_count} countries)")
            
            # Show data quality info
            if country_count < 50:  # Expect at least 50 countries
                st.warning(f"⚠️ Low country count: {country_count}")
        else:
            st.error("❌ Not connected to World Bank API")
            if st.button("🔄 Retry Connection"):
                st.session_state.countries_loaded = False
                st.session_state.countries_data = []
                st.rerun()
        
        # Show data status
        if st.session_state.selected_country_code:
            data_count = len(st.session_state.gini_data)
            if data_count > 0:
                st.info(f"📊 {data_count} data points loaded")
                
                # Show data range
                if not st.session_state.gini_data.empty:
                    min_year = st.session_state.gini_data['year'].min()
                    max_year = st.session_state.gini_data['year'].max()
                    st.caption(f"Data range: {min_year}-{max_year}")
            else:
                st.warning("⚠️ No data available for selected country")
        
        # Show loading status
        if st.session_state.data_loading:
            st.info("⏳ Loading data...")
        
        # Show last error if any
        if st.session_state.last_error:
            with st.expander("🔍 Debug Info", expanded=False):
                st.error(st.session_state.last_error)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Clear Error", key="clear_error"):
                        st.session_state.last_error = None
                        st.rerun()
                
                with col2:
                    if st.button("Reset App", key="reset_app"):
                        # Reset all session state
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
        
        # Add system info
        with st.expander("ℹ️ System Info", expanded=False):
            st.caption(f"Session ID: {st.session_state.get('session_id', 'Unknown')}")
            st.caption(f"Cache size: {len(st.session_state.get('cache', {}))}")
            
            # Show memory usage of session state
            import sys
            total_size = sum(sys.getsizeof(v) for v in st.session_state.values())
            st.caption(f"Session size: {total_size:,} bytes")


def main():
    """
    Main application entry point with comprehensive orchestration.
    
    This function coordinates all application components:
    - Streamlit page configuration and layout
    - Application state management for country selection
    - Data fetching, processing, and visualization coordination
    - Comprehensive error handling and user feedback mechanisms
    """
    # Streamlit page configuration
    st.set_page_config(
        page_title="Gini Inequality Visualizer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/worldbank/data',
            'Report a bug': None,
            'About': "Gini Inequality Visualizer - Explore income inequality trends using World Bank data"
        }
    )
    
    # Initialize session state for application state management
    initialize_session_state()
    
    # Validate application state and handle edge cases
    if not validate_application_state():
        st.stop()
    
    # Initialize World Bank API client with error handling
    try:
        client = WorldBankClient()
        logger.info("WorldBankClient initialized successfully")
    except Exception as e:
        error_msg = f"Failed to initialize data client: {str(e)}"
        logger.error(error_msg)
        st.error(
            f"❌ **Initialization Error**\n\n"
            f"{error_msg}\n\n"
            "**What you can do:**\n"
            "- 🔄 Refresh the page\n"
            "- 🌐 Check your internet connection\n"
            "- ⏳ Try again in a few moments"
        )
        st.stop()
    
    # Load countries data on first run
    countries_loaded = load_countries_data(client)
    
    if countries_loaded and st.session_state.countries_data:
        # Handle country selection and coordinate data loading
        handle_country_selection(client, st.session_state.countries_data)
        
        # Render main content based on application state
        render_main_content()
        
        # Display application status in sidebar
        display_app_status()
        
    else:
        # Failed to load countries - show comprehensive error state
        st.error(
            "❌ **Unable to Load Application Data**\n\n"
            "The application cannot connect to the World Bank API to load country data.\n\n"
            "**What you can do:**\n"
            "- 🌐 Check your internet connection\n"
            "- 🔄 Click the retry button below\n"
            "- ⏳ Wait a few moments and refresh the page\n"
            "- 🔍 Check if the World Bank API is accessible from your network"
        )
        
        # Show error details if available
        if st.session_state.last_error:
            with st.expander("🔍 Technical Details"):
                st.code(st.session_state.last_error)
        
        # Provide retry options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Retry Connection", type="primary"):
                st.session_state.countries_loaded = False
                st.session_state.countries_data = []
                st.session_state.last_error = None
                st.session_state.error_count = 0
                st.rerun()
        
        with col2:
            if st.button("🔧 Reset Application"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        with col3:
            if st.button("📊 Test Connection"):
                # Test basic connectivity
                try:
                    import requests
                    response = requests.get("https://api.worldbank.org/v2/country", timeout=10)
                    if response.status_code == 200:
                        st.success("✅ World Bank API is accessible")
                    else:
                        st.error(f"❌ API returned status code: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Connection test failed: {str(e)}")
        
        # Show alternative options
        st.info(
            "**Alternative Options:**\n"
            "- Try accessing the app from a different network\n"
            "- Check if your firewall or proxy is blocking the connection\n"
            "- The World Bank API may be temporarily unavailable"
        )
    
    # Add footer with data source information
    st.markdown("---")
    st.markdown(
        "**Data Source:** [World Bank Open Data](https://data.worldbank.org/) | "
        "**Indicator:** SI.POV.GINI (Gini Index) | "
        "**Last Updated:** Real-time via World Bank API"
    )


if __name__ == "__main__":
    main()