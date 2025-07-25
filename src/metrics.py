"""
Functions to compute inequality metrics including Gini coefficient, Palma ratio, and income shares.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from scipy import stats
from .utils import logger

def gini_coefficient(values: List[float]) -> float:
    """
    Calculate the Gini coefficient for a list of values.
    
    The Gini coefficient measures inequality on a scale from 0 (perfect equality) 
    to 1 (perfect inequality).
    
    Args:
        values: List of numeric values (e.g., incomes)
    
    Returns:
        Gini coefficient as a float between 0 and 1
    
    Raises:
        ValueError: If values list is empty or contains non-positive values
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    # Convert to numpy array and filter out non-positive values
    values = np.array(values)
    values = values[values > 0]
    
    if len(values) == 0:
        raise ValueError("No positive values found")
    
    # Sort values in ascending order
    values = np.sort(values)
    
    n = len(values)
    if n == 1:
        return 0.0  # Perfect equality for single value
    
    # Handle case where all values are the same (perfect equality)
    if np.all(values == values[0]):
        return 0.0
    
    # Handle case where only one value is non-zero (perfect inequality)
    non_zero_values = values[values > 0]
    if len(non_zero_values) == 1 and len(values) > 1:
        return 1.0
    
    # Calculate Gini coefficient using the formula:
    # G = (2 * sum(i * x_i) - (n + 1) * sum(x_i)) / (n * sum(x_i))
    # where i is the rank and x_i is the value
    numerator = 2 * np.sum(np.arange(1, n + 1) * values) - (n + 1) * np.sum(values)
    denominator = n * np.sum(values)
    
    gini = numerator / denominator
    
    # Ensure result is between 0 and 1
    return max(0.0, min(1.0, gini))

def palma_ratio(values: List[float]) -> float:
    """
    Calculate the Palma ratio for a list of values.
    
    The Palma ratio is the ratio of the richest 10% to the poorest 40% of the population.
    
    Args:
        values: List of numeric values (e.g., incomes)
    
    Returns:
        Palma ratio as a float
    
    Raises:
        ValueError: If values list is empty or contains non-positive values
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    # Convert to numpy array and filter out non-positive values
    values = np.array(values)
    values = values[values > 0]
    
    if len(values) == 0:
        raise ValueError("No positive values found")
    
    # Sort values in ascending order
    values = np.sort(values)
    n = len(values)
    
    if n < 10:
        raise ValueError("Need at least 10 values to calculate Palma ratio")
    
    # Calculate percentiles
    top_10_threshold = np.percentile(values, 90)  # 90th percentile
    bottom_40_threshold = np.percentile(values, 40)  # 40th percentile
    
    # Calculate shares
    top_10_share = np.sum(values[values >= top_10_threshold]) / np.sum(values)
    bottom_40_share = np.sum(values[values <= bottom_40_threshold]) / np.sum(values)
    
    # Avoid division by zero
    if bottom_40_share == 0:
        return float('inf') if top_10_share > 0 else 0.0
    
    return top_10_share / bottom_40_share

def income_shares(values: List[float], percentiles: List[float] = None) -> Dict[str, float]:
    """
    Calculate income shares for different percentiles of the population.
    
    Args:
        values: List of numeric values (e.g., incomes)
        percentiles: List of percentiles to calculate (default: [1, 10, 50, 90, 99])
    
    Returns:
        Dictionary with percentile names as keys and shares as values
    
    Raises:
        ValueError: If values list is empty or contains non-positive values
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    if percentiles is None:
        percentiles = [1, 10, 50, 90, 99]
    
    # Convert to numpy array and filter out non-positive values
    values = np.array(values)
    values = values[values > 0]
    
    if len(values) == 0:
        raise ValueError("No positive values found")
    
    # Sort values in ascending order
    values = np.sort(values)
    total_income = np.sum(values)
    
    if total_income == 0:
        raise ValueError("Total income cannot be zero")
    
    shares = {}
    
    for percentile in percentiles:
        if percentile < 0 or percentile > 100:
            continue
            
        threshold = np.percentile(values, percentile)
        
        if percentile == 100:
            # For 100th percentile, include all values
            share = 1.0
        else:
            # Calculate share of income below this percentile
            share = np.sum(values[values <= threshold]) / total_income
        
        shares[f'p{percentile}'] = share
    
    # Calculate specific shares commonly used in inequality analysis
    if 1 in percentiles and 10 in percentiles:
        shares['top_1_share'] = 1 - shares['p99']
        shares['top_10_share'] = 1 - shares['p90']
    
    if 50 in percentiles:
        shares['bottom_50_share'] = shares['p50']
    
    return shares

def lorenz_curve_data(values: List[float], num_points: int = 100) -> Tuple[List[float], List[float]]:
    """
    Generate data points for plotting a Lorenz curve.
    
    The Lorenz curve shows the cumulative distribution of income.
    
    Args:
        values: List of numeric values (e.g., incomes)
        num_points: Number of points to generate for the curve
    
    Returns:
        Tuple of (cumulative population share, cumulative income share)
    
    Raises:
        ValueError: If values list is empty or contains non-positive values
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    # Convert to numpy array and filter out non-positive values
    values = np.array(values)
    values = values[values > 0]
    
    if len(values) == 0:
        raise ValueError("No positive values found")
    
    # Sort values in ascending order
    values = np.sort(values)
    n = len(values)
    total_income = np.sum(values)
    
    if total_income == 0:
        raise ValueError("Total income cannot be zero")
    
    # Generate population shares
    population_shares = np.linspace(0, 1, num_points)
    
    # Calculate cumulative income shares
    income_shares = []
    for p in population_shares:
        if p == 0:
            income_shares.append(0.0)
        elif p == 1:
            income_shares.append(1.0)
        else:
            # Find the index corresponding to this population share
            index = int(p * n)
            if index >= n:
                index = n - 1
            
            # Calculate cumulative income share
            cumulative_income = np.sum(values[:index + 1])
            income_share = cumulative_income / total_income
            income_shares.append(income_share)
    
    return population_shares.tolist(), income_shares

def theil_index(values: List[float]) -> float:
    """
    Calculate the Theil index for a list of values.
    
    The Theil index is another measure of inequality that is more sensitive
    to changes in the upper tail of the distribution.
    
    Args:
        values: List of numeric values (e.g., incomes)
    
    Returns:
        Theil index as a float (≥ 0)
    
    Raises:
        ValueError: If values list is empty or contains non-positive values
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    # Convert to numpy array and filter out non-positive values
    values = np.array(values)
    values = values[values > 0]
    
    if len(values) == 0:
        raise ValueError("No positive values found")
    
    n = len(values)
    mean_income = np.mean(values)
    
    if mean_income == 0:
        return 0.0
    
    # Calculate Theil index
    theil = np.sum((values / mean_income) * np.log(values / mean_income)) / n
    
    return max(0.0, theil)

def atkinson_index(values: List[float], epsilon: float = 1.0) -> float:
    """
    Calculate the Atkinson index for a list of values.
    
    The Atkinson index is a measure of inequality that allows for different
    degrees of inequality aversion through the epsilon parameter.
    
    Args:
        values: List of numeric values (e.g., incomes)
        epsilon: Inequality aversion parameter (ε > 0, ε ≠ 1)
    
    Returns:
        Atkinson index as a float between 0 and 1
    
    Raises:
        ValueError: If values list is empty, contains non-positive values, or epsilon ≤ 0
    """
    if not values:
        raise ValueError("Values list cannot be empty")
    
    if epsilon <= 0:
        raise ValueError("Epsilon must be positive")
    
    # Convert to numpy array and filter out non-positive values
    values = np.array(values)
    values = values[values > 0]
    
    if len(values) == 0:
        raise ValueError("No positive values found")
    
    n = len(values)
    mean_income = np.mean(values)
    
    if epsilon == 1:
        # Special case for epsilon = 1
        atkinson = 1 - np.exp(np.mean(np.log(values))) / mean_income
    else:
        # General case
        atkinson = 1 - (np.mean(values ** (1 - epsilon)) ** (1 / (1 - epsilon))) / mean_income
    
    return max(0.0, min(1.0, atkinson))

def calculate_all_metrics(values: List[float]) -> Dict[str, float]:
    """
    Calculate all inequality metrics for a given dataset.
    
    Args:
        values: List of numeric values (e.g., incomes)
    
    Returns:
        Dictionary containing all calculated metrics
    """
    try:
        metrics = {}
        
        # Basic metrics
        metrics['gini'] = gini_coefficient(values)
        metrics['palma_ratio'] = palma_ratio(values)
        metrics['theil_index'] = theil_index(values)
        metrics['atkinson_index'] = atkinson_index(values)
        
        # Income shares
        shares = income_shares(values)
        metrics.update(shares)
        
        # Additional derived metrics
        if 'top_10_share' in shares and 'bottom_50_share' in shares:
            metrics['palma_ratio_manual'] = shares['top_10_share'] / shares['bottom_50_share']
        
        if 'top_1_share' in shares and 'bottom_50_share' in shares:
            metrics['top_1_vs_bottom_50'] = shares['top_1_share'] / shares['bottom_50_share']
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {}

def validate_metric_values(metrics: Dict[str, float]) -> Dict[str, bool]:
    """
    Validate that calculated metrics are within expected ranges.
    
    Args:
        metrics: Dictionary of calculated metrics
    
    Returns:
        Dictionary indicating which metrics are valid
    """
    validation = {}
    
    # Gini coefficient should be between 0 and 1
    if 'gini' in metrics:
        validation['gini'] = 0 <= metrics['gini'] <= 1
    
    # Palma ratio should be positive
    if 'palma_ratio' in metrics:
        validation['palma_ratio'] = metrics['palma_ratio'] >= 0
    
    # Theil index should be non-negative
    if 'theil_index' in metrics:
        validation['theil_index'] = metrics['theil_index'] >= 0
    
    # Atkinson index should be between 0 and 1
    if 'atkinson_index' in metrics:
        validation['atkinson_index'] = 0 <= metrics['atkinson_index'] <= 1
    
    # Income shares should be between 0 and 1
    share_metrics = ['top_1_share', 'top_10_share', 'bottom_50_share']
    for metric in share_metrics:
        if metric in metrics:
            validation[metric] = 0 <= metrics[metric] <= 1
    
    return validation 