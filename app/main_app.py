"""
Main Streamlit application for the Inequality Visualization Dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.data_fetch import (
    fetch_world_bank_gini, 
    fetch_oecd_data, 
    fetch_wid_data, 
    fetch_eurostat_data,
    get_available_countries,
    fetch_all_sources_data
)
from src.data_cleaning import clean_inequality_data, merge_data_sources
from src.metrics import gini_coefficient, palma_ratio, income_shares, lorenz_curve_data
from src.visualization import (
    plot_lorenz_curve,
    plot_gini_by_country,
    plot_income_shares,
    plot_inequality_trends,
    plot_country_comparison,
    plot_inequality_distribution,
    create_dashboard_summary
)
from src.utils import (
    get_country_name,
    get_country_code,
    validate_year_range,
    format_number,
    get_continent_mapping,
    filter_by_continent,
    get_metric_description
)

# Page configuration
st.set_page_config(
    page_title="Global Inequality Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: #1f77b4;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .metric-card h2 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    
    .sidebar-header {
        font-size: 1.5rem;
        color: #1f77b4;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Section headers */
    h2 {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_available_countries():
    """Load available countries for the app."""
    return get_available_countries()

@st.cache_data
def load_continent_mapping():
    """Load continent mapping."""
    return get_continent_mapping()

@st.cache_data
def fetch_cached_data(country_code: str, start_year: int, end_year: int):
    """Fetch and cache data for a specific country and time range."""
    try:
        return fetch_all_sources_data(country_code, start_year, end_year)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return {}

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🌍 Global Inequality Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">📋 Controls</h2>', unsafe_allow_html=True)
        
        # Data source selection
        st.subheader("Data Sources")
        data_sources = st.multiselect(
            "Select data sources:",
            ["World Bank", "OECD", "WID.world", "Eurostat"],
            default=["World Bank", "OECD"]
        )
        
        # Continent filter
        st.subheader("Geographic Filter")
        continent_mapping = load_continent_mapping()
        continent = st.selectbox(
            "Select continent:",
            ["All Continents"] + list(continent_mapping.keys())
        )
        
        # Country selection
        available_countries = load_available_countries()
        if continent != "All Continents":
            continent_countries = continent_mapping.get(continent, [])
            available_countries = [c for c in available_countries if c in continent_countries]
        
        # Set Spain as default country
        default_country_index = available_countries.index("ESP") if "ESP" in available_countries else 0
        
        country_code = st.selectbox(
            "Select country:",
            available_countries,
            index=default_country_index,
            format_func=lambda x: f"{x} - {get_country_name(x)}"
        )
        
        # Year range
        st.subheader("Time Period")
        current_year = datetime.now().year
        start_year, end_year = st.slider(
            "Select year range:",
            min_value=1960,
            max_value=current_year,
            value=(2010, current_year)
        )
        
        # Metrics selection
        st.subheader("Metrics")
        selected_metrics = st.multiselect(
            "Select metrics to display:",
            ["Gini Coefficient", "Palma Ratio", "Income Shares", "Lorenz Curve", "Trends"],
            default=["Gini Coefficient", "Income Shares", "Lorenz Curve"]
        )
        
        # Update button
        if st.button("🔄 Update Dashboard", type="primary"):
            st.rerun()
    
    # Main content
    if country_code:
        st.markdown(f"## 📊 Inequality Analysis for {get_country_name(country_code)}")
        
        # Fetch data
        with st.spinner("Fetching inequality data..."):
            all_data = fetch_cached_data(country_code, start_year, end_year)
        
        if not all_data:
            st.warning("No data available for the selected criteria. Please try different parameters.")
            return
        
        # Merge and clean data
        merged_data = merge_data_sources(all_data)
        if merged_data.empty:
            st.warning("No data available after merging sources.")
            return
        
        # Filter by year range
        merged_data = merged_data[
            (merged_data['year'] >= start_year) & 
            (merged_data['year'] <= end_year)
        ]
        
        if merged_data.empty:
            st.warning(f"No data available for {get_country_name(country_code)} between {start_year} and {end_year}")
            return
        
        # Display latest data summary
        latest_data = merged_data.loc[merged_data['year'].idxmax()]
        
        # Create metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'gini' in latest_data:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Gini Coefficient</h3>
                    <h2>{format_number(latest_data['gini'])}</h2>
                    <p>{get_metric_description('gini')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if 'palma_ratio' in latest_data:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Palma Ratio</h3>
                    <h2>{format_number(latest_data['palma_ratio'])}</h2>
                    <p>{get_metric_description('palma')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if 'top_10_share' in latest_data:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Top 10% Share</h3>
                    <h2>{format_number(latest_data['top_10_share'], 1)}%</h2>
                    <p>{get_metric_description('top_10_share')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if 'bottom_50_share' in latest_data:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Bottom 50% Share</h3>
                    <h2>{format_number(latest_data['bottom_50_share'], 1)}%</h2>
                    <p>{get_metric_description('bottom_50_share')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ============================================================================
        # 📈 TRENDS SECTION
        # ============================================================================
        st.markdown("## 📈 Inequality Trends Over Time")
        
        # Metric selection for trends
        trend_metric = st.selectbox(
            "Select metric for trend analysis:",
            ["gini", "palma_ratio", "top_10_share", "bottom_50_share"],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if trend_metric in merged_data.columns:
            fig_trends = plot_inequality_trends(
                merged_data, 
                [country_code], 
                trend_metric, 
                start_year, 
                end_year
            )
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.warning(f"Data for {trend_metric} not available")
        
        st.markdown("---")
        
        # ============================================================================
        # 📊 INCOME DISTRIBUTION SECTION
        # ============================================================================
        st.markdown("## 📊 Income Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Lorenz curve
            if "Lorenz Curve" in selected_metrics:
                st.subheader("Lorenz Curve")
                
                # Generate sample income data for Lorenz curve
                # In a real application, you would use actual income distribution data
                np.random.seed(42)
                sample_incomes = np.random.lognormal(mean=10, sigma=0.5, size=1000)
                sample_series = pd.Series(sample_incomes)
                
                fig_lorenz = plot_lorenz_curve(sample_series, f"Lorenz Curve - {get_country_name(country_code)}")
                st.plotly_chart(fig_lorenz, use_container_width=True)
        
        with col2:
            # Income shares
            if "Income Shares" in selected_metrics:
                st.subheader("Income Shares")
                fig_shares = plot_income_shares(merged_data, country_code, latest_data['year'])
                st.plotly_chart(fig_shares, use_container_width=True)
        
        st.markdown("---")
        
        # ============================================================================
        # 🌐 COUNTRY COMPARISON SECTION
        # ============================================================================
        st.markdown("## 🌐 Country Comparison")
        
        # Select countries to compare
        comparison_countries = st.multiselect(
            "Select countries to compare:",
            available_countries,
            default=[country_code],
            format_func=lambda x: f"{x} - {get_country_name(x)}"
        )
        
        if len(comparison_countries) >= 2:
            # Fetch data for comparison countries
            comparison_data = []
            for cc in comparison_countries:
                cc_data = fetch_cached_data(cc, start_year, end_year)
                if cc_data:
                    merged_cc_data = merge_data_sources(cc_data)
                    if not merged_cc_data.empty:
                        comparison_data.append(merged_cc_data)
            
            if comparison_data:
                all_comparison_data = pd.concat(comparison_data, ignore_index=True)
                
                # Gini comparison
                fig_gini_comp = plot_gini_by_country(all_comparison_data, latest_data['year'])
                st.plotly_chart(fig_gini_comp, use_container_width=True)
                
                # Radar chart comparison
                fig_radar = plot_country_comparison(
                    all_comparison_data, 
                    comparison_countries, 
                    latest_data['year']
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.warning("No comparison data available")
        else:
            st.info("Select at least 2 countries for comparison")
        
        st.markdown("---")
        
        # ============================================================================
        # 📋 DATA TABLE SECTION
        # ============================================================================
        st.markdown("## 📋 Data Table")
        
        # Display the data
        st.dataframe(
            merged_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = merged_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"inequality_data_{country_code}_{start_year}_{end_year}.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        
        # ============================================================================
        # 📚 DOCUMENTATION SECTION
        # ============================================================================
        st.markdown("## 📚 Documentation")
        
        st.markdown("""
        ### 📊 Inequality Metrics Guide
        
        #### Gini Coefficient
        The Gini coefficient is the most widely used measure of income inequality.
        - **Range**: 0 (perfect equality) to 1 (perfect inequality)
        - **Interpretation**: 
          - 0.0-0.3: Low inequality
          - 0.3-0.5: Moderate inequality  
          - 0.5-1.0: High inequality
        - **Formula**: G = (2 * Σ(i * x_i) - (n + 1) * Σ(x_i)) / (n * Σ(x_i))
        
        #### Palma Ratio
        The Palma ratio focuses on the extremes of the income distribution.
        - **Definition**: Ratio of richest 10% to poorest 40% of population
        - **Interpretation**: Values > 1 indicate inequality
        - **Advantage**: Less sensitive to middle-class changes than Gini
        
        #### Income Shares
        Shows the distribution of total income across population segments.
        - **Top 1% Share**: Percentage held by the wealthiest 1%
        - **Top 10% Share**: Percentage held by the wealthiest 10%
        - **Bottom 50% Share**: Percentage held by the poorest 50%
        
        #### Lorenz Curve
        Visual representation of income distribution.
        - **Perfect Equality**: Diagonal line from (0,0) to (1,1)
        - **Inequality**: Curve below the diagonal
        - **Gini**: Area between curve and diagonal line
        
        ### 🔬 Methodology
        
        #### Data Collection
        1. **World Bank API**: Automated fetching of Gini coefficients
        2. **OECD Database**: Income distribution statistics
        3. **WID.world**: Historical inequality data
        4. **Eurostat**: EU-specific indicators
        
        #### Data Processing
        - **Cleaning**: Remove duplicates, handle missing values
        - **Normalization**: Standardize country codes and formats
        - **Validation**: Check for logical consistency
        - **Merging**: Combine data from multiple sources
        
        #### Statistical Methods
        - **Percentile Calculations**: Using numpy percentile functions
        - **Cumulative Distributions**: For Lorenz curve generation
        - **Weighted Averages**: For aggregated statistics
        
        ### 📈 Visualization Techniques
        
        #### Interactive Charts
        - **Plotly**: For interactive, web-based visualizations
        - **Hover Information**: Detailed data on mouse hover
        - **Zoom and Pan**: User-controlled chart exploration
        - **Export Options**: Download charts as images
        
        #### Chart Types
        - **Line Charts**: For time series analysis
        - **Bar Charts**: For categorical comparisons
        - **Scatter Plots**: For correlation analysis
        - **Radar Charts**: For multi-dimensional comparison
        
        ### 🛠️ Technical Implementation
        
        #### Architecture
        - **Modular Design**: Separate modules for data, metrics, visualization
        - **Caching**: Streamlit caching for performance
        - **Error Handling**: Graceful degradation for missing data
        - **Responsive Design**: Works on desktop and mobile
        
        #### Data Flow
        1. User selects parameters (country, year, metrics)
        2. System fetches data from APIs
        3. Data is cleaned and processed
        4. Metrics are calculated
        5. Visualizations are generated
        6. Results are displayed to user
        
        ### 📋 Data Quality
        
        #### Data Sources Reliability
        - **World Bank**: Official international statistics
        - **OECD**: Peer-reviewed methodology
        - **WID.world**: Academic research standards
        - **Eurostat**: EU statistical authority
        
        #### Limitations
        - **Coverage**: Not all countries have complete data
        - **Timeliness**: Some data may be 1-2 years old
        - **Methodology**: Different sources use varying approaches
        - **Definitions**: Income vs. consumption measures vary
        
        ### 🔍 Best Practices
        
        #### Interpretation Guidelines
        - **Context Matters**: Consider economic and social factors
        - **Trends vs. Levels**: Focus on changes over time
        - **Comparisons**: Use similar countries for benchmarking
        - **Caveats**: Acknowledge data limitations
        
        #### Usage Recommendations
        - **Multiple Metrics**: Don't rely on single measure
        - **Time Series**: Analyze trends, not just levels
        - **Cross-Country**: Compare with similar economies
        - **Updates**: Check for latest data availability
        """)
        
        st.markdown("---")
        
        # ============================================================================
        # ℹ️ ABOUT SECTION
        # ============================================================================
        st.markdown("## ℹ️ About This Dashboard")
        
        st.markdown("""
        ### Data Sources
        
        This dashboard uses data from multiple reliable sources:
        
        - **World Bank**: Gini coefficients and poverty indicators
        - **OECD**: Income distribution data for member countries
        - **WID.world**: World Inequality Database with comprehensive inequality metrics
        - **Eurostat**: EU-specific inequality and income data
        
        ### Metrics Explained
        
        - **Gini Coefficient**: Measures income inequality on a scale from 0 (perfect equality) to 1 (perfect inequality)
        - **Palma Ratio**: Ratio of the richest 10% to the poorest 40% of the population
        - **Income Shares**: Percentage of total income held by different population segments
        - **Lorenz Curve**: Visual representation of income distribution
        
        ### Methodology
        
        Data is collected from public APIs and databases, cleaned and standardized,
        and analyzed using established inequality measurement techniques.
        
        ### Limitations
        
        - Data availability varies by country and time period
        - Different sources may use slightly different methodologies
        - Some countries may have limited or outdated data
        
        ### Contact
        
        For questions or suggestions, please refer to the project documentation.
        """)
    
    else:
        st.info("👈 Please select a country from the sidebar to begin analysis.")

if __name__ == "__main__":
    main() 