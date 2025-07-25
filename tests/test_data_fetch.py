"""
Unit tests for data fetching functions.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.data_fetch import (
    fetch_world_bank_gini,
    fetch_oecd_data,
    fetch_wid_data,
    fetch_eurostat_data,
    get_available_countries,
    fetch_all_sources_data,
    DataFetchError
)

class TestWorldBankDataFetch:
    """Test cases for World Bank data fetching."""
    
    @patch('src.data_fetch.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful data fetch from World Bank."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 50, "total": 1},
            [
                {
                    "indicator": {"id": "SI.POV.GINI", "value": "Gini index"},
                    "country": {"id": "USA", "value": "United States"},
                    "countryiso3code": "USA",
                    "date": "2020",
                    "value": 0.41,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the function
        result = fetch_world_bank_gini("USA", 2020, 2020)
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert len(result) == 1
        assert result.iloc[0]['country_code'] == 'USA'
        assert result.iloc[0]['year'] == 2020
        assert result.iloc[0]['gini'] == 0.41
        assert result.iloc[0]['source'] == 'World Bank'
    
    @patch('src.data_fetch.requests.get')
    def test_no_data_found(self, mock_get):
        """Test when no data is found."""
        # Mock response with no data
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 50, "total": 0},
            []
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the function
        result = fetch_world_bank_gini("XXX", 2020, 2020)
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    @patch('src.data_fetch.requests.get')
    def test_request_error(self, mock_get):
        """Test handling of request errors."""
        # Mock request error
        mock_get.side_effect = Exception("Network error")
        
        # Test the function
        with pytest.raises(DataFetchError):
            fetch_world_bank_gini("USA", 2020, 2020)
    
    def test_invalid_country_code(self):
        """Test with invalid country code."""
        # This should raise an error or return empty DataFrame
        # depending on the implementation
        pass

class TestOECDDataFetch:
    """Test cases for OECD data fetching."""
    
    def test_oecd_data_fetch(self):
        """Test OECD data fetching."""
        result = fetch_oecd_data()
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'country_code' in result.columns
        assert 'gini' in result.columns
        assert 'source' in result.columns
        assert all(result['source'] == 'OECD')
    
    def test_oecd_data_with_country_filter(self):
        """Test OECD data fetching with country filter."""
        result = fetch_oecd_data("USA")
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert all(result['country_code'] == 'USA')

class TestWIDDataFetch:
    """Test cases for WID.world data fetching."""
    
    def test_wid_data_fetch(self):
        """Test WID.world data fetching."""
        result = fetch_wid_data()
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'country_code' in result.columns
        assert 'gini' in result.columns
        assert 'palma_ratio' in result.columns
        assert 'source' in result.columns
        assert all(result['source'] == 'WID.world')
    
    def test_wid_data_with_country_filter(self):
        """Test WID.world data fetching with country filter."""
        result = fetch_wid_data("USA")
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert all(result['country_code'] == 'USA')

class TestEurostatDataFetch:
    """Test cases for Eurostat data fetching."""
    
    def test_eurostat_data_fetch(self):
        """Test Eurostat data fetching."""
        result = fetch_eurostat_data()
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'country_code' in result.columns
        assert 'gini' in result.columns
        assert 'source' in result.columns
        assert all(result['source'] == 'Eurostat')
    
    def test_eurostat_data_with_country_filter(self):
        """Test Eurostat data fetching with country filter."""
        result = fetch_eurostat_data("DEU")
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert all(result['country_code'] == 'DEU')

class TestAvailableCountries:
    """Test cases for available countries function."""
    
    def test_get_available_countries(self):
        """Test getting available countries."""
        countries = get_available_countries()
        
        # Verify the result
        assert isinstance(countries, list)
        assert len(countries) > 0
        assert all(isinstance(country, str) for country in countries)
        assert all(len(country) == 3 for country in countries)  # ISO 3-letter codes
        
        # Check for some expected countries
        expected_countries = ['USA', 'DEU', 'FRA', 'GBR']
        for country in expected_countries:
            assert country in countries

class TestFetchAllSourcesData:
    """Test cases for fetching data from all sources."""
    
    @patch('src.data_fetch.fetch_world_bank_gini')
    @patch('src.data_fetch.fetch_oecd_data')
    @patch('src.data_fetch.fetch_wid_data')
    @patch('src.data_fetch.fetch_eurostat_data')
    def test_fetch_all_sources_success(self, mock_eurostat, mock_wid, mock_oecd, mock_world_bank):
        """Test successful fetch from all sources."""
        # Mock successful responses
        mock_world_bank.return_value = pd.DataFrame({
            'country_code': ['USA'],
            'year': [2020],
            'gini': [0.41],
            'source': ['World Bank']
        })
        
        mock_oecd.return_value = pd.DataFrame({
            'country_code': ['USA'],
            'year': [2020],
            'gini': [0.42],
            'top_10_share': [0.47],
            'source': ['OECD']
        })
        
        mock_wid.return_value = pd.DataFrame({
            'country_code': ['USA'],
            'year': [2020],
            'gini': [0.43],
            'palma_ratio': [1.85],
            'source': ['WID.world']
        })
        
        mock_eurostat.return_value = pd.DataFrame()  # No Eurostat data for USA
        
        # Test the function
        result = fetch_all_sources_data("USA", 2020, 2020)
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'world_bank' in result
        assert 'oecd' in result
        assert 'wid' in result
        assert 'eurostat' in result
        
        # Check that each source returned a DataFrame
        for source, data in result.items():
            assert isinstance(data, pd.DataFrame)
    
    @patch('src.data_fetch.fetch_world_bank_gini')
    @patch('src.data_fetch.fetch_oecd_data')
    @patch('src.data_fetch.fetch_wid_data')
    @patch('src.data_fetch.fetch_eurostat_data')
    def test_fetch_all_sources_with_errors(self, mock_eurostat, mock_wid, mock_oecd, mock_world_bank):
        """Test fetch from all sources with some errors."""
        # Mock some successful and some failed responses
        mock_world_bank.side_effect = DataFetchError("World Bank error")
        mock_oecd.return_value = pd.DataFrame({
            'country_code': ['USA'],
            'year': [2020],
            'gini': [0.42],
            'source': ['OECD']
        })
        mock_wid.side_effect = DataFetchError("WID error")
        mock_eurostat.return_value = pd.DataFrame()
        
        # Test the function
        result = fetch_all_sources_data("USA", 2020, 2020)
        
        # Verify the result
        assert isinstance(result, dict)
        assert 'world_bank' in result
        assert 'oecd' in result
        assert 'wid' in result
        assert 'eurostat' in result
        
        # Check that failed sources return empty DataFrames
        assert result['world_bank'].empty
        assert not result['oecd'].empty
        assert result['wid'].empty
        assert result['eurostat'].empty

class TestDataFetchError:
    """Test cases for DataFetchError exception."""
    
    def test_data_fetch_error_creation(self):
        """Test creating DataFetchError."""
        error = DataFetchError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

class TestDataValidation:
    """Test cases for data validation."""
    
    def test_data_structure_validation(self):
        """Test that fetched data has the expected structure."""
        # Test World Bank data
        world_bank_data = fetch_world_bank_gini("USA", 2020, 2020)
        if not world_bank_data.empty:
            required_columns = ['country_code', 'country_name', 'year', 'gini', 'source']
            for col in required_columns:
                assert col in world_bank_data.columns
        
        # Test OECD data
        oecd_data = fetch_oecd_data()
        if not oecd_data.empty:
            required_columns = ['country_code', 'country_name', 'year', 'gini', 'source']
            for col in required_columns:
                assert col in oecd_data.columns
        
        # Test WID data
        wid_data = fetch_wid_data()
        if not wid_data.empty:
            required_columns = ['country_code', 'country_name', 'year', 'gini', 'source']
            for col in required_columns:
                assert col in wid_data.columns
    
    def test_data_value_validation(self):
        """Test that fetched data has reasonable values."""
        # Test Gini coefficient values
        oecd_data = fetch_oecd_data()
        if not oecd_data.empty and 'gini' in oecd_data.columns:
            gini_values = oecd_data['gini'].dropna()
            if not gini_values.empty:
                assert all(0 <= gini <= 1 for gini in gini_values)
        
        # Test year values
        wid_data = fetch_wid_data()
        if not wid_data.empty and 'year' in wid_data.columns:
            year_values = wid_data['year'].dropna()
            if not year_values.empty:
                assert all(1960 <= year <= 2024 for year in year_values)

if __name__ == "__main__":
    pytest.main([__file__]) 