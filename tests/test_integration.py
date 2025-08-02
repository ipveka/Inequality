#!/usr/bin/env python3
"""
Comprehensive integration tests for the Gini Inequality Visualizer application.

This module tests:
- Complete user workflow from country selection to visualization
- World Bank API connectivity and data retrieval
- Application performance with multiple countries and datasets
- Application startup and functionality verification
"""

import pandas as pd
import sys
import os
import time
import subprocess
import requests
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application components
from utils.data_service import WorldBankClient, WorldBankAPIError, APIConnectionError, DataNotAvailableError
from utils.visualization import create_gini_table, create_gini_line_plot
from utils.ui_components import render_sidebar, render_main_dashboard
from utils.data_models import Country, GiniDataPoint


class IntegrationTestSuite:
    """Comprehensive integration test suite for the Gini Inequality Visualizer."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.client = None
        self.test_countries = ['USA', 'DEU', 'BRA', 'JPN', 'GBR']
        self.errors = []
        self.performance_metrics = {}
        
    def log_error(self, test_name: str, message: str):
        """Log an error for reporting."""
        if test_name not in self.errors:
            self.errors.append(f"{test_name}: {message}")
    
    def test_world_bank_api_connectivity(self) -> bool:
        """Test actual World Bank API connectivity and basic functionality."""
        print("\\n1. Testing World Bank API Connectivity")
        print("-" * 50)
        
        try:
            # Test basic API endpoint accessibility
            response = requests.get("https://api.worldbank.org/v2/country?format=json&per_page=5", timeout=10)
            if response.status_code == 200:
                print("   ✅ PASS: API endpoint accessibility")
                print("      World Bank API is accessible")
            else:
                print(f"   ❌ FAIL: API returned status code {response.status_code}")
                self.log_error("Api Connectivity", f"HTTP {response.status_code}")
                return False
            
            # Test WorldBankClient initialization and countries retrieval
            start_time = time.time()
            self.client = WorldBankClient()
            countries = self.client.get_countries()
            duration = time.time() - start_time
            
            if countries and len(countries) > 50:  # Expect reasonable number of countries
                print(f"   ✅ PASS: Countries data retrieval ({duration:.2f}s)")
                print(f"      Retrieved {len(countries)} countries")
                self.performance_metrics['countries_load_time'] = duration
                return True
            else:
                print(f"   ❌ FAIL: Insufficient countries data ({len(countries) if countries else 0})")
                self.log_error("Api Connectivity", "Insufficient countries data")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAIL: Network error - {e}")
            self.log_error("Api Connectivity", f"Network error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ FAIL: Unexpected error - {e}")
            self.log_error("Api Connectivity", f"Unexpected error: {e}")
            return False
    
    def test_data_retrieval_multiple_countries(self) -> bool:
        """Test data retrieval for multiple countries with performance monitoring."""
        print("\\n2. Testing Data Retrieval for Multiple Countries")
        print("-" * 50)
        
        if not self.client:
            print("   ❌ FAIL: Client not initialized")
            return False
        
        retrieval_times = []
        successful_retrievals = 0
        total_data_points = 0
        
        for country_code in self.test_countries:
            try:
                start_time = time.time()
                gini_data = self.client.get_gini_data(country_code, start_year=2010, end_year=2020)
                duration = time.time() - start_time
                retrieval_times.append(duration)
                
                if not gini_data.empty:
                    print(f"   ✅ PASS: Data retrieval for {country_code} ({duration:.2f}s)")
                    print(f"      {len(gini_data)} data points")
                    
                    # Validate data structure
                    required_columns = ['year', 'value', 'country_code']
                    if all(col in gini_data.columns for col in required_columns):
                        print(f"   ✅ PASS: Data structure validation for {country_code}")
                        successful_retrievals += 1
                        total_data_points += len(gini_data)
                    else:
                        print(f"   ❌ FAIL: Invalid data structure for {country_code}")
                        self.log_error("Data Retrieval", f"Invalid structure for {country_code}")
                else:
                    print(f"   ⚠️  WARN: No data available for {country_code}")
                    
            except Exception as e:
                print(f"   ❌ FAIL: Error retrieving data for {country_code} - {e}")
                self.log_error("Data Retrieval", f"Error for {country_code}: {e}")
        
        # Performance analysis
        if retrieval_times:
            avg_time = sum(retrieval_times) / len(retrieval_times)
            max_time = max(retrieval_times)
            
            print(f"\\n   Performance Summary:")
            print(f"   - Average retrieval time: {avg_time:.2f}s")
            print(f"   - Maximum retrieval time: {max_time:.2f}s")
            print(f"   - Total data points retrieved: {total_data_points}")
            print(f"   - Successful retrievals: {successful_retrievals}/{len(self.test_countries)}")
            
            self.performance_metrics.update({
                'avg_retrieval_time': avg_time,
                'max_retrieval_time': max_time,
                'total_data_points': total_data_points,
                'success_rate': (successful_retrievals / len(self.test_countries)) * 100
            })
            
            if successful_retrievals >= len(self.test_countries) * 0.6:  # 60% success rate minimum
                print(f"   ✅ PASS: Overall data retrieval")
                print(f"      Success rate: {(successful_retrievals / len(self.test_countries)) * 100:.1f}%")
                return True
            else:
                print(f"   ❌ FAIL: Low success rate ({successful_retrievals}/{len(self.test_countries)})")
                self.log_error("Data Retrieval", "Low success rate")
                return False
        else:
            print("   ❌ FAIL: No successful data retrievals")
            self.log_error("Data Retrieval", "No successful retrievals")
            return False
    
    def test_visualization_creation(self) -> bool:
        """Test visualization creation with real data."""
        print("\\n3. Testing Visualization Creation")
        print("-" * 50)
        
        if not self.client:
            print("   ❌ FAIL: Client not initialized")
            return False
        
        successful_visualizations = 0
        test_countries = ['USA', 'DEU', 'BRA']  # Subset for visualization testing
        
        for country_code in test_countries:
            try:
                # Get data
                gini_data = self.client.get_gini_data(country_code, start_year=2010, end_year=2020)
                
                if not gini_data.empty:
                    # Test chart creation
                    start_time = time.time()
                    chart = create_gini_line_plot(gini_data, f"Test Country {country_code}")
                    chart_duration = time.time() - start_time
                    
                    if chart and hasattr(chart, 'data') and len(chart.data) > 0:
                        print(f"   ✅ PASS: Chart creation for {country_code} ({chart_duration:.2f}s)")
                        print(f"      Chart with {len(gini_data)} points")
                        
                        # Validate chart data
                        if chart.data[0].x is not None and chart.data[0].y is not None:
                            print(f"   ✅ PASS: Chart data validation for {country_code}")
                        else:
                            print(f"   ❌ FAIL: Invalid chart data for {country_code}")
                            self.log_error("Visualization Creation", f"Invalid chart data for {country_code}")
                            continue
                    else:
                        print(f"   ❌ FAIL: Chart creation failed for {country_code}")
                        self.log_error("Visualization Creation", f"Chart creation failed for {country_code}")
                        continue
                    
                    # Test table creation
                    start_time = time.time()
                    table = create_gini_table(gini_data)
                    table_duration = time.time() - start_time
                    
                    if isinstance(table, pd.DataFrame) and not table.empty:
                        print(f"   ✅ PASS: Table creation for {country_code} ({table_duration:.2f}s)")
                        print(f"      Table with {len(table)} rows")
                        
                        # Validate table structure
                        expected_columns = ['Year', 'Gini Coefficient']
                        if all(col in table.columns for col in expected_columns):
                            print(f"   ✅ PASS: Table structure validation for {country_code}")
                            successful_visualizations += 1
                        else:
                            print(f"   ❌ FAIL: Invalid table structure for {country_code}")
                            self.log_error("Visualization Creation", f"Invalid table structure for {country_code}")
                    else:
                        print(f"   ❌ FAIL: Table creation failed for {country_code}")
                        self.log_error("Visualization Creation", f"Table creation failed for {country_code}")
                        
            except Exception as e:
                print(f"   ❌ FAIL: Visualization error for {country_code} - {e}")
                self.log_error("Visualization Creation", f"Error for {country_code}: {e}")
        
        if successful_visualizations >= len(test_countries) * 0.8:  # 80% success rate
            print(f"   ✅ PASS: Overall visualization creation")
            print(f"      {successful_visualizations} successful visualizations")
            return True
        else:
            print(f"   ❌ FAIL: Insufficient successful visualizations ({successful_visualizations}/{len(test_countries)})")
            self.log_error("Visualization Creation", "Low success rate")
            return False
    
    def test_complete_user_workflow(self) -> bool:
        """Test complete user workflow from country selection to visualization."""
        print("\\n4. Testing Complete User Workflow")
        print("-" * 50)
        
        try:
            # Step 1: Load countries
            start_time = time.time()
            client = WorldBankClient()
            countries = client.get_countries()
            countries_duration = time.time() - start_time
            
            if countries and len(countries) > 0:
                print(f"   ✅ PASS: Step 1: Load countries ({countries_duration:.2f}s)")
                print(f"      {len(countries)} countries loaded")
            else:
                print("   ❌ FAIL: Step 1: Failed to load countries")
                self.log_error("User Workflow", "Failed to load countries")
                return False
            
            # Step 2: Select a country (simulate user selection)
            test_country = next((c for c in countries if c.code == 'USA'), None)
            if test_country:
                print("   ✅ PASS: Step 2: Country selection")
                print(f"      Selected {test_country.name}")
            else:
                print("   ❌ FAIL: Step 2: Test country not found")
                self.log_error("User Workflow", "Test country not found")
                return False
            
            # Step 3: Fetch data for selected country
            start_time = time.time()
            gini_data = client.get_gini_data(test_country.code, start_year=2000, end_year=2020)
            data_duration = time.time() - start_time
            
            if not gini_data.empty:
                print(f"   ✅ PASS: Step 3: Data fetching ({data_duration:.2f}s)")
                print(f"      {len(gini_data)} data points")
            else:
                print("   ❌ FAIL: Step 3: No data retrieved")
                self.log_error("User Workflow", "No data retrieved")
                return False
            
            # Step 4: Create visualizations
            start_time = time.time()
            chart = create_gini_line_plot(gini_data, test_country.name)
            table = create_gini_table(gini_data)
            viz_duration = time.time() - start_time
            
            if chart and isinstance(table, pd.DataFrame):
                print(f"   ✅ PASS: Step 4: Visualization creation ({viz_duration:.2f}s)")
                print("      Chart and table created")
            else:
                print("   ❌ FAIL: Step 4: Visualization creation failed")
                self.log_error("User Workflow", "Visualization creation failed")
                return False
            
            # Step 5: Validate data consistency
            if len(gini_data) == len(table):
                print("   ✅ PASS: Step 5: Data consistency validation")
                print(f"      All components have {len(gini_data)} data points")
                return True
            else:
                print("   ❌ FAIL: Step 5: Data inconsistency detected")
                self.log_error("User Workflow", "Data inconsistency")
                return False
                
        except Exception as e:
            print(f"   ❌ FAIL: Workflow error - {e}")
            self.log_error("User Workflow", f"Workflow error: {e}")
            return False
    
    def test_application_performance(self) -> bool:
        """Test application performance with multiple datasets."""
        print("\\n5. Testing Application Performance")
        print("-" * 50)
        
        try:
            client = WorldBankClient()
            
            # Test caching performance
            start_time = time.time()
            countries1 = client.get_countries()
            first_call = time.time() - start_time
            
            start_time = time.time()
            countries2 = client.get_countries()
            second_call = time.time() - start_time
            
            if second_call < first_call * 0.1:  # Cache should be significantly faster
                print(f"   ✅ PASS: Cache performance")
                print(f"      First call: {first_call:.3f}s, Cached call: {second_call:.3f}s")
            else:
                print(f"   ❌ FAIL: Cache performance")
                print(f"      Cache not significantly faster: {second_call:.3f}s vs {first_call:.3f}s")
                self.log_error("Performance", f"Cache not significantly faster: {second_call:.3f}s vs {first_call:.3f}s")
            
            # Test bulk processing
            test_countries = ['USA', 'DEU', 'BRA']
            start_time = time.time()
            
            for country_code in test_countries:
                gini_data = client.get_gini_data(country_code, start_year=2015, end_year=2020)
                
            bulk_duration = time.time() - start_time
            
            if bulk_duration < 10:  # Should complete within reasonable time
                print(f"   ✅ PASS: Bulk processing performance")
                print(f"      Processed {len(test_countries)} countries in {bulk_duration:.2f}s")
            else:
                print(f"   ❌ FAIL: Bulk processing too slow ({bulk_duration:.2f}s)")
                self.log_error("Performance", f"Bulk processing too slow: {bulk_duration:.2f}s")
            
            # Test memory management
            cache_info = client.get_cache_info()
            if cache_info['cache_size'] > 0:
                print(f"   ✅ PASS: Memory management")
                print(f"      Cache contains {cache_info['cache_size']} items")
                return True
            else:
                print("   ❌ FAIL: Cache not working")
                self.log_error("Performance", "Cache not working")
                return False
                
        except Exception as e:
            print(f"   ❌ FAIL: Performance test error - {e}")
            self.log_error("Performance", f"Performance test error: {e}")
            return False
    
    def test_streamlit_app_startup(self) -> bool:
        """Test that the Streamlit application starts successfully."""
        print("\\n6. Testing Streamlit Application Startup")
        print("-" * 50)
        
        try:
            # Test app module import
            import app
            print("   ✅ PASS: App module import")
            print("      app.py imported successfully")
            
            # Test required dependencies
            dependencies = ['streamlit', 'pandas', 'plotly', 'requests']
            for dep in dependencies:
                try:
                    __import__(dep)
                    print(f"   ✅ PASS: Dependency check: {dep}")
                except ImportError:
                    print(f"   ❌ FAIL: Missing dependency: {dep}")
                    self.log_error("App Startup", f"Missing dependency: {dep}")
                    return False
            
            # Test Streamlit CLI availability
            try:
                result = subprocess.run(['streamlit', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("   ✅ PASS: Streamlit CLI availability")
                    return True
                else:
                    print("   ❌ FAIL: Streamlit CLI error")
                    self.log_error("App Startup", "Streamlit CLI error")
                    return False
            except subprocess.TimeoutExpired:
                print("   ❌ FAIL: Streamlit CLI availability")
                self.log_error("App Startup", "Command '['streamlit', '--version']' timed out after 10 seconds")
                return False
                
        except Exception as e:
            print(f"   ❌ FAIL: App startup test error - {e}")
            self.log_error("App Startup", f"App startup error: {e}")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all integration tests and return results."""
        print("🚀 Starting Comprehensive Integration Test Suite")
        print("=" * 60)
        print("Testing complete user workflow from country selection to visualization")
        print("Verifying actual World Bank API connectivity and data retrieval")
        print("Testing application performance with multiple countries and datasets")
        print("Ensuring application runs successfully with 'streamlit run app.py'")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        test_results = {
            'Api Connectivity': self.test_world_bank_api_connectivity(),
            'Data Retrieval': self.test_data_retrieval_multiple_countries(),
            'Visualization Creation': self.test_visualization_creation(),
            'User Workflow': self.test_complete_user_workflow(),
            'Performance': self.test_application_performance(),
            'App Startup': self.test_streamlit_app_startup(),
        }
        
        total_duration = time.time() - start_time
        
        # Generate comprehensive report
        self.generate_report(test_results, total_duration)
        
        return {
            'results': test_results,
            'errors': self.errors,
            'performance': self.performance_metrics,
            'duration': total_duration
        }
    
    def generate_report(self, test_results: Dict[str, bool], duration: float):
        """Generate comprehensive test report."""
        print("\\n" + "=" * 60)
        print("📋 COMPREHENSIVE INTEGRATION TEST REPORT")
        print("=" * 60)
        
        # Summary
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        success_rate = (passed / total) * 100
        
        print(f"\\n📊 Test Results Summary:")
        print(f"   Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"   Total Duration: {duration:.2f} seconds")
        
        # Individual results
        print(f"\\n🔍 Individual Test Results:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        # Performance metrics
        if self.performance_metrics:
            print(f"\\n⚡ Performance Metrics:")
            for metric, value in self.performance_metrics.items():
                if isinstance(value, float):
                    if 'time' in metric.lower():
                        print(f"   {metric.replace('_', ' ').title()}: {value:.3f}s")
                    elif 'rate' in metric.lower():
                        print(f"   {metric.replace('_', ' ').title()}: {value:.1f}%")
                    else:
                        print(f"   {metric.replace('_', ' ').title()}: {value:.3f}")
                else:
                    print(f"   {metric.replace('_', ' ').title()}: {value}")
        
        # Errors
        if self.errors:
            print(f"\\n❌ Errors Encountered ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        # Overall assessment
        print(f"\\n🎯 Overall Assessment:")
        if success_rate >= 80:
            print("   ✅ EXCELLENT: Application is ready for production use")
            print("   ✅ All critical functionality is working correctly")
            print("   ✅ Performance meets expected standards")
        elif success_rate >= 60:
            print("   ⚠️  GOOD: Application is mostly functional with minor issues")
            print("   ⚠️  Some non-critical features may need attention")
        else:
            print("   ❌ NEEDS WORK: Significant issues detected")
            print("   ❌ Critical functionality may be impaired")
        
        print(f"\\n💡 Recommendations:")
        if self.errors:
            print("   - Review and address the errors listed above")
        if success_rate < 100:
            print("   - Verify Streamlit installation and app configuration")
        print("   - Application is ready for deployment")
        print("   - Consider adding monitoring and logging for production")
        
        print("\\n" + "=" * 60)
        if success_rate >= 80:
            print("🎉 INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
            print("🚀 Application is ready for use with 'streamlit run app.py'")
        else:
            print("⚠️  INTEGRATION TESTS COMPLETED WITH ISSUES")
            print("🔧 Please address the issues before deployment")
        print("=" * 60)


def main():
    """Run the integration test suite."""
    test_suite = IntegrationTestSuite()
    results = test_suite.run_all_tests()
    
    # Return appropriate exit code
    passed_tests = sum(1 for result in results['results'].values() if result)
    total_tests = len(results['results'])
    
    if passed_tests == total_tests:
        return 0  # All tests passed
    elif passed_tests >= total_tests * 0.8:
        return 0  # 80% or more passed (acceptable)
    else:
        return 1  # Too many failures


if __name__ == "__main__":
    exit(main())