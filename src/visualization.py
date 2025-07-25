"""
Visualization functions for inequality data using Plotly and other libraries.
"""

import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from .metrics import lorenz_curve_data, gini_coefficient
from .utils import get_country_name, logger

def plot_lorenz_curve(data: pd.Series, title: str = "Lorenz Curve", 
                     show_perfect_equality: bool = True) -> go.Figure:
    """
    Create an interactive Lorenz curve plot.
    
    Args:
        data: Pandas Series containing income/wealth values
        title: Plot title
        show_perfect_equality: Whether to show the perfect equality line
    
    Returns:
        Plotly figure object
    """
    try:
        # Generate Lorenz curve data
        population_shares, income_shares = lorenz_curve_data(data.tolist())
        
        # Create the plot
        fig = go.Figure()
        
        # Add Lorenz curve
        fig.add_trace(go.Scatter(
            x=population_shares,
            y=income_shares,
            mode='lines',
            name='Lorenz Curve',
            line=dict(color='blue', width=3),
            fill='tonexty',
            fillcolor='rgba(0, 100, 255, 0.1)'
        ))
        
        # Add perfect equality line
        if show_perfect_equality:
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode='lines',
                name='Perfect Equality',
                line=dict(color='red', width=2, dash='dash'),
                showlegend=True
            ))
        
        # Calculate Gini coefficient
        gini = gini_coefficient(data.tolist())
        
        # Update layout
        fig.update_layout(
            title=f"{title}<br><sub>Gini Coefficient: {gini:.3f}</sub>",
            xaxis_title="Cumulative Population Share",
            yaxis_title="Cumulative Income Share",
            xaxis=dict(range=[0, 1], tickformat='.1%'),
            yaxis=dict(range=[0, 1], tickformat='.1%'),
            hovermode='x unified',
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating Lorenz curve: {e}")
        return go.Figure()

def plot_gini_by_country(df: pd.DataFrame, year: int = None) -> go.Figure:
    """
    Create a bar chart showing Gini coefficients by country.
    
    Args:
        df: DataFrame with columns: country_code, gini, year
        year: Specific year to plot (if None, uses latest available)
    
    Returns:
        Plotly figure object
    """
    try:
        # Filter data
        if year is not None:
            df_filtered = df[df['year'] == year].copy()
        else:
            # Use latest year for each country
            df_filtered = df.loc[df.groupby('country_code')['year'].idxmax()].copy()
        
        if df_filtered.empty:
            logger.warning("No data available for the specified criteria")
            return go.Figure()
        
        # Sort by Gini coefficient
        df_filtered = df_filtered.sort_values('gini', ascending=True)
        
        # Create the plot
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=df_filtered['gini'],
            y=df_filtered['country_name'],
            orientation='h',
            marker=dict(
                color=df_filtered['gini'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Gini Coefficient")
            ),
            text=[f"{gini:.3f}" for gini in df_filtered['gini']],
            textposition='auto',
            hovertemplate="<b>%{y}</b><br>" +
                         "Gini: %{x:.3f}<br>" +
                         "Year: " + str(df_filtered['year'].iloc[0]) +
                         "<extra></extra>"
        ))
        
        # Update layout
        year_text = f" ({year})" if year else ""
        fig.update_layout(
            title=f"Gini Coefficient by Country{year_text}",
            xaxis_title="Gini Coefficient",
            yaxis_title="Country",
            xaxis=dict(range=[0, 1]),
            height=max(400, len(df_filtered) * 30),
            template='plotly_white',
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating Gini by country plot: {e}")
        return go.Figure()

def plot_income_shares(df: pd.DataFrame, country_code: str = None, 
                      year: int = None) -> go.Figure:
    """
    Create a stacked bar chart showing income shares by percentile.
    
    Args:
        df: DataFrame with income share columns
        country_code: Specific country to plot
        year: Specific year to plot
    
    Returns:
        Plotly figure object
    """
    try:
        # Filter data
        df_filtered = df.copy()
        
        if country_code:
            df_filtered = df_filtered[df_filtered['country_code'] == country_code]
        
        if year:
            df_filtered = df_filtered[df_filtered['year'] == year]
        
        if df_filtered.empty:
            logger.warning("No data available for the specified criteria")
            return go.Figure()
        
        # Use latest data if multiple years
        if len(df_filtered) > 1:
            latest_year = df_filtered['year'].idxmax()
            df_filtered = df_filtered.loc[[latest_year]]
        
        # Prepare data for plotting
        share_columns = ['bottom_50_share', 'middle_40_share', 'top_10_share']
        available_columns = [col for col in share_columns if col in df_filtered.columns]
        
        if not available_columns:
            logger.warning("No income share columns found")
            return go.Figure()
        
        # Create the plot
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#d62728']  # Blue, Orange, Red
        
        for i, col in enumerate(available_columns):
            share_value = df_filtered[col]
            if pd.notna(share_value):
                fig.add_trace(go.Bar(
                    name=col.replace('_', ' ').title(),
                    y=[share_value],
                    marker_color=colors[i % len(colors)],
                    text=f"{share_value:.1%}",
                    textposition='auto'
                ))
        
        # Update layout
        country_name = get_country_name(country_code) if country_code else "All Countries"
        year_text = f" ({df_filtered['year']})" if 'year' in df_filtered else ""
        
        fig.update_layout(
            title=f"Income Shares - {country_name}{year_text}",
            yaxis_title="Share of Total Income",
            yaxis=dict(tickformat='.1%', range=[0, 1]),
            barmode='stack',
            template='plotly_white',
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating income shares plot: {e}")
        return go.Figure()

def plot_inequality_trends(df: pd.DataFrame, country_codes: List[str] = None,
                          metric: str = 'gini', start_year: int = None, 
                          end_year: int = None) -> go.Figure:
    """
    Create a line plot showing inequality trends over time.
    
    Args:
        df: DataFrame with time series data
        country_codes: List of country codes to include
        metric: Metric to plot (gini, palma_ratio, etc.)
        start_year: Start year for the plot
        end_year: End year for the plot
    
    Returns:
        Plotly figure object
    """
    try:
        # Filter data
        df_filtered = df.copy()
        
        if country_codes:
            df_filtered = df_filtered[df_filtered['country_code'].isin(country_codes)]
        
        if start_year:
            df_filtered = df_filtered[df_filtered['year'] >= start_year]
        
        if end_year:
            df_filtered = df_filtered[df_filtered['year'] <= end_year]
        
        if metric not in df_filtered.columns:
            logger.warning(f"Metric '{metric}' not found in data")
            return go.Figure()
        
        if df_filtered.empty:
            logger.warning("No data available for the specified criteria")
            return go.Figure()
        
        # Create the plot
        fig = go.Figure()
        
        # Add lines for each country
        for country_code in df_filtered['country_code'].unique():
            country_data = df_filtered[df_filtered['country_code'] == country_code]
            country_name = get_country_name(country_code)
            
            fig.add_trace(go.Scatter(
                x=country_data['year'],
                y=country_data[metric],
                mode='lines+markers',
                name=country_name,
                hovertemplate=f"<b>{country_name}</b><br>" +
                             f"Year: %{{x}}<br>" +
                             f"{metric.replace('_', ' ').title()}: %{{y:.3f}}" +
                             "<extra></extra>"
            ))
        
        # Update layout
        metric_title = metric.replace('_', ' ').title()
        fig.update_layout(
            title=f"{metric_title} Trends Over Time",
            xaxis_title="Year",
            yaxis_title=metric_title,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating inequality trends plot: {e}")
        return go.Figure()

def plot_country_comparison(df: pd.DataFrame, country_codes: List[str],
                           year: int = None, metrics: List[str] = None) -> go.Figure:
    """
    Create a radar chart comparing multiple countries across different metrics.
    
    Args:
        df: DataFrame with inequality metrics
        country_codes: List of country codes to compare
        year: Specific year to compare
        metrics: List of metrics to include in comparison
    
    Returns:
        Plotly figure object
    """
    try:
        if metrics is None:
            metrics = ['gini', 'palma_ratio', 'top_10_share', 'bottom_50_share']
        
        # Filter data
        df_filtered = df[df['country_code'].isin(country_codes)].copy()
        
        if year:
            df_filtered = df_filtered[df_filtered['year'] == year]
        else:
            # Use latest year for each country
            df_filtered = df_filtered.loc[df_filtered.groupby('country_code')['year'].idxmax()]
        
        if df_filtered.empty:
            logger.warning("No data available for the specified criteria")
            return go.Figure()
        
        # Create the plot
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set3
        
        for i, country_code in enumerate(country_codes):
            country_data = df_filtered[df_filtered['country_code'] == country_code]
            if country_data.empty:
                continue
                
            country_name = get_country_name(country_code)
            values = []
            
            for metric in metrics:
                if metric in country_data.columns:
                    value = country_data[metric].iloc[0]
                    if pd.notna(value):
                        values.append(value)
                    else:
                        values.append(0)
                else:
                    values.append(0)
            
            # Normalize values to 0-1 scale for radar chart
            values_normalized = [(v - min(values)) / (max(values) - min(values)) if max(values) != min(values) else 0.5 for v in values]
            
            fig.add_trace(go.Scatterpolar(
                r=values_normalized,
                theta=metrics,
                fill='toself',
                name=country_name,
                line_color=colors[i % len(colors)]
            ))
        
        # Update layout
        year_text = f" ({year})" if year else ""
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            title=f"Country Comparison{year_text}",
            template='plotly_white',
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating country comparison plot: {e}")
        return go.Figure()

def plot_inequality_distribution(df: pd.DataFrame, metric: str = 'gini',
                                bins: int = 20) -> go.Figure:
    """
    Create a histogram showing the distribution of inequality metrics.
    
    Args:
        df: DataFrame with inequality metrics
        metric: Metric to plot
        bins: Number of histogram bins
    
    Returns:
        Plotly figure object
    """
    try:
        if metric not in df.columns:
            logger.warning(f"Metric '{metric}' not found in data")
            return go.Figure()
        
        # Remove missing values
        values = df[metric].dropna()
        
        if values.empty:
            logger.warning(f"No data available for metric '{metric}'")
            return go.Figure()
        
        # Create the plot
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=values,
            nbinsx=bins,
            name=metric.replace('_', ' ').title(),
            marker_color='lightblue',
            opacity=0.7
        ))
        
        # Add vertical line for mean
        mean_value = values.mean()
        fig.add_vline(
            x=mean_value,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_value:.3f}"
        )
        
        # Update layout
        metric_title = metric.replace('_', ' ').title()
        fig.update_layout(
            title=f"Distribution of {metric_title}",
            xaxis_title=metric_title,
            yaxis_title="Frequency",
            template='plotly_white',
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating inequality distribution plot: {e}")
        return go.Figure()

def create_dashboard_summary(df: pd.DataFrame, country_code: str = None,
                           year: int = None) -> go.Figure:
    """
    Create a comprehensive dashboard with multiple inequality metrics.
    
    Args:
        df: DataFrame with inequality data
        country_code: Specific country to focus on
        year: Specific year to focus on
    
    Returns:
        Plotly figure with subplots
    """
    try:
        # Filter data
        df_filtered = df.copy()
        
        if country_code:
            df_filtered = df_filtered[df_filtered['country_code'] == country_code]
        
        if year:
            df_filtered = df_filtered[df_filtered['year'] == year]
        
        if df_filtered.empty:
            logger.warning("No data available for the specified criteria")
            return go.Figure()
        
        # Use latest data if multiple years
        if len(df_filtered) > 1:
            latest_year = df_filtered['year'].idxmax()
            df_filtered = df_filtered.loc[[latest_year]]
        
        # Create subplots
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=('Gini Coefficient', 'Income Shares', 'Palma Ratio', 'Top 1% vs Bottom 50%'),
            specs=[[{"type": "indicator"}, {"type": "bar"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Gini coefficient gauge
        if 'gini' in df_filtered.columns:
            gini_value = df_filtered['gini'].iloc[0]
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=gini_value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Gini Coefficient"},
                gauge={'axis': {'range': [None, 1]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 0.3], 'color': "lightgray"},
                           {'range': [0.3, 0.5], 'color': "yellow"},
                           {'range': [0.5, 1], 'color': "red"}
                       ],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75, 'value': 0.5}}
            ), row=1, col=1)
        
        # Income shares bar chart
        share_columns = ['bottom_50_share', 'middle_40_share', 'top_10_share']
        available_shares = [col for col in share_columns if col in df_filtered.columns]
        
        if available_shares:
            for col in available_shares:
                value = df_filtered[col].iloc[0]
                if pd.notna(value):
                    fig.add_trace(go.Bar(
                        x=[col.replace('_', ' ').title()],
                        y=[value],
                        name=col.replace('_', ' ').title(),
                        text=f"{value:.1%}",
                        textposition='auto'
                    ), row=1, col=2)
        
        # Palma ratio indicator
        if 'palma_ratio' in df_filtered.columns:
            palma_value = df_filtered['palma_ratio'].iloc[0]
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=palma_value,
                title={'text': "Palma Ratio"},
                delta={'reference': 1.0}
            ), row=2, col=1)
        
        # Top 1% vs Bottom 50% ratio
        if 'top_1_share' in df_filtered.columns and 'bottom_50_share' in df_filtered.columns:
            top_1 = df_filtered['top_1_share'].iloc[0]
            bottom_50 = df_filtered['bottom_50_share'].iloc[0]
            if pd.notna(top_1) and pd.notna(bottom_50) and bottom_50 > 0:
                ratio = top_1 / bottom_50
                fig.add_trace(go.Indicator(
                    mode="number+delta",
                    value=ratio,
                    title={'text': "Top 1% / Bottom 50%"},
                    delta={'reference': 1.0}
                ), row=2, col=2)
        
        # Update layout
        country_name = get_country_name(country_code) if country_code else "All Countries"
        year_text = f" ({df_filtered['year'].iloc[0]})" if 'year' in df_filtered else ""
        
        fig.update_layout(
            title=f"Inequality Dashboard - {country_name}{year_text}",
            template='plotly_white',
            height=600
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating dashboard summary: {e}")
        return go.Figure() 