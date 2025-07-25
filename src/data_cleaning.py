"""
Data cleaning and formatting functions for inequality data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from .utils import get_country_name, get_country_code, validate_dataframe, logger

def normalize_country_codes(df: pd.DataFrame, country_column: str = 'country_code') -> pd.DataFrame:
    """
    Normalize country codes to ISO 3-letter format.
    
    Args:
        df: DataFrame containing country data
        country_column: Name of the column containing country codes/names
    
    Returns:
        DataFrame with normalized country codes
    """
    if country_column not in df.columns:
        logger.warning(f"Country column '{country_column}' not found in DataFrame")
        return df
    
    df_clean = df.copy()
    
    # Create mapping for common variations
    country_mapping = {
        'US': 'USA', 'United States': 'USA', 'USA': 'USA',
        'Germany': 'DEU', 'DE': 'DEU', 'DEU': 'DEU',
        'France': 'FRA', 'FR': 'FRA', 'FRA': 'FRA',
        'United Kingdom': 'GBR', 'UK': 'GBR', 'GB': 'GBR', 'GBR': 'GBR',
        'Italy': 'ITA', 'IT': 'ITA', 'ITA': 'ITA',
        'Spain': 'ESP', 'ES': 'ESP', 'ESP': 'ESP',
        'Canada': 'CAN', 'CA': 'CAN', 'CAN': 'CAN',
        'Australia': 'AUS', 'AU': 'AUS', 'AUS': 'AUS',
        'Japan': 'JPN', 'JP': 'JPN', 'JPN': 'JPN',
        'Brazil': 'BRA', 'BR': 'BRA', 'BRA': 'BRA',
        'India': 'IND', 'IN': 'IND', 'IND': 'IND',
        'China': 'CHN', 'CN': 'CHN', 'CHN': 'CHN',
        'Russia': 'RUS', 'RU': 'RUS', 'RUS': 'RUS',
        'Mexico': 'MEX', 'MX': 'MEX', 'MEX': 'MEX',
        'South Korea': 'KOR', 'KR': 'KOR', 'KOR': 'KOR',
        'Netherlands': 'NLD', 'NL': 'NLD', 'NLD': 'NLD',
        'Sweden': 'SWE', 'SE': 'SWE', 'SWE': 'SWE',
        'Norway': 'NOR', 'NO': 'NOR', 'NOR': 'NOR',
        'Denmark': 'DNK', 'DK': 'DNK', 'DNK': 'DNK',
        'Finland': 'FIN', 'FI': 'FIN', 'FIN': 'FIN'
    }
    
    # Apply mapping
    df_clean[country_column] = df_clean[country_column].map(
        lambda x: country_mapping.get(str(x).strip(), str(x).strip())
    )
    
    # Add country names if not present
    if 'country_name' not in df_clean.columns:
        df_clean['country_name'] = df_clean[country_column].apply(get_country_name)
    
    return df_clean

def clean_inequality_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize inequality data.
    
    Args:
        df: Raw inequality DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Normalize country codes
    if 'country_code' in df_clean.columns:
        df_clean = normalize_country_codes(df_clean)
    
    # Handle missing values
    df_clean = handle_missing_values(df_clean)
    
    # Standardize column names
    df_clean = standardize_column_names(df_clean)
    
    # Validate data types
    df_clean = validate_data_types(df_clean)
    
    # Remove duplicates
    df_clean = df_clean.drop_duplicates()
    
    # Sort by country and year
    if 'country_code' in df_clean.columns and 'year' in df_clean.columns:
        df_clean = df_clean.sort_values(['country_code', 'year'])
    
    logger.info(f"Cleaned data: {len(df_clean)} rows, {len(df_clean.columns)} columns")
    return df_clean

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in inequality data.
    
    Args:
        df: DataFrame with potential missing values
    
    Returns:
        DataFrame with handled missing values
    """
    df_clean = df.copy()
    
    # For numeric columns, we'll keep NaN values but log them
    numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        missing_count = df_clean[col].isna().sum()
        if missing_count > 0:
            logger.info(f"Column '{col}' has {missing_count} missing values")
    
    # For categorical columns, fill with 'Unknown' or most common value
    categorical_columns = df_clean.select_dtypes(include=['object']).columns
    
    for col in categorical_columns:
        if col in ['country_code', 'country_name', 'source']:
            # For important categorical columns, keep NaN
            continue
        else:
            # For other categorical columns, fill with most common value
            most_common = df_clean[col].mode().iloc[0] if not df_clean[col].mode().empty else 'Unknown'
            df_clean[col] = df_clean[col].fillna(most_common)
    
    return df_clean

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names to lowercase with underscores.
    
    Args:
        df: DataFrame with potentially inconsistent column names
    
    Returns:
        DataFrame with standardized column names
    """
    df_clean = df.copy()
    
    # Create mapping for common column name variations
    column_mapping = {
        'Country': 'country_code',
        'Country Code': 'country_code',
        'CountryName': 'country_name',
        'Country Name': 'country_name',
        'Year': 'year',
        'Gini': 'gini',
        'Gini Coefficient': 'gini',
        'GiniIndex': 'gini',
        'Top10Share': 'top_10_share',
        'Top 10 Share': 'top_10_share',
        'Top10': 'top_10_share',
        'Bottom50Share': 'bottom_50_share',
        'Bottom 50 Share': 'bottom_50_share',
        'Bottom50': 'bottom_50_share',
        'Top1Share': 'top_1_share',
        'Top 1 Share': 'top_1_share',
        'Top1': 'top_1_share',
        'PalmaRatio': 'palma_ratio',
        'Palma Ratio': 'palma_ratio',
        'Source': 'source',
        'DataSource': 'source'
    }
    
    # Rename columns
    df_clean = df_clean.rename(columns=column_mapping)
    
    # Convert remaining column names to lowercase with underscores
    df_clean.columns = [col.lower().replace(' ', '_') for col in df_clean.columns]
    
    return df_clean

def validate_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and convert data types for inequality data.
    
    Args:
        df: DataFrame with potentially incorrect data types
    
    Returns:
        DataFrame with correct data types
    """
    df_clean = df.copy()
    
    # Convert year to integer
    if 'year' in df_clean.columns:
        df_clean['year'] = pd.to_numeric(df_clean['year'], errors='coerce').astype('Int64')
    
    # Convert numeric columns
    numeric_columns = ['gini', 'top_10_share', 'bottom_50_share', 'top_1_share', 'palma_ratio']
    
    for col in numeric_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Ensure country codes are strings
    if 'country_code' in df_clean.columns:
        df_clean['country_code'] = df_clean['country_code'].astype(str)
    
    # Ensure country names are strings
    if 'country_name' in df_clean.columns:
        df_clean['country_name'] = df_clean['country_name'].astype(str)
    
    # Ensure source is string
    if 'source' in df_clean.columns:
        df_clean['source'] = df_clean['source'].astype(str)
    
    return df_clean

