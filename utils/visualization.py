"""
Visualization service module for creating charts and tables.

This module handles all visualization operations using plotly and pandas
for interactive charts and formatted data tables.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional


def create_gini_line_plot(data: pd.DataFrame, country_name: str) -> go.Figure:
    """
    Create interactive line plot of Gini index over time.
    
    Args:
        data: DataFrame containing year and Gini value columns
        country_name: Name of the country for chart title
        
    Returns:
        Plotly figure object
    """
    # Create figure with custom styling
    fig = go.Figure()
    
    if data.empty:
        # Create empty plot with message
        fig.add_annotation(
            text=f"No Gini coefficient data available for {country_name}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=f"Gini Coefficient Over Time - {country_name}",
            xaxis_title="Year",
            yaxis_title="Gini Coefficient",
            height=500
        )
        return fig
    
    # Sort data chronologically for proper line plot display
    plot_data = data.copy()
    plot_data = plot_data.sort_values('year').reset_index(drop=True)
    
    # Filter out missing values for clean visualization
    plot_data = plot_data.dropna(subset=['value'])
    
    if plot_data.empty:
        # Handle case where all values were missing
        fig.add_annotation(
            text=f"No valid Gini coefficient data available for {country_name}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=f"Gini Coefficient Over Time - {country_name}",
            xaxis_title="Year",
            yaxis_title="Gini Coefficient",
            height=500
        )
        return fig
    
    # Create the main line trace with professional styling
    # Using Scatter with lines+markers for better interactivity
    fig.add_trace(go.Scatter(
        x=plot_data['year'],
        y=plot_data['value'],
        mode='lines+markers',  # Show both line and data points
        name=f'{country_name} Gini Coefficient',
        line=dict(
            color='#1f77b4',  # Professional blue color (matplotlib default)
            width=3  # Thicker line for better visibility
        ),
        marker=dict(
            size=8,  # Visible but not overwhelming marker size
            color='#1f77b4',  # Match line color
            line=dict(width=2, color='white')  # White border for contrast
        ),
        # Custom hover template for better user experience
        hovertemplate=(
            '<b>' + country_name + '</b><br>' +
            'Year: %{x}<br>' +
            'Gini Coefficient: %{y:.2f}<br>' +
            '<extra></extra>'  # Remove default trace box
        )
    ))
    
    # Configure layout with professional styling and accessibility
    fig.update_layout(
        title=dict(
            text=f"Gini Coefficient Over Time - {country_name}",
            font=dict(size=20, color='#2c3e50'),  # Dark blue-gray for readability
            x=0.5,  # Center the title
            xanchor='center'
        ),
        xaxis=dict(
            title="Year",
            title_font=dict(size=14, color='#2c3e50'),
            tickfont=dict(size=12, color='#2c3e50'),
            gridcolor='#ecf0f1',  # Light gray grid lines
            showgrid=True,  # Show grid for easier reading
            zeroline=False  # Hide zero line (not meaningful for years)
        ),
        yaxis=dict(
            title="Gini Coefficient",
            title_font=dict(size=14, color='#2c3e50'),
            tickfont=dict(size=12, color='#2c3e50'),
            gridcolor='#ecf0f1',  # Light gray grid lines
            showgrid=True,  # Show grid for easier reading
            zeroline=False,  # Hide zero line
            # Set appropriate y-axis range (0-100 for Gini coefficient)
            range=[0, max(100, data['value'].max() * 1.1) if not data.empty else 100]
        ),
        plot_bgcolor='white',  # Clean white background
        paper_bgcolor='white',  # Clean white paper background
        height=500,  # Fixed height for consistency
        margin=dict(l=60, r=40, t=80, b=60),  # Adequate margins for labels
        hovermode='x unified',  # Show hover info for all traces at same x
        showlegend=False,  # Hide legend (single trace doesn't need it)
        font=dict(family="Arial, sans-serif")  # Professional font family
    )
    
    # Add subtle background styling
    fig.update_xaxes(showline=True, linewidth=1, linecolor='#bdc3c7')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='#bdc3c7')
    
    return fig


def create_gini_table(data: pd.DataFrame) -> pd.DataFrame:
    """
    Format Gini data for tabular display.
    
    Args:
        data: Raw Gini data DataFrame
        
    Returns:
        Formatted DataFrame for display with missing values handled appropriately
    """
    if data.empty:
        return pd.DataFrame(columns=['Year', 'Gini Coefficient'])
    
    # Create a copy for formatting
    table_data = data.copy()
    
    # Handle missing data values appropriately by filtering out NaN/None values
    table_data = table_data.dropna(subset=['value'])
    
    # If all values were missing, return empty table with proper columns
    if table_data.empty:
        return pd.DataFrame(columns=['Year', 'Gini Coefficient'])
    
    # Sort by year in chronological order (most recent first for better UX)
    table_data = table_data.sort_values('year', ascending=False).reset_index(drop=True)
    
    # Create formatted table with proper column names and decimal formatting
    formatted_table = pd.DataFrame({
        'Year': table_data['year'].astype(int),
        'Gini Coefficient': table_data['value'].round(2)
    })
    
    return formatted_table


def format_gini_data(raw_data: dict) -> pd.DataFrame:
    """
    Clean and structure raw API data into DataFrame.
    
    Args:
        raw_data: Raw data from World Bank API
        
    Returns:
        Cleaned and formatted DataFrame
    """
    if not raw_data or not isinstance(raw_data, dict):
        return pd.DataFrame(columns=['year', 'value', 'country_code'])
    
    # Extract data points from API response
    data_points = []
    
    # Handle different possible API response structures
    if 'data' in raw_data:
        api_data = raw_data['data']
    else:
        api_data = raw_data
    
    if isinstance(api_data, list):
        for entry in api_data:
            if isinstance(entry, dict) and 'date' in entry and 'value' in entry:
                year = entry.get('date')
                value = entry.get('value')
                country_code = entry.get('country', {}).get('id', '') if isinstance(entry.get('country'), dict) else ''
                
                # Validate and add data point
                if year and value is not None:
                    try:
                        year_int = int(year)
                        value_float = float(value)
                        
                        # Normalize Gini value to 0-100 scale if needed
                        if value_float <= 1:
                            value_float = value_float * 100
                        
                        data_points.append({
                            'year': year_int,
                            'value': round(value_float, 2),
                            'country_code': country_code
                        })
                    except (ValueError, TypeError):
                        continue
    
    # Create DataFrame
    df = pd.DataFrame(data_points)
    
    if not df.empty:
        # Sort by year and remove duplicates
        df = df.sort_values('year').drop_duplicates(subset=['year'], keep='last').reset_index(drop=True)
    
    return df