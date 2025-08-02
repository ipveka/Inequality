"""
UI components module for Streamlit interface elements.

This module contains reusable UI components and layout management
functions for the Streamlit application.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Optional
import time


def render_sidebar(countries: List[Dict[str, str]]) -> Optional[str]:
    """
    Create country selection sidebar with comprehensive validation and error handling.
    
    Args:
        countries: List of country dictionaries with 'code' and 'name' keys
        
    Returns:
        Selected country code or None
    """
    with st.sidebar:
        st.header("🌍 Country Selection")
        
        # Handle empty or invalid countries list
        if not countries:
            st.error("❌ **No countries available**")
            st.info(
                "**Possible causes:**\n"
                "- Connection issue with World Bank API\n"
                "- Service temporarily unavailable\n\n"
                "**Try:**\n"
                "- Refresh the page\n"
                "- Check your internet connection"
            )
            
            # Add retry button
            if st.button("🔄 Retry Loading Countries"):
                st.rerun()
            
            return None
        
        # Validate and filter countries data structure
        # This ensures we only display countries with valid code and name
        valid_countries = []
        for country in countries:
            # Check if country is a dictionary with required keys
            if isinstance(country, dict) and 'code' in country and 'name' in country:
                # Ensure both code and name are non-empty strings
                if country['code'] and country['name']:  
                    valid_countries.append(country)
                else:
                    # Log invalid entries for debugging but don't overwhelm UI
                    st.warning(f"⚠️ Skipping invalid country data: {country}")
        
        # Handle case where all countries were filtered out
        if not valid_countries:
            st.error("❌ **No valid countries found**")
            st.info("The countries data appears to be corrupted. Please refresh the page.")
            return None
        
        # Show data quality info
        if len(valid_countries) != len(countries):
            st.warning(f"⚠️ Filtered out {len(countries) - len(valid_countries)} invalid entries")
        
        st.success(f"✅ {len(valid_countries)} countries available")
        
        # Create options for selectbox - display country names but return codes
        # First option is a placeholder to force user selection
        country_options = ["Select a country..."] + [
            f"{country['name']}" for country in valid_countries
        ]
        
        # Create reverse mapping to convert display name back to country code
        # This allows us to show user-friendly names while working with ISO codes internally
        name_to_code = {country['name']: country['code'] for country in valid_countries}
        
        # Add search functionality hint
        st.caption("💡 Tip: You can type to search for countries")
        
        selected_display = st.selectbox(
            "Choose a country to analyze:",
            options=country_options,
            index=0,
            help="Select a country to view its Gini coefficient data over time. "
                 "Countries with better data coverage include USA, Germany, Brazil, and most European nations."
        )
        
        # Validate and return country code if valid selection made
        if selected_display != "Select a country...":
            selected_code = name_to_code.get(selected_display)
            
            # Additional validation
            if not selected_code:
                st.error(f"❌ Invalid country selection: {selected_display}")
                return None
            
            # Show additional country info if available
            selected_country = next(
                (c for c in valid_countries if c['code'] == selected_code), 
                None
            )
            
            if selected_country:
                # Display country information
                if selected_country.get('region'):
                    st.info(f"**Region:** {selected_country['region']}")
                
                # Show data availability hint
                st.caption(f"🔍 Loading Gini data for {selected_country['name']}...")
                
                return selected_code
            else:
                st.error(f"❌ Country data not found for: {selected_display}")
                return None
        
        # Show helpful information when no country is selected
        with st.expander("ℹ️ About Country Data"):
            st.markdown("""
            **Data Source:** World Bank Open Data
            
            **Countries with good Gini data coverage:**
            - 🇺🇸 United States
            - 🇩🇪 Germany  
            - 🇧🇷 Brazil
            - 🇫🇷 France
            - 🇬🇧 United Kingdom
            - 🇮🇹 Italy
            - 🇯🇵 Japan
            
            **Note:** Some countries may have limited or no Gini coefficient data available.
            """)
        
        return None


def render_main_dashboard(data: pd.DataFrame, country_name: str, chart_figure: Optional[go.Figure] = None) -> None:
    """
    Display charts and tables in the main dashboard area.
    
    Args:
        data: Gini data DataFrame
        country_name: Name of selected country
        chart_figure: Optional pre-generated plotly figure
    """
    # Main title
    st.title("📊 Gini Inequality Visualizer")
    st.markdown("---")
    
    if data.empty:
        st.warning(f"No Gini coefficient data available for **{country_name}**.")
        st.info(
            "This could be because:\n"
            "- The World Bank doesn't have Gini data for this country\n"
            "- Data is not available for the selected time period\n"
            "- There was an issue fetching the data"
        )
        return
    
    # Country header with summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        latest_year = data['year'].max()
        latest_value = data[data['year'] == latest_year]['value'].iloc[0]
        st.metric(
            label="Latest Gini Coefficient",
            value=f"{latest_value:.2f}",
            help=f"Most recent data from {latest_year}"
        )
    
    with col2:
        data_range = f"{data['year'].min()} - {data['year'].max()}"
        st.metric(
            label="Data Range",
            value=data_range,
            help="Years covered by available data"
        )
    
    with col3:
        avg_value = data['value'].mean()
        st.metric(
            label="Average Gini",
            value=f"{avg_value:.2f}",
            help="Average across all available years"
        )
    
    st.markdown("---")
    
    # Chart section
    st.subheader(f"📈 Gini Coefficient Trend - {country_name}")
    
    if chart_figure:
        st.plotly_chart(chart_figure, use_container_width=True)
    else:
        st.error("Chart could not be generated.")
    
    # Add interpretation help
    with st.expander("ℹ️ Understanding the Gini Coefficient"):
        st.markdown("""
        The **Gini coefficient** measures income inequality within a country:
        
        - **0**: Perfect equality (everyone has the same income)
        - **100**: Perfect inequality (one person has all the income)
        
        **Typical ranges:**
        - **20-35**: Relatively equal distribution (Nordic countries)
        - **35-50**: Moderate inequality (most developed countries)
        - **50+**: High inequality (some developing countries)
        """)
    
    st.markdown("---")
    
    # Table section
    st.subheader(f"📋 Detailed Data - {country_name}")
    
    # Import and use the create_gini_table function for consistent formatting
    from .visualization import create_gini_table
    display_table = create_gini_table(data)
    
    # Check if table has data after filtering missing values
    if display_table.empty:
        st.warning("No valid data points available for table display after filtering missing values.")
    else:
        # Display table with professional styling
        st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Year": st.column_config.NumberColumn(
                    "Year",
                    help="Year of measurement",
                    format="%d",
                    width="small"
                ),
                "Gini Coefficient": st.column_config.NumberColumn(
                    "Gini Coefficient",
                    help="Gini coefficient value (0-100 scale)",
                    format="%.2f",
                    width="medium"
                )
            }
        )
        
        # Show data summary
        st.caption(f"Showing {len(display_table)} data points sorted chronologically (most recent first)")
    
        # Download option
        csv_data = display_table.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv_data,
            file_name=f"gini_data_{country_name.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            help="Download the data table as a CSV file"
        )


def show_loading_state(message: str = "Loading data...") -> None:
    """
    Display loading indicators during data fetching.
    
    Args:
        message: Custom loading message to display
    """
    with st.spinner(message):
        # Create a progress bar for visual feedback
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate loading progress (this would be replaced with actual progress tracking)
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 30:
                status_text.text("Connecting to World Bank API...")
            elif i < 60:
                status_text.text("Fetching country data...")
            elif i < 90:
                status_text.text("Processing data...")
            else:
                status_text.text("Finalizing...")
            time.sleep(0.01)  # Small delay for visual effect
        
        # Clear the progress indicators
        progress_bar.empty()
        status_text.empty()


def show_error_message(error: str, error_type: str = "error") -> None:
    """
    Handle error display with comprehensive user-friendly messages and guidance.
    
    Args:
        error: Error message to display
        error_type: Type of error ('error', 'warning', 'info')
    """
    # Map error types to appropriate Streamlit functions
    error_functions = {
        'error': st.error,
        'warning': st.warning,
        'info': st.info
    }
    
    error_func = error_functions.get(error_type, st.error)
    
    # Enhanced error handling with specific guidance
    if "connection" in error.lower() or "connect" in error.lower() or "timeout" in error.lower():
        error_func(
            f"🌐 **Connection Issue**\n\n"
            f"{error}\n\n"
            "**What you can do:**\n"
            "- ✅ Check your internet connection\n"
            "- 🔄 Try refreshing the page\n"
            "- ⏱️ Wait a few moments and try again\n"
            "- 🌍 The World Bank API might be temporarily unavailable\n\n"
            "If the problem persists, the service may be experiencing high traffic."
        )
    elif "rate limit" in error.lower():
        error_func(
            f"⏱️ **API Rate Limit Reached**\n\n"
            f"{error}\n\n"
            "**What this means:**\n"
            "The World Bank API has usage limits to ensure fair access for all users.\n\n"
            "**What you can do:**\n"
            "- ⏳ Wait 1-2 minutes before trying again\n"
            "- 🔄 The app will automatically retry\n"
            "- 📊 Previously loaded data is still available\n\n"
            "Thank you for your patience!"
        )
    elif "no data" in error.lower() or "not available" in error.lower() or "data not found" in error.lower():
        error_func(
            f"📊 **No Data Available**\n\n"
            f"{error}\n\n"
            "**Why this happens:**\n"
            "- 🏛️ The country hasn't reported Gini data to the World Bank\n"
            "- 📅 Data may not be available for the selected time period\n"
            "- 🔍 Some countries have limited economic data coverage\n\n"
            "**What you can do:**\n"
            "- 🌍 Try selecting a different country\n"
            "- 📈 Countries like USA, Germany, Brazil typically have good data coverage\n"
            "- 🔍 Check the sidebar for countries with available data"
        )
    elif "invalid country" in error.lower() or "not found" in error.lower():
        error_func(
            f"⚠️ **Invalid Country Selection**\n\n"
            f"{error}\n\n"
            "**What happened:**\n"
            "The selected country code is not recognized by the World Bank database.\n\n"
            "**What you can do:**\n"
            "- 🌍 Select a country from the dropdown menu in the sidebar\n"
            "- 🔄 Refresh the page if the country list didn't load properly\n"
            "- ✅ Only use countries from the provided dropdown list"
        )
    elif "server error" in error.lower() or "503" in error or "500" in error:
        error_func(
            f"🔧 **Service Temporarily Unavailable**\n\n"
            f"{error}\n\n"
            "**What's happening:**\n"
            "The World Bank API is experiencing technical difficulties.\n\n"
            "**What you can do:**\n"
            "- ⏳ Wait 5-10 minutes and try again\n"
            "- 🔄 Refresh the page\n"
            "- 📊 This is usually temporary and resolves quickly\n\n"
            "We apologize for the inconvenience!"
        )
    elif "json" in error.lower() or "format" in error.lower():
        error_func(
            f"🔧 **Data Format Issue**\n\n"
            f"{error}\n\n"
            "**What happened:**\n"
            "The API returned data in an unexpected format.\n\n"
            "**What you can do:**\n"
            "- 🔄 Try again - this is usually temporary\n"
            "- 🌍 Try selecting a different country\n"
            "- 📱 If the problem persists, please report this issue"
        )
    else:
        # Generic error with helpful guidance
        error_func(
            f"❌ **Unexpected Error**\n\n"
            f"{error}\n\n"
            "**What you can do:**\n"
            "- 🔄 Try refreshing the page\n"
            "- 🌍 Try selecting a different country\n"
            "- ⏳ Wait a moment and try again\n"
            "- 📱 If the problem persists, this may be a temporary service issue"
        )


def show_welcome_message() -> None:
    """Display welcome message when no country is selected."""
    st.title("📊 Gini Inequality Visualizer")
    
    st.markdown("""
    Welcome to the **Gini Inequality Visualizer**! This application helps you explore income inequality 
    trends across different countries using the Gini coefficient.
    
    ### 🚀 Getting Started
    1. **Select a country** from the sidebar dropdown
    2. **View the interactive chart** showing Gini trends over time
    3. **Examine detailed data** in the table below the chart
    4. **Download the data** for further analysis
    
    ### 📈 About the Gini Coefficient
    The Gini coefficient is a measure of income inequality within a country, ranging from 0 (perfect equality) 
    to 100 (perfect inequality). This data comes from the World Bank's comprehensive database.
    """)
    
    # Add some visual elements
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**📊 Interactive Charts**\nExplore trends with hover details and zoom functionality")
    
    with col2:
        st.info("**🌍 Global Data**\nAccess real-time data from the World Bank API")
    
    with col3:
        st.info("**📥 Export Ready**\nDownload data in CSV format for your analysis")
    
    st.markdown("---")
    st.markdown("👈 **Start by selecting a country from the sidebar!**")


def display_data_summary(data: pd.DataFrame, country_name: str) -> None:
    """
    Display a summary of the data trends and insights.
    
    Args:
        data: Gini data DataFrame
        country_name: Name of selected country
    """
    if data.empty:
        return
    
    st.subheader("📊 Data Insights")
    
    # Calculate trend
    if len(data) > 1:
        first_value = data.iloc[0]['value']
        last_value = data.iloc[-1]['value']
        change = last_value - first_value
        change_percent = (change / first_value) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            if change > 0:
                st.metric(
                    "Trend",
                    "Increasing Inequality",
                    f"+{change:.2f} points",
                    delta_color="inverse"
                )
            elif change < 0:
                st.metric(
                    "Trend",
                    "Decreasing Inequality", 
                    f"{change:.2f} points",
                    delta_color="normal"
                )
            else:
                st.metric("Trend", "Stable", "No change")
        
        with col2:
            st.metric(
                "Total Change",
                f"{change_percent:+.1f}%",
                f"From {data['year'].min()} to {data['year'].max()}"
            )
    
    # Show data quality info
    years_span = data['year'].max() - data['year'].min() + 1
    data_points = len(data)
    coverage = (data_points / years_span) * 100 if years_span > 0 else 0
    
    st.info(f"**Data Coverage**: {data_points} data points over {years_span} years ({coverage:.0f}% coverage)")