def filter_by_year_range(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Filter DataFrame by year range.
    
    Args:
        df: DataFrame with year column
        start_year: Start year (inclusive)
        end_year: End year (inclusive)
    
    Returns:
        Filtered DataFrame
    """
    if 'year' not in df.columns:
        logger.warning("No 'year' column found in DataFrame")
        return df
    
    df_filtered = df[
        (df['year'] >= start_year) & 
        (df['year'] <= end_year)
    ].copy()
    
    logger.info(f"Filtered data from {start_year} to {end_year}: {len(df_filtered)} rows")
    return df_filtered

def filter_by_countries(df: pd.DataFrame, country_codes: List[str]) -> pd.DataFrame:
    """
    Filter DataFrame by country codes.
    
    Args:
        df: DataFrame with country_code column
        country_codes: List of country codes to include
    
    Returns:
        Filtered DataFrame
    """
    if 'country_code' not in df.columns:
        logger.warning("No 'country_code' column found in DataFrame")
        return df
    
    df_filtered = df[df['country_code'].isin(country_codes)].copy()
    
    logger.info(f"Filtered data for {len(country_codes)} countries: {len(df_filtered)} rows")
    return df_filtered

def merge_data_sources(dataframes: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merge data from multiple sources into a single DataFrame.
    
    Args:
        dataframes: Dictionary with source names as keys and DataFrames as values
    
    Returns:
        Merged DataFrame
    """
    if not dataframes:
        return pd.DataFrame()
    
    # Clean all dataframes
    cleaned_dfs = {}
    for source, df in dataframes.items():
        if not df.empty:
            df_clean = clean_inequality_data(df)
            df_clean['source'] = source
            cleaned_dfs[source] = df_clean
    
    if not cleaned_dfs:
        return pd.DataFrame()
    
    # Concatenate all dataframes
    merged_df = pd.concat(cleaned_dfs.values(), ignore_index=True)
    
    # Remove duplicates based on country, year, and metric
    key_columns = ['country_code', 'year']
    if 'gini' in merged_df.columns:
        key_columns.append('gini')
    
    merged_df = merged_df.drop_duplicates(subset=key_columns, keep='first')
    
    logger.info(f"Merged data from {len(cleaned_dfs)} sources: {len(merged_df)} rows")
    return merged_df

def validate_inequality_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate inequality metrics for logical consistency.
    
    Args:
        df: DataFrame with inequality metrics
    
    Returns:
        DataFrame with validated metrics
    """
    df_valid = df.copy()
    
    # Validate Gini coefficient (should be between 0 and 1)
    if 'gini' in df_valid.columns:
        invalid_gini = df_valid[
            (df_valid['gini'] < 0) | (df_valid['gini'] > 1)
        ]
        if not invalid_gini.empty:
            logger.warning(f"Found {len(invalid_gini)} rows with invalid Gini values")
            df_valid = df_valid[
                (df_valid['gini'] >= 0) & (df_valid['gini'] <= 1)
            ]
    
    # Validate income shares (should be between 0 and 1)
    share_columns = ['top_10_share', 'bottom_50_share', 'top_1_share']
    for col in share_columns:
        if col in df_valid.columns:
            invalid_shares = df_valid[
                (df_valid[col] < 0) | (df_valid[col] > 1)
            ]
            if not invalid_shares.empty:
                logger.warning(f"Found {len(invalid_shares)} rows with invalid {col} values")
                df_valid = df_valid[
                    (df_valid[col] >= 0) & (df_valid[col] <= 1)
                ]
    
    # Validate Palma ratio (should be positive)
    if 'palma_ratio' in df_valid.columns:
        invalid_palma = df_valid[df_valid['palma_ratio'] < 0]
        if not invalid_palma.empty:
            logger.warning(f"Found {len(invalid_palma)} rows with invalid Palma ratio values")
            df_valid = df_valid[df_valid['palma_ratio'] >= 0]
    
    return df_valid

def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived inequality metrics to the DataFrame.
    
    Args:
        df: DataFrame with basic inequality metrics
    
    Returns:
        DataFrame with additional derived metrics
    """
    df_enhanced = df.copy()
    
    # Calculate Palma ratio if not present but we have top 10% and bottom 50% shares
    if 'palma_ratio' not in df_enhanced.columns and 'top_10_share' in df_enhanced.columns and 'bottom_50_share' in df_enhanced.columns:
        df_enhanced['palma_ratio'] = df_enhanced['top_10_share'] / df_enhanced['bottom_50_share']
        logger.info("Added Palma ratio calculation")
    
    # Calculate middle 40% share if we have top 10% and bottom 50% shares
    if 'top_10_share' in df_enhanced.columns and 'bottom_50_share' in df_enhanced.columns:
        df_enhanced['middle_40_share'] = 1 - df_enhanced['top_10_share'] - df_enhanced['bottom_50_share']
        logger.info("Added middle 40% share calculation")
    
    # Calculate inequality ratio (top 10% / bottom 10% if available)
    if 'top_10_share' in df_enhanced.columns and 'bottom_10_share' in df_enhanced.columns:
        df_enhanced['inequality_ratio'] = df_enhanced['top_10_share'] / df_enhanced['bottom_10_share']
        logger.info("Added inequality ratio calculation")
    
    return df_enhanced 