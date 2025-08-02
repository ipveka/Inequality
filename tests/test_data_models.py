#!/usr/bin/env python3
"""
Unit tests for data models and processing utilities.

This module tests:
- Data model classes (Country, GiniDataPoint, GiniTimeSeries)
- Validation functions for data integrity
- Data processing and transformation utilities
- Summary statistics generation
"""

import pandas as pd
import sys
import os
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_models import (
    Country, GiniDataPoint, GiniTimeSeries,
    validate_gini_value, validate_year, validate_country_code,
    convert_api_response_to_dataframe, clean_gini_data,
    handle_missing_values, format_data_for_visualization,
    create_gini_data_points, get_data_summary
)


class TestDataModels:
    """Test suite for data model classes."""
    
    def test_country_model(self):
        """Test Country data model."""
        # Valid country
        country = Country(code="USA", name="United States", region="North America")
        assert country.code == "USA"
        assert country.name == "United States"
        assert country.region == "North America"
        
        # Test code normalization
        country_lower = Country(code="usa", name="United States", region="North America")
        assert country_lower.code == "USA"
        
        # Test validation
        with pytest.raises(ValueError):
            Country(code="", name="United States", region="North America")
        
        with pytest.raises(ValueError):
            Country(code="USA", name="", region="North America")
    
    def test_gini_data_point_model(self):
        """Test GiniDataPoint data model."""
        # Valid data point
        point = GiniDataPoint(year=2020, value=35.5, country_code="USA")
        assert point.year == 2020
        assert point.value == 35.5
        assert point.country_code == "USA"
        
        # Test country code normalization
        point_lower = GiniDataPoint(year=2020, value=35.5, country_code="usa")
        assert point_lower.country_code == "USA"
        
        # Test validation
        with pytest.raises(ValueError):
            GiniDataPoint(year=1950, value=35.5, country_code="USA")  # Invalid year
        
        with pytest.raises(ValueError):
            GiniDataPoint(year=2020, value=150, country_code="USA")  # Invalid Gini value
        
        with pytest.raises(ValueError):
            GiniDataPoint(year=2020, value=35.5, country_code="")  # Invalid country code
    
    def test_gini_time_series_model(self):
        """Test GiniTimeSeries data model."""
        country = Country(code="USA", name="United States", region="North America")
        data_points = [
            GiniDataPoint(year=2018, value=35.5, country_code="USA"),
            GiniDataPoint(year=2019, value=36.0, country_code="USA"),
            GiniDataPoint(year=2020, value=35.8, country_code="USA")
        ]
        
        time_series = GiniTimeSeries(country=country, data_points=data_points)
        
        # Test to_dataframe conversion
        df = time_series.to_dataframe()
        assert len(df) == 3
        assert list(df.columns) == ['year', 'value', 'country_code', 'country_name']
        assert df['country_name'].iloc[0] == "United States"
        
        # Test get_latest_value
        latest = time_series.get_latest_value()
        assert latest.year == 2020
        assert latest.value == 35.8
        
        # Test get_value_for_year
        value_2019 = time_series.get_value_for_year(2019)
        assert value_2019 == 36.0
        
        value_missing = time_series.get_value_for_year(2021)
        assert value_missing is None


class TestValidationFunctions:
    """Test suite for validation functions."""
    
    def test_validate_gini_value(self):
        """Test Gini value validation."""
        # Valid values
        assert validate_gini_value(35.5) == True
        assert validate_gini_value(0) == True
        assert validate_gini_value(100) == True
        assert validate_gini_value(0.355) == True  # 0-1 scale
        
        # Invalid values
        assert validate_gini_value(-5) == False
        assert validate_gini_value(150) == False
        assert validate_gini_value(None) == False
        assert validate_gini_value("invalid") == False
    
    def test_validate_year(self):
        """Test year validation."""
        # Valid years
        assert validate_year(2020) == True
        assert validate_year(1990) == True
        assert validate_year("2020") == True
        
        # Invalid years
        assert validate_year(1950) == False
        assert validate_year(2050) == False
        assert validate_year(None) == False
        assert validate_year("invalid") == False
    
    def test_validate_country_code(self):
        """Test country code validation."""
        # Valid codes
        assert validate_country_code("USA") == True
        assert validate_country_code("DEU") == True
        
        # Invalid codes
        assert validate_country_code("US") == False  # Too short
        assert validate_country_code("USAA") == False  # Too long
        assert validate_country_code("US1") == False  # Contains number
        assert validate_country_code("") == False
        assert validate_country_code(None) == False


class TestDataProcessing:
    """Test suite for data processing utilities."""
    
    def test_convert_api_response_to_dataframe(self):
        """Test API response conversion."""
        # Mock API response
        api_response = [
            {"date": "2020", "value": 35.5},
            {"date": "2019", "value": 36.0},
            {"date": "2018", "value": None},  # Missing value
            {"date": "invalid", "value": 37.0},  # Invalid year
        ]
        
        df = convert_api_response_to_dataframe(api_response, "USA")
        
        # Should filter out invalid entries
        assert len(df) == 2
        assert list(df.columns) == ['year', 'value', 'country_code']
        assert df['country_code'].iloc[0] == "USA"
        assert df['year'].iloc[0] == 2018  # Should be sorted
    
    def test_clean_gini_data(self):
        """Test data cleaning functionality."""
        # Create test data with issues
        dirty_data = pd.DataFrame({
            'year': [2020, 2019, 1950, 2018, 2020],  # Duplicate and invalid year
            'value': [35.5, 150, 36.0, 0.37, 35.5],  # Invalid and 0-1 scale values
            'country_code': ['usa', 'USA', 'USA', 'USA', 'USA']
        })
        
        cleaned_data = clean_gini_data(dirty_data)
        
        # Should remove invalid entries and normalize
        assert len(cleaned_data) == 3  # Removed invalid year and value, kept one duplicate
        assert all(cleaned_data['year'] >= 1960)
        assert all(cleaned_data['value'] <= 100)
        assert all(cleaned_data['country_code'] == 'USA')  # Normalized to uppercase
        
        # Check 0-1 scale conversion
        assert any(cleaned_data['value'] == 37.0)  # 0.37 * 100
    
    def test_handle_missing_values(self):
        """Test missing value handling."""
        # Create data with missing values
        data_with_missing = pd.DataFrame({
            'year': [2018, 2019, 2020, 2021],
            'value': [35.5, None, 36.0, None],
            'country_code': ['USA', 'USA', 'USA', 'USA']
        })
        
        # Test drop method
        dropped = handle_missing_values(data_with_missing, method='drop')
        assert len(dropped) == 2
        assert not dropped['value'].isna().any()
        
        # Test interpolate method
        interpolated = handle_missing_values(data_with_missing, method='interpolate')
        assert len(interpolated) == 3  # Should interpolate middle value, drop last
        assert not interpolated['value'].isna().any()
    
    def test_format_data_for_visualization(self):
        """Test data formatting for visualization."""
        # Create test data
        raw_data = pd.DataFrame({
            'year': [2020, 2019, 2018],
            'value': [35.5, 36.0, 34.8],
            'country_code': ['USA', 'USA', 'USA']
        })
        
        formatted = format_data_for_visualization(raw_data, "United States")
        
        # Check formatting
        assert 'country_name' in formatted.columns
        assert formatted['country_name'].iloc[0] == "United States"
        assert formatted['year'].dtype == int
        assert formatted['value'].dtype == float
        
        # Check sorting (should be chronological)
        assert formatted['year'].iloc[0] == 2018
        assert formatted['year'].iloc[-1] == 2020
    
    def test_create_gini_data_points(self):
        """Test GiniDataPoint creation from DataFrame."""
        df = pd.DataFrame({
            'year': [2020, 2019],
            'value': [35.5, 36.0],
            'country_code': ['USA', 'USA']
        })
        
        data_points = create_gini_data_points(df)
        
        assert len(data_points) == 2
        assert all(isinstance(point, GiniDataPoint) for point in data_points)
        assert data_points[0].year == 2020
        assert data_points[0].value == 35.5
    
    def test_get_data_summary(self):
        """Test data summary generation."""
        df = pd.DataFrame({
            'year': [2018, 2019, 2020],
            'value': [34.0, 36.0, 35.0],
            'country_code': ['USA', 'USA', 'USA']
        })
        
        summary = get_data_summary(df)
        
        assert summary['count'] == 3
        assert summary['year_range'] == (2018, 2020)
        assert summary['value_range'] == (34.0, 36.0)
        assert summary['mean_value'] == 35.0
        assert summary['latest_value'] == 35.0
        assert summary['trend'] in ['increasing', 'decreasing', 'stable']


def test_data_models():
    """Run all data model tests."""
    print("Testing data models...")
    
    # Run test classes
    test_models = TestDataModels()
    test_validation = TestValidationFunctions()
    test_processing = TestDataProcessing()
    
    try:
        # Test data models
        test_models.test_country_model()
        test_models.test_gini_data_point_model()
        test_models.test_gini_time_series_model()
        print("✓ Data model classes working correctly")
        
        # Test validation functions
        test_validation.test_validate_gini_value()
        test_validation.test_validate_year()
        test_validation.test_validate_country_code()
        print("✓ Validation functions working correctly")
        
        # Test data processing
        test_processing.test_convert_api_response_to_dataframe()
        test_processing.test_clean_gini_data()
        test_processing.test_handle_missing_values()
        test_processing.test_format_data_for_visualization()
        test_processing.test_create_gini_data_points()
        test_processing.test_get_data_summary()
        print("✓ Data processing utilities working correctly")
        
        print("✅ All data model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Data model tests failed: {e}")
        return False


if __name__ == "__main__":
    success = test_data_models()
    exit(0 if success else 1)