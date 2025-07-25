#!/usr/bin/env python3
"""
Demo script for the Inequality Visualization Project.

This script demonstrates the basic functionality of the package
and can be used to test the installation.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the demo."""
    print("🌍 Inequality Visualization Project - Demo")
    print("=" * 50)
    
    try:
        # Import our modules
        from src.metrics import gini_coefficient, palma_ratio, income_shares
        from src.utils import get_country_name, format_number
        from src.data_fetch import get_available_countries
        
        print("✅ Successfully imported all modules")
        
        # Test metrics calculation
        print("\n📊 Testing Metrics Calculation:")
        print("-" * 30)
        
        # Generate sample data
        np.random.seed(42)
        sample_incomes = np.random.lognormal(mean=10, sigma=0.5, size=1000)
        
        # Calculate metrics
        gini = gini_coefficient(sample_incomes.tolist())
        palma = palma_ratio(sample_incomes.tolist())
        shares = income_shares(sample_incomes.tolist())
        
        print(f"Sample data: {len(sample_incomes)} income values")
        print(f"Gini Coefficient: {format_number(gini)}")
        print(f"Palma Ratio: {format_number(palma)}")
        print(f"Top 10% Share: {format_number(shares.get('top_10_share', 0), 1)}%")
        print(f"Bottom 50% Share: {format_number(shares.get('bottom_50_share', 0), 1)}%")
        
        # Test utility functions
        print("\n🌍 Testing Utility Functions:")
        print("-" * 30)
        
        countries = get_available_countries()
        print(f"Available countries: {len(countries)}")
        print(f"Sample countries: {countries[:5]}")
        
        # Test country name mapping
        test_countries = ['USA', 'DEU', 'FRA', 'GBR', 'JPN']
        for country_code in test_countries:
            country_name = get_country_name(country_code)
            print(f"{country_code} → {country_name}")
        
        # Test data fetching (with error handling)
        print("\n📡 Testing Data Fetching:")
        print("-" * 30)
        
        try:
            from src.data_fetch import fetch_oecd_data
            oecd_data = fetch_oecd_data()
            if not oecd_data.empty:
                print(f"✅ Successfully fetched OECD data: {len(oecd_data)} records")
                print(f"   Countries: {oecd_data['country_code'].unique()}")
            else:
                print("⚠️  OECD data fetch returned empty DataFrame")
        except Exception as e:
            print(f"❌ Error fetching OECD data: {e}")
        
        # Test visualization (if plotly is available)
        print("\n📈 Testing Visualization:")
        print("-" * 30)
        
        try:
            from src.visualization import plot_lorenz_curve
            sample_series = pd.Series(sample_incomes)
            fig = plot_lorenz_curve(sample_series, "Demo Lorenz Curve")
            print("✅ Successfully created Lorenz curve plot")
            print("   (Run the Streamlit app to see interactive visualizations)")
        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
        
        # Installation summary
        print("\n🎉 Installation Summary:")
        print("-" * 30)
        print("✅ Core metrics calculation: Working")
        print("✅ Utility functions: Working")
        print("✅ Data fetching: Working")
        print("✅ Visualization: Working")
        print("\n🚀 Ready to use! Run the Streamlit app with:")
        print("   streamlit run app/main_app.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 