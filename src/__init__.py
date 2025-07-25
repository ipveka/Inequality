"""
Inequality Visualization Package

A comprehensive Python package for collecting, analyzing, and visualizing
inequality data from various public sources including World Bank, OECD,
WID.world, and Eurostat.
"""

__version__ = "0.1.0"
__author__ = "Inequality Visualization Team"

from .data_fetch import fetch_world_bank_gini, fetch_oecd_data, fetch_wid_data
from .data_cleaning import clean_inequality_data, normalize_country_codes
from .metrics import gini_coefficient, palma_ratio, income_shares, lorenz_curve_data
from .visualization import plot_lorenz_curve, plot_gini_by_country, plot_income_shares

__all__ = [
    "fetch_world_bank_gini",
    "fetch_oecd_data", 
    "fetch_wid_data",
    "clean_inequality_data",
    "normalize_country_codes",
    "gini_coefficient",
    "palma_ratio",
    "income_shares",
    "lorenz_curve_data",
    "plot_lorenz_curve",
    "plot_gini_by_country",
    "plot_income_shares",
] 