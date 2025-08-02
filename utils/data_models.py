"""
Data models and processing utilities for the Gini Inequality Visualizer.

This module contains data models, validation functions, and utility functions
for processing Gini coefficient data from the World Bank API.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class Country:
    """Data model for country information."""
    code: str          # ISO country code (e.g., "USA")
    name: str          # Full country name (e.g., "United States")
    region: str        # World Bank region classification

    def __post_init__(self):
        """Validate country data after initialization."""
        if not self.code or not isinstance(self.code, str):
            raise ValueError("Country code must be a non-empty string")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Country name must be a non-empty string")
        
        # Normalize country code to uppercase
        self.code = self.code.upper()


@dataclass
class GiniDataPoint:
    """Data model for individual Gini coefficient data points."""
    year: int          # Year of measurement
    value: float       # Gini coefficient (0-100 scale)
    country_code: str  # ISO country code

    def __post_init__(self):
        """Validate Gini data point after initialization."""
        if not validate_year(self.year):
            raise ValueError(f"Invalid year: {self.year}")
        if not validate_gini_value(self.value):
            raise ValueError(f"Invalid Gini value: {self.value}")
        if not self.country_code or not isinstance(self.country_code, str):
            raise ValueError("Country code must be a non-empty string")
        
        # Normalize country code to uppercase
        self.country_code = self.country_code.upper()


@dataclass
class GiniTimeSeries:
    """Container for a time series of Gini data points for a country."""
    country: Country
    data_points: List[GiniDataPoint]
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert Gini time series to pandas DataFrame for visualization.
        
        Returns:
            DataFrame with columns: ['year', 'value', 'country_code', 'country_name']
        """
        if not self.data_points:
            return pd.DataFrame(columns=['year', 'value', 'country_code', 'country_name'])
        
        data = []
        for point in self.data_points:
            data.append({
                'year': point.year,
                'value': point.value,
                'country_code': point.country_code,
                'country_name': self.country.name
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('year').reset_index(drop=True)
    
    def get_latest_value(self) -> Optional[GiniDataPoint]:
        """Get the most recent Gini data point."""
        if not self.data_points:
            return None
        return max(self.data_points, key=lambda x: x.year)
    
    def get_value_for_year(self, year: int) -> Optional[float]:
        """Get Gini value for a specific year."""
        for point in self.data_points:
            if point.year == year:
                return point.value
        return None


# Data validation functions

def validate_gini_value(value: Union[float, int, None]) -> bool:
    """
    Validate that a Gini coefficient value is within acceptable range.
    
    The Gini coefficient can be expressed on different scales:
    - 0-1 scale (decimal format, used by some sources)
    - 0-100 scale (percentage format, used by World Bank)
    
    Args:
        value: Gini coefficient value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if value is None:
        return False
    
    try:
        float_value = float(value)
        # Accept both 0-1 scale (decimal) and 0-100 scale (percentage)
        # We normalize to 0-100 scale during data processing
        return 0 <= float_value <= 100 or 0 <= float_value <= 1
    except (ValueError, TypeError):
        return False


def validate_year(year: Union[int, str, None]) -> bool:
    """
    Validate that a year value is reasonable for Gini data.
    
    World Bank economic data typically starts from the 1960s, and we allow
    a few years into the future to account for data publication delays.
    
    Args:
        year: Year value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if year is None:
        return False
    
    try:
        int_year = int(year)
        # Reasonable range: World Bank data starts ~1960, allow future years for data delays
        return 1960 <= int_year <= 2030
    except (ValueError, TypeError):
        return False


def validate_country_code(code: Union[str, None]) -> bool:
    """
    Validate country code format.
    
    Args:
        code: Country code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not code or not isinstance(code, str):
        return False
    
    # World Bank uses 3-letter ISO codes
    return len(code.strip()) == 3 and code.strip().isalpha()


# Data processing utility functions

def convert_api_response_to_dataframe(api_response: List[Dict[str, Any]], 
                                    country_code: str) -> pd.DataFrame:
    """
    Convert World Bank API response to pandas DataFrame.
    
    Args:
        api_response: Raw API response data
        country_code: ISO country code for the data
        
    Returns:
        DataFrame with columns: ['year', 'value', 'country_code']
    """
    if not api_response:
        return pd.DataFrame(columns=['year', 'value', 'country_code'])
    
    processed_data = []
    
    for entry in api_response:
        if not isinstance(entry, dict):
            continue
            
        # Extract year and value from API response
        year_raw = entry.get('date')
        value_raw = entry.get('value')
        
        # Skip entries with missing data
        if year_raw is None or value_raw is None:
            continue
        
        # Validate and convert data
        if validate_year(year_raw) and validate_gini_value(value_raw):
            try:
                year = int(year_raw)
                value = float(value_raw)
                
                # Normalize Gini value to 0-100 scale if needed
                if value <= 1:
                    value = value * 100
                
                processed_data.append({
                    'year': year,
                    'value': value,
                    'country_code': country_code.upper()
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid data point: {entry}, error: {e}")
    
    df = pd.DataFrame(processed_data)
    
    if not df.empty:
        df = df.sort_values('year').reset_index(drop=True)
    
    return df


def clean_gini_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and format Gini coefficient data.
    
    Args:
        df: Raw DataFrame with Gini data
        
    Returns:
        Cleaned DataFrame with proper formatting and missing value handling
    """
    if df.empty:
        return df
    
    # Make a copy to avoid modifying original data
    cleaned_df = df.copy()
    
    # Ensure required columns exist
    required_columns = ['year', 'value', 'country_code']
    for col in required_columns:
        if col not in cleaned_df.columns:
            cleaned_df[col] = None
    
    # Remove rows with invalid data
    initial_rows = len(cleaned_df)
    
    # Filter out invalid years
    cleaned_df = cleaned_df[cleaned_df['year'].apply(validate_year)]
    
    # Filter out invalid Gini values
    cleaned_df = cleaned_df[cleaned_df['value'].apply(validate_gini_value)]
    
    # Remove duplicates (same year for same country)
    cleaned_df = cleaned_df.drop_duplicates(subset=['year', 'country_code'], keep='last')
    
    # Sort by year
    cleaned_df = cleaned_df.sort_values('year').reset_index(drop=True)
    
    # Normalize Gini values to 0-100 scale
    cleaned_df['value'] = cleaned_df['value'].apply(lambda x: x * 100 if x <= 1 else x)
    
    # Round values to 2 decimal places for consistency
    cleaned_df['value'] = cleaned_df['value'].round(2)
    
    # Ensure country codes are uppercase
    cleaned_df['country_code'] = cleaned_df['country_code'].str.upper()
    
    rows_removed = initial_rows - len(cleaned_df)
    if rows_removed > 0:
        logger.info(f"Removed {rows_removed} invalid data points during cleaning")
    
    return cleaned_df


def handle_missing_values(df: pd.DataFrame, method: str = 'drop') -> pd.DataFrame:
    """
    Handle missing values in Gini data.
    
    Args:
        df: DataFrame with potential missing values
        method: Method for handling missing values ('drop', 'interpolate', 'forward_fill')
        
    Returns:
        DataFrame with missing values handled according to specified method
    """
    if df.empty:
        return df
    
    cleaned_df = df.copy()
    
    if method == 'drop':
        # Remove rows with any missing values
        cleaned_df = cleaned_df.dropna()
    
    elif method == 'interpolate':
        # Interpolate missing values (only for numeric columns)
        if 'value' in cleaned_df.columns:
            cleaned_df['value'] = cleaned_df['value'].interpolate(method='linear')
        cleaned_df = cleaned_df.dropna()  # Drop any remaining NaN values
    
    elif method == 'forward_fill':
        # Forward fill missing values
        cleaned_df = cleaned_df.fillna(method='ffill')
        cleaned_df = cleaned_df.dropna()  # Drop any remaining NaN values
    
    else:
        raise ValueError(f"Unknown method for handling missing values: {method}")
    
    return cleaned_df.reset_index(drop=True)


def format_data_for_visualization(df: pd.DataFrame, country_name: str = None) -> pd.DataFrame:
    """
    Format Gini data for visualization components.
    
    Args:
        df: DataFrame with Gini data
        country_name: Optional country name to add to the data
        
    Returns:
        Formatted DataFrame ready for visualization
    """
    if df.empty:
        return pd.DataFrame(columns=['year', 'value', 'country_code', 'country_name'])
    
    formatted_df = df.copy()
    
    # Ensure proper data types
    formatted_df['year'] = formatted_df['year'].astype(int)
    formatted_df['value'] = formatted_df['value'].astype(float)
    formatted_df['country_code'] = formatted_df['country_code'].astype(str)
    
    # Add country name if provided
    if country_name:
        formatted_df['country_name'] = country_name
    elif 'country_name' not in formatted_df.columns:
        formatted_df['country_name'] = formatted_df['country_code']
    
    # Sort by year for proper visualization
    formatted_df = formatted_df.sort_values('year').reset_index(drop=True)
    
    return formatted_df


def create_gini_data_points(df: pd.DataFrame) -> List[GiniDataPoint]:
    """
    Convert DataFrame to list of GiniDataPoint objects.
    
    Args:
        df: DataFrame with Gini data
        
    Returns:
        List of GiniDataPoint objects
    """
    if df.empty:
        return []
    
    data_points = []
    
    for _, row in df.iterrows():
        try:
            data_point = GiniDataPoint(
                year=int(row['year']),
                value=float(row['value']),
                country_code=str(row['country_code'])
            )
            data_points.append(data_point)
        except (ValueError, KeyError) as e:
            logger.warning(f"Skipping invalid row during GiniDataPoint creation: {row}, error: {e}")
    
    return data_points


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics for Gini data.
    
    Args:
        df: DataFrame with Gini data
        
    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {
            'count': 0,
            'year_range': None,
            'value_range': None,
            'mean_value': None,
            'latest_value': None,
            'trend': None
        }
    
    summary = {
        'count': len(df),
        'year_range': (int(df['year'].min()), int(df['year'].max())),
        'value_range': (float(df['value'].min()), float(df['value'].max())),
        'mean_value': float(df['value'].mean()),
        'latest_value': float(df.loc[df['year'].idxmax(), 'value']),
    }
    
    # Calculate trend (simple linear trend)
    if len(df) > 1:
        years = df['year'].values
        values = df['value'].values
        trend_coef = np.polyfit(years, values, 1)[0]
        
        if trend_coef > 0.1:
            summary['trend'] = 'increasing'
        elif trend_coef < -0.1:
            summary['trend'] = 'decreasing'
        else:
            summary['trend'] = 'stable'
    else:
        summary['trend'] = 'insufficient_data'
    
    return summary