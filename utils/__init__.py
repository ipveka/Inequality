"""
Utilities package for the Gini Inequality Visualizer.

This package contains core utility modules for data processing,
API interaction, visualization, and UI components.
"""

from .data_models import Country, GiniDataPoint, GiniTimeSeries
from .data_service import WorldBankClient, WorldBankAPIError, APIConnectionError, APIRateLimitError, DataNotAvailableError, InvalidCountryError
from .visualization import create_gini_line_plot, create_gini_table
from .ui_components import render_sidebar, render_main_dashboard, show_loading_state, show_error_message, show_welcome_message, display_data_summary

__all__ = [
    # Data models
    'Country',
    'GiniDataPoint', 
    'GiniTimeSeries',
    
    # Data service
    'WorldBankClient',
    'WorldBankAPIError',
    'APIConnectionError',
    'APIRateLimitError',
    'DataNotAvailableError',
    'InvalidCountryError',
    
    # Visualization
    'create_gini_line_plot',
    'create_gini_table',
    
    # UI components
    'render_sidebar',
    'render_main_dashboard',
    'show_loading_state',
    'show_error_message',
    'show_welcome_message',
    'display_data_summary',
]