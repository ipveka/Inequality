"""
Utility functions for the inequality visualization project.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Country code mappings
COUNTRY_CODES = {
    "USA": "United States",
    "DEU": "Germany", 
    "FRA": "France",
    "GBR": "United Kingdom",
    "ITA": "Italy",
    "ESP": "Spain",
    "CAN": "Canada",
    "AUS": "Australia",
    "JPN": "Japan",
    "BRA": "Brazil",
    "IND": "India",
    "CHN": "China",
    "RUS": "Russia",
    "MEX": "Mexico",
    "KOR": "South Korea",
    "NLD": "Netherlands",
    "SWE": "Sweden",
    "NOR": "Norway",
    "DNK": "Denmark",
    "FIN": "Finland"
}

def get_country_name(code: str) -> str:
    """Convert country code to full name."""
    return COUNTRY_CODES.get(code.upper(), code)

def get_country_code(name: str) -> str:
    """Convert country name to code."""
    reverse_mapping = {v: k for k, v in COUNTRY_CODES.items()}
    return reverse_mapping.get(name, name)

def validate_year_range(start_year: int, end_year: int) -> Tuple[int, int]:
    """Validate and return year range."""
    current_year = pd.Timestamp.now().year
    
    if start_year < 1960:
        start_year = 1960
        logger.warning(f"Start year adjusted to {start_year}")
    
    if end_year > current_year:
        end_year = current_year
        logger.warning(f"End year adjusted to {end_year}")
    
    if start_year > end_year:
        start_year, end_year = end_year, start_year
        logger.warning("Start and end years swapped")
    
    return start_year, end_year

def format_number(value: float, decimals: int = 2) -> str:
    """Format number with specified decimal places."""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}"

def calculate_percentage_change(current: float, previous: float) -> float:
    """Calculate percentage change between two values."""
    if previous == 0:
        return float('inf') if current > 0 else 0
    return ((current - previous) / previous) * 100

def get_data_directory() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent / "data"

def ensure_data_directory() -> Path:
    """Ensure data directory exists and return path."""
    data_dir = get_data_directory()
    data_dir.mkdir(exist_ok=True)
    return data_dir

def save_dataframe(df: pd.DataFrame, filename: str) -> None:
    """Save DataFrame to CSV in data directory."""
    data_dir = ensure_data_directory()
    filepath = data_dir / filename
    df.to_csv(filepath, index=False)
    logger.info(f"Data saved to {filepath}")

def load_dataframe(filename: str) -> Optional[pd.DataFrame]:
    """Load DataFrame from CSV in data directory."""
    data_dir = get_data_directory()
    filepath = data_dir / filename
    
    if filepath.exists():
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Data loaded from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return None
    else:
        logger.warning(f"File not found: {filepath}")
        return None

def get_continent_mapping() -> Dict[str, List[str]]:
    """Get mapping of continents to country codes."""
    return {
        "Europe": ["DEU", "FRA", "GBR", "ITA", "ESP", "NLD", "SWE", "NOR", "DNK", "FIN"],
        "North America": ["USA", "CAN", "MEX"],
        "Asia": ["JPN", "CHN", "IND", "KOR", "RUS"],
        "South America": ["BRA"],
        "Oceania": ["AUS"],
        "Africa": []  # Add African countries as needed
    }

def filter_by_continent(df: pd.DataFrame, continent: str) -> pd.DataFrame:
    """Filter DataFrame by continent."""
    continent_mapping = get_continent_mapping()
    if continent in continent_mapping:
        country_codes = continent_mapping[continent]
        return df[df['country_code'].isin(country_codes)]
    return df

def get_metric_description(metric: str) -> str:
    """Get description for inequality metrics."""
    descriptions = {
        "gini": "Gini measures income inequality on a scale from 0 (equality) to 1 (inequality)",
        "palma": "Palma ratio is the ratio of the richest 10% to the poorest 40% of the population",
        "top_10_share": "Share of total income held by the top 10% of the population",
        "bottom_50_share": "Share of total income held by the bottom 50% of the population",
        "top_1_share": "Share of total income held by the top 1% of the population"
    }
    return descriptions.get(metric, "No description available")

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validate DataFrame has required columns."""
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False
    return True 