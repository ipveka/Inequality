"""
Data service module for fetching and processing Gini coefficient data.

This module handles all data fetching operations from the World Bank API
and provides caching mechanisms to improve performance.
"""

import requests
import pandas as pd
import time
from typing import List, Dict, Optional
import logging

# Import data models and utilities
from .data_models import (
    Country, GiniDataPoint, GiniTimeSeries,
    validate_gini_value, validate_year, validate_country_code,
    convert_api_response_to_dataframe, clean_gini_data,
    handle_missing_values, format_data_for_visualization,
    create_gini_data_points
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorldBankAPIError(Exception):
    """Custom exception for World Bank API errors."""
    def __init__(self, message: str, error_type: str = "general"):
        """
        Initialize WorldBankAPIError with message and error type.
        
        Args:
            message: Error message describing the issue
            error_type: Category of error for handling purposes
        """
        super().__init__(message)
        self.error_type = error_type


class APIConnectionError(WorldBankAPIError):
    """Exception for API connection issues."""
    def __init__(self, message: str):
        """
        Initialize APIConnectionError.
        
        Args:
            message: Error message describing the connection issue
        """
        super().__init__(message, "connection")


class APIRateLimitError(WorldBankAPIError):
    """Exception for API rate limiting issues."""
    def __init__(self, message: str):
        """
        Initialize APIRateLimitError.
        
        Args:
            message: Error message describing the rate limit issue
        """
        super().__init__(message, "rate_limit")


class DataNotAvailableError(WorldBankAPIError):
    """Exception for when no data is available for a country."""
    def __init__(self, message: str):
        """
        Initialize DataNotAvailableError.
        
        Args:
            message: Error message describing the data availability issue
        """
        super().__init__(message, "no_data")


class InvalidCountryError(WorldBankAPIError):
    """Exception for invalid country selections."""
    def __init__(self, message: str):
        """
        Initialize InvalidCountryError.
        
        Args:
            message: Error message describing the invalid country issue
        """
        super().__init__(message, "invalid_country")


class WorldBankClient:
    """Client for fetching data from the World Bank API."""
    
    def __init__(self):
        """Initialize the World Bank API client."""
        self.base_url = "https://api.worldbank.org/v2"
        self.cache = {}
        self.cache_ttl = 3600  # Cache for 1 hour
        self.request_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """
        Make HTTP request to World Bank API with comprehensive error handling and retries.
        
        This method implements a robust retry mechanism with exponential backoff to handle
        temporary network issues, API rate limits, and server errors gracefully.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            APIConnectionError: If connection fails after retries
            APIRateLimitError: If rate limit is exceeded
            WorldBankAPIError: For other API-related errors
        """
        if params is None:
            params = {}
        
        # Configure World Bank API specific parameters
        params['format'] = 'json'  # Request JSON format (default is XML)
        params['per_page'] = '1000'  # Increase page size to reduce API calls
        
        # Implement retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making request to {url} (attempt {attempt + 1})")
                response = requests.get(url, params=params, timeout=self.request_timeout)
                
                # Handle specific HTTP status codes that require special treatment
                if response.status_code == 429:
                    # Rate limit exceeded - World Bank API has usage limits
                    retry_after = response.headers.get('Retry-After', '60')
                    raise APIRateLimitError(
                        f"API rate limit exceeded. Please wait {retry_after} seconds before trying again."
                    )
                elif response.status_code == 503:
                    # Service unavailable - temporary server issues
                    raise APIConnectionError(
                        "World Bank API is temporarily unavailable. Please try again later."
                    )
                elif response.status_code >= 500:
                    # Server errors (5xx) - internal server problems
                    raise APIConnectionError(
                        f"World Bank API server error (HTTP {response.status_code}). Please try again later."
                    )
                
                response.raise_for_status()
                
                # Parse JSON response with error handling
                try:
                    data = response.json()
                except ValueError as e:
                    raise WorldBankAPIError(f"Invalid JSON response from World Bank API: {e}")
                
                # World Bank API returns array: [metadata, data]
                # First element contains pagination info and error messages
                # Second element contains the actual data
                if isinstance(data, list) and len(data) >= 2:
                    # Check for API error messages in the metadata (first element)
                    if isinstance(data[0], dict) and 'message' in data[0]:
                        # Extract error message from nested structure
                        error_msg = data[0]['message'][0]['value'] if isinstance(data[0]['message'], list) else str(data[0]['message'])
                        # Classify error types for appropriate handling
                        if 'not found' in error_msg.lower() or 'invalid' in error_msg.lower():
                            raise DataNotAvailableError(f"World Bank API error: {error_msg}")
                        else:
                            raise WorldBankAPIError(f"World Bank API error: {error_msg}")
                    return data
                else:
                    raise WorldBankAPIError("Invalid response format from World Bank API")
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise APIConnectionError(
                        f"Unable to connect to World Bank API after {self.max_retries} attempts. "
                        "Please check your internet connection and try again."
                    )
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                
            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timeout (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise APIConnectionError(
                        f"Request to World Bank API timed out after {self.max_retries} attempts. "
                        "The service may be slow or unavailable."
                    )
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTP error (attempt {attempt + 1}): {e}")
                if response.status_code == 404:
                    raise DataNotAvailableError("Requested data not found in World Bank API")
                elif attempt == self.max_retries - 1:
                    raise APIConnectionError(f"HTTP error from World Bank API: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except (APIConnectionError, APIRateLimitError, DataNotAvailableError):
                # Re-raise our custom exceptions without retry
                raise
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise APIConnectionError(f"Failed to connect to World Bank API: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt == self.max_retries - 1:
                    raise WorldBankAPIError(f"Unexpected error occurred: {e}")
                time.sleep(self.retry_delay * (2 ** attempt))
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid based on TTL."""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return time.time() - cached_time < self.cache_ttl
    
    def get_countries(self) -> List[Country]:
        """
        Fetch list of countries with codes and names from World Bank API.
        
        Returns:
            List of Country objects
            
        Raises:
            APIConnectionError: If connection fails
            APIRateLimitError: If rate limit exceeded
            WorldBankAPIError: For other API-related errors
        """
        cache_key = 'countries'
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info("Returning cached countries data")
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.base_url}/country"
            response_data = self._make_request(url)
            
            # Extract countries data (second element in response array)
            countries_data = response_data[1] if len(response_data) > 1 else []
            
            if not countries_data:
                raise DataNotAvailableError("No countries data received from World Bank API")
            
            countries = []
            for country in countries_data:
                # Filter out aggregates and regions, keep only actual countries
                if (country.get('capitalCity') and 
                    country.get('longitude') and 
                    country.get('latitude')):
                    
                    code = country.get('id', '')
                    name = country.get('name', '')
                    region = country.get('region', {}).get('value', '') if country.get('region') else ''
                    
                    # Validate country code before creating Country object
                    if validate_country_code(code) and name:
                        try:
                            country_obj = Country(code=code, name=name, region=region)
                            countries.append(country_obj)
                        except ValueError as e:
                            logger.warning(f"Skipping invalid country data: {country}, error: {e}")
            
            if not countries:
                raise DataNotAvailableError("No valid countries found in World Bank API response")
            
            # Sort countries by name for better UX
            countries.sort(key=lambda x: x.name)
            
            # Cache the results
            self.cache[cache_key] = {
                'data': countries,
                'timestamp': time.time()
            }
            
            logger.info(f"Fetched {len(countries)} countries from World Bank API")
            return countries
            
        except (APIConnectionError, APIRateLimitError, DataNotAvailableError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Error fetching countries: {e}")
            raise WorldBankAPIError(f"Failed to fetch countries: {e}")
    
    def get_countries_dict(self) -> List[Dict[str, str]]:
        """
        Get countries as dictionary format for backward compatibility.
        
        Returns:
            List of dictionaries with country information
        """
        countries = self.get_countries()
        return [
            {
                'code': country.code,
                'name': country.name,
                'region': country.region
            }
            for country in countries
        ]
    
    def get_gini_data(self, country_code: str, start_year: int = 1990, end_year: int = 2023) -> pd.DataFrame:
        """
        Fetch Gini coefficient data for specified country and time range.
        
        Args:
            country_code: ISO country code (e.g., 'USA', 'DEU')
            start_year: Starting year for data retrieval (default: 1990)
            end_year: Ending year for data retrieval (default: 2023)
            
        Returns:
            Cleaned DataFrame with columns: ['year', 'value', 'country_code']
            
        Raises:
            InvalidCountryError: If country code is invalid
            APIConnectionError: If connection fails
            APIRateLimitError: If rate limit exceeded
            DataNotAvailableError: If no data available for country
            ValueError: If invalid parameters provided
        """
        # Validate inputs using utility functions
        if not validate_country_code(country_code):
            raise InvalidCountryError(f"Invalid country code format: '{country_code}'. Must be a valid ISO country code.")
        
        if not validate_year(start_year) or not validate_year(end_year):
            raise ValueError(f"Invalid year range: {start_year}-{end_year}. Years must be between 1960 and current year.")
        
        if start_year > end_year:
            raise ValueError("Start year cannot be greater than end year")
        
        # Validate that country exists in our countries list
        try:
            countries = self.get_countries()
            valid_codes = [c.code.upper() for c in countries]
            if country_code.upper() not in valid_codes:
                raise InvalidCountryError(
                    f"Country code '{country_code}' not found in World Bank database. "
                    f"Please select a valid country from the dropdown."
                )
        except (APIConnectionError, APIRateLimitError):
            # If we can't validate due to connection issues, proceed anyway
            logger.warning(f"Could not validate country code {country_code} due to connection issues")
        
        cache_key = f'gini_{country_code.upper()}_{start_year}_{end_year}'
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached Gini data for {country_code}")
            return self.cache[cache_key]['data']
        
        try:
            # World Bank Gini coefficient indicator code
            indicator_code = 'SI.POV.GINI'
            url = f"{self.base_url}/country/{country_code}/indicator/{indicator_code}"
            
            params = {
                'date': f'{start_year}:{end_year}',
                'format': 'json'
            }
            
            response_data = self._make_request(url, params)
            
            # Extract indicator data (second element in response array)
            gini_data = response_data[1] if len(response_data) > 1 else []
            
            # Check if we got any data
            if not gini_data or gini_data is None:
                raise DataNotAvailableError(
                    f"No Gini coefficient data available for country '{country_code}' "
                    f"in the period {start_year}-{end_year}. This country may not have "
                    f"reported Gini data to the World Bank."
                )
            
            # Convert API response to DataFrame using utility function
            df = convert_api_response_to_dataframe(gini_data, country_code)
            
            # Clean the data using utility functions
            df = clean_gini_data(df)
            df = handle_missing_values(df, method='drop')
            
            # Check if we have any valid data after cleaning
            if df.empty:
                raise DataNotAvailableError(
                    f"No valid Gini coefficient data found for country '{country_code}' "
                    f"after data cleaning. The available data may contain only missing values."
                )
            
            # Cache the results
            self.cache[cache_key] = {
                'data': df,
                'timestamp': time.time()
            }
            
            logger.info(f"Fetched and cleaned {len(df)} Gini data points for {country_code}")
            return df
            
        except (APIConnectionError, APIRateLimitError, DataNotAvailableError, InvalidCountryError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Error fetching Gini data for {country_code}: {e}")
            raise WorldBankAPIError(f"Failed to fetch Gini data for {country_code}: {e}")
    
    def get_gini_time_series(self, country_code: str, start_year: int = 1990, end_year: int = 2023) -> GiniTimeSeries:
        """
        Fetch Gini data as a GiniTimeSeries object.
        
        Args:
            country_code: ISO country code
            start_year: Starting year for data retrieval
            end_year: Ending year for data retrieval
            
        Returns:
            GiniTimeSeries object with country and data points
            
        Raises:
            WorldBankAPIError: If API request fails
            ValueError: If invalid parameters provided
        """
        # Get the DataFrame
        df = self.get_gini_data(country_code, start_year, end_year)
        
        # Find the country object
        countries = self.get_countries()
        country_obj = None
        for country in countries:
            if country.code.upper() == country_code.upper():
                country_obj = country
                break
        
        if not country_obj:
            # Create a basic country object if not found
            country_obj = Country(code=country_code.upper(), name=country_code.upper(), region="Unknown")
        
        # Convert DataFrame to GiniDataPoint objects
        data_points = create_gini_data_points(df)
        
        return GiniTimeSeries(country=country_obj, data_points=data_points)
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_info(self) -> Dict:
        """Get information about current cache state."""
        return {
            'cache_size': len(self.cache),
            'cache_keys': list(self.cache.keys()),
            'cache_ttl': self.cache_ttl
        }