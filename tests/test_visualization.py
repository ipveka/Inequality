#!/usr/bin/env python3
"""
Unit tests for visualization components.

This module tests:
- Interactive line plot creation with Plotly
- Data table formatting and display
- Empty data handling and edge cases
- Chart styling and accessibility features
"""

import pandas as pd
import sys
import os
import plotly.graph_objects as go
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.visualization import create_gini_line_plot, create_gini_table, format_gini_data


class TestVisualization:
    """Test suite for visualization functions."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        self.sample_data = pd.DataFrame({
            'year': [2015, 2016, 2017, 2018, 2019, 2020],
            'value': [45.2, 44.8, 44.5, 44.1, 43.9, 43.7],
            'country_code': ['USA'] * 6
        })
        
        self.empty_data = pd.DataFrame(columns=['year', 'value', 'country_code'])
        
        self.missing_data = pd.DataFrame({
            'year': [2015, 2016, 2017, 2018],
            'value': [45.2, None, 44.5, None],
            'country_code': ['USA'] * 4
        })
    
    def test_create_gini_line_plot_with_data(self):
        """Test line plot creation with valid data."""
        fig = create_gini_line_plot(self.sample_data, "United States")
        
        # Check that figure is created
        assert isinstance(fig, go.Figure)
        
        # Check that figure has data
        assert len(fig.data) == 1
        
        # Check data content
        trace = fig.data[0]
        assert len(trace.x) == 6
        assert len(trace.y) == 6
        assert trace.mode == 'lines+markers'
        
        # Check styling
        assert trace.line.color == '#1f77b4'
        assert trace.line.width == 3
        assert trace.marker.size == 8
        
        # Check layout
        assert "United States" in fig.layout.title.text
        assert fig.layout.xaxis.title.text == "Year"
        assert fig.layout.yaxis.title.text == "Gini Coefficient"
        assert fig.layout.height == 500
    
    def test_create_gini_line_plot_empty_data(self):
        """Test line plot creation with empty data."""
        fig = create_gini_line_plot(self.empty_data, "Test Country")
        
        # Should still create a figure
        assert isinstance(fig, go.Figure)
        
        # Should have annotation for no data
        assert len(fig.layout.annotations) > 0
        assert "No Gini coefficient data available" in fig.layout.annotations[0].text
    
    def test_create_gini_line_plot_missing_values(self):
        """Test line plot creation with missing values."""
        fig = create_gini_line_plot(self.missing_data, "Test Country")
        
        # Should create figure and filter out missing values
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        
        # Should only have 2 data points (non-missing values)
        trace = fig.data[0]
        assert len(trace.x) == 2
        assert len(trace.y) == 2
    
    def test_create_gini_table_with_data(self):
        """Test table creation with valid data."""
        table = create_gini_table(self.sample_data)
        
        # Check that DataFrame is returned
        assert isinstance(table, pd.DataFrame)
        
        # Check structure
        assert len(table) == 6
        assert list(table.columns) == ['Year', 'Gini Coefficient']
        
        # Check data types
        assert table['Year'].dtype == int
        assert table['Gini Coefficient'].dtype == float
        
        # Check sorting (most recent first)
        assert table['Year'].iloc[0] == 2020
        assert table['Year'].iloc[-1] == 2015
        
        # Check decimal formatting
        assert all(table['Gini Coefficient'] == table['Gini Coefficient'].round(2))
    
    def test_create_gini_table_empty_data(self):
        """Test table creation with empty data."""
        table = create_gini_table(self.empty_data)
        
        # Should return empty DataFrame with correct columns
        assert isinstance(table, pd.DataFrame)
        assert len(table) == 0
        assert list(table.columns) == ['Year', 'Gini Coefficient']
    
    def test_create_gini_table_missing_values(self):
        """Test table creation with missing values."""
        table = create_gini_table(self.missing_data)
        
        # Should filter out missing values
        assert isinstance(table, pd.DataFrame)
        assert len(table) == 2  # Only non-missing values
        
        # Check that no NaN values remain
        assert not table['Gini Coefficient'].isna().any()
    
    def test_format_gini_data_valid_input(self):
        """Test data formatting with valid input."""
        raw_data = {
            'data': [
                {'date': '2020', 'value': 35.5, 'country': {'id': 'USA'}},
                {'date': '2019', 'value': 36.0, 'country': {'id': 'USA'}},
                {'date': '2018', 'value': None, 'country': {'id': 'USA'}},  # Missing value
            ]
        }
        
        df = format_gini_data(raw_data)
        
        # Should process valid entries
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2  # Filtered out missing value
        assert list(df.columns) == ['year', 'value', 'country_code']
        
        # Check data processing
        assert df['year'].iloc[0] == 2018  # Should be sorted
        assert df['country_code'].iloc[0] == 'USA'
    
    def test_format_gini_data_empty_input(self):
        """Test data formatting with empty input."""
        df = format_gini_data({})
        
        # Should return empty DataFrame with correct structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ['year', 'value', 'country_code']
    
    def test_format_gini_data_scale_conversion(self):
        """Test Gini value scale conversion (0-1 to 0-100)."""
        raw_data = {
            'data': [
                {'date': '2020', 'value': 0.355, 'country': {'id': 'USA'}},  # 0-1 scale
                {'date': '2019', 'value': 36.0, 'country': {'id': 'USA'}},   # 0-100 scale
            ]
        }
        
        df = format_gini_data(raw_data)
        
        # Should convert 0-1 scale to 0-100 scale
        values = sorted(df['value'].tolist())
        assert values[0] == 35.5  # 0.355 * 100
        assert values[1] == 36.0  # Already in 0-100 scale


def test_line_plot_requirements():
    """Test that line plot meets all requirements."""
    print("Testing line plot requirements...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'year': [2010, 2012, 2014, 2016, 2018, 2020],
        'value': [35.2, 36.1, 34.8, 37.2, 36.9, 35.5],
        'country_code': ['USA'] * 6
    })
    
    try:
        # Test chart creation
        fig = create_gini_line_plot(sample_data, "United States")
        
        # Requirement 2.1: Display line plot for selected country
        assert isinstance(fig, go.Figure), "Should create Plotly figure"
        assert len(fig.data) == 1, "Should have one data trace"
        print("✓ Requirement 2.1: Line plot displays for selected country")
        
        # Requirement 2.2: Clear x-axis (years) and y-axis (Gini values)
        assert fig.layout.xaxis.title.text == "Year", "X-axis should be labeled 'Year'"
        assert fig.layout.yaxis.title.text == "Gini Coefficient", "Y-axis should be labeled 'Gini Coefficient'"
        print("✓ Requirement 2.2: Clear axis labels")
        
        # Requirement 2.3: Hover tooltips with exact values
        trace = fig.data[0]
        assert 'hovertemplate' in trace, "Should have hover template"
        assert '%{x}' in trace.hovertemplate, "Should show x values in hover"
        assert '%{y' in trace.hovertemplate, "Should show y values in hover"
        print("✓ Requirement 2.3: Hover tooltips with exact values")
        
        # Requirement 2.5: Professional styling
        assert trace.line.color == '#1f77b4', "Should use professional color"
        assert trace.line.width == 3, "Should have appropriate line width"
        assert fig.layout.height == 500, "Should have fixed height"
        print("✓ Requirement 2.5: Professional styling")
        
        print("✅ All line plot requirements met!")
        return True
        
    except Exception as e:
        print(f"❌ Line plot test failed: {e}")
        return False


def test_table_requirements():
    """Test that table meets all requirements."""
    print("\\nTesting table requirements...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'year': [2018, 2020, 2019, 2017],  # Unsorted to test sorting
        'value': [35.234, 36.789, 34.567, 37.123],  # Unrounded to test formatting
        'country_code': ['USA'] * 4
    })
    
    try:
        # Test table creation
        table = create_gini_table(sample_data)
        
        # Requirement 3.1: Table shows year and Gini values
        assert isinstance(table, pd.DataFrame), "Should return DataFrame"
        assert 'Year' in table.columns, "Should have Year column"
        assert 'Gini Coefficient' in table.columns, "Should have Gini Coefficient column"
        print("✓ Requirement 3.1: Table shows year and Gini values")
        
        # Requirement 3.2: Chronological sorting by year
        years = table['Year'].tolist()
        assert years == sorted(years, reverse=True), "Should be sorted chronologically (newest first)"
        print("✓ Requirement 3.2: Chronological sorting")
        
        # Requirement 3.3: Proper decimal formatting
        gini_values = table['Gini Coefficient'].tolist()
        for value in gini_values:
            assert len(str(value).split('.')[-1]) <= 2, "Should have max 2 decimal places"
        print("✓ Requirement 3.3: Proper decimal formatting")
        
        print("✅ All table requirements met!")
        return True
        
    except Exception as e:
        print(f"❌ Table test failed: {e}")
        return False


def test_empty_data_handling():
    """Test handling of empty data."""
    print("\\nTesting empty data handling...")
    
    empty_data = pd.DataFrame(columns=['year', 'value', 'country_code'])
    
    try:
        # Test empty data with line plot
        fig = create_gini_line_plot(empty_data, "Test Country")
        assert isinstance(fig, go.Figure), "Should create figure even with empty data"
        assert len(fig.layout.annotations) > 0, "Should show no data message"
        print("✓ Line plot handles empty data gracefully")
        
        # Test empty data with table
        table = create_gini_table(empty_data)
        assert isinstance(table, pd.DataFrame), "Should return DataFrame even with empty data"
        assert len(table) == 0, "Should be empty table"
        assert list(table.columns) == ['Year', 'Gini Coefficient'], "Should have correct columns"
        print("✓ Table handles empty data gracefully")
        
        print("✅ Empty data handling works correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Empty data handling failed: {e}")
        return False


def test_comprehensive_functionality():
    """Run comprehensive tests for all visualization functions."""
    print("\\nTesting comprehensive visualization functionality...")
    
    try:
        # Run all test classes
        test_viz = TestVisualization()
        test_viz.setup_method()
        
        # Test line plots
        test_viz.test_create_gini_line_plot_with_data()
        test_viz.test_create_gini_line_plot_empty_data()
        test_viz.test_create_gini_line_plot_missing_values()
        
        # Test tables
        test_viz.test_create_gini_table_with_data()
        test_viz.test_create_gini_table_empty_data()
        test_viz.test_create_gini_table_missing_values()
        
        # Test data formatting
        test_viz.test_format_gini_data_valid_input()
        test_viz.test_format_gini_data_empty_input()
        test_viz.test_format_gini_data_scale_conversion()
        
        print("✅ All comprehensive visualization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive visualization tests failed: {e}")
        return False


def main():
    """Run all visualization tests."""
    print("🎨 Testing Visualization Components")
    print("=" * 50)
    
    results = []
    
    # Run individual test suites
    results.append(test_line_plot_requirements())
    results.append(test_table_requirements())
    results.append(test_empty_data_handling())
    results.append(test_comprehensive_functionality())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\\n📊 Visualization Test Summary:")
    print(f"   Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All visualization tests passed!")
        return True
    else:
        print("❌ Some visualization tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)