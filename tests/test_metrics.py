"""
Unit tests for inequality metrics calculation functions.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.metrics import (
    gini_coefficient,
    palma_ratio,
    income_shares,
    lorenz_curve_data,
    theil_index,
    atkinson_index,
    calculate_all_metrics,
    validate_metric_values
)

class TestGiniCoefficient:
    """Test cases for Gini coefficient calculation."""
    
    def test_perfect_equality(self):
        """Test Gini coefficient for perfect equality."""
        values = [100, 100, 100, 100, 100]
        gini = gini_coefficient(values)
        assert gini == 0.0
    
    def test_perfect_inequality(self):
        """Test Gini coefficient for perfect inequality."""
        values = [0, 0, 0, 0, 100]
        gini = gini_coefficient(values)
        assert gini == 1.0
    
    def test_typical_distribution(self):
        """Test Gini coefficient for a typical income distribution."""
        values = [10, 20, 30, 40, 50]
        gini = gini_coefficient(values)
        assert 0.0 < gini < 1.0
        # The actual Gini for [10, 20, 30, 40, 50] is approximately 0.267
        assert gini == pytest.approx(0.267, rel=1e-2)
    
    def test_single_value(self):
        """Test Gini coefficient for single value."""
        values = [100]
        gini = gini_coefficient(values)
        assert gini == 0.0
    
    def test_empty_list(self):
        """Test Gini coefficient with empty list."""
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            gini_coefficient([])
    
    def test_negative_values(self):
        """Test Gini coefficient with negative values."""
        values = [-10, 20, 30, 40, 50]
        gini = gini_coefficient(values)
        assert 0.0 < gini < 1.0
    
    def test_zero_values(self):
        """Test Gini coefficient with zero values."""
        values = [0, 0, 20, 30, 50]
        gini = gini_coefficient(values)
        assert 0.0 < gini < 1.0

class TestPalmaRatio:
    """Test cases for Palma ratio calculation."""
    
    def test_perfect_equality(self):
        """Test Palma ratio for perfect equality."""
        values = [100] * 20
        palma = palma_ratio(values)
        assert palma == pytest.approx(1.0, rel=1e-2)
    
    def test_high_inequality(self):
        """Test Palma ratio for high inequality."""
        values = [10] * 18 + [1000, 1000]  # 90% poor, 10% rich
        palma = palma_ratio(values)
        assert palma > 1.0
    
    def test_insufficient_data(self):
        """Test Palma ratio with insufficient data."""
        values = [10, 20, 30, 40, 50]
        with pytest.raises(ValueError, match="Need at least 10 values"):
            palma_ratio(values)
    
    def test_empty_list(self):
        """Test Palma ratio with empty list."""
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            palma_ratio([])

class TestIncomeShares:
    """Test cases for income shares calculation."""
    
    def test_perfect_equality(self):
        """Test income shares for perfect equality."""
        values = [100] * 100
        shares = income_shares(values)
        
        # For perfect equality, cumulative shares should match population shares
        assert shares['p10'] == pytest.approx(0.1, rel=1e-2)
        assert shares['p50'] == pytest.approx(0.5, rel=1e-2)
        assert shares['p90'] == pytest.approx(0.9, rel=1e-2)
        assert shares['top_10_share'] == pytest.approx(0.1, rel=1e-2)
        assert shares['bottom_50_share'] == pytest.approx(0.5, rel=1e-2)
    
    def test_high_inequality(self):
        """Test income shares for high inequality."""
        values = [10] * 90 + [1000] * 10  # 90% poor, 10% rich
        shares = income_shares(values)
        
        assert shares['top_10_share'] > shares['bottom_50_share']
        # With this distribution, top 1% should have significant share
        assert shares.get('top_1_share', 0) >= 0.0
    
    def test_custom_percentiles(self):
        """Test income shares with custom percentiles."""
        values = list(range(1, 101))
        shares = income_shares(values, percentiles=[25, 75])
        
        assert 'p25' in shares
        assert 'p75' in shares
        assert shares['p25'] < shares['p75']
    
    def test_empty_list(self):
        """Test income shares with empty list."""
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            income_shares([])

class TestLorenzCurveData:
    """Test cases for Lorenz curve data generation."""
    
    def test_perfect_equality(self):
        """Test Lorenz curve data for perfect equality."""
        values = [100] * 100
        pop_shares, inc_shares = lorenz_curve_data(values)
        
        assert len(pop_shares) == len(inc_shares)
        assert pop_shares[0] == 0.0
        assert pop_shares[-1] == 1.0
        assert inc_shares[0] == 0.0
        assert inc_shares[-1] == 1.0
        
        # For perfect equality, population and income shares should be equal
        # Allow for small numerical differences
        for p, i in zip(pop_shares, inc_shares):
            assert p == pytest.approx(i, rel=1e-1)
    
    def test_high_inequality(self):
        """Test Lorenz curve data for high inequality."""
        values = [10] * 90 + [1000] * 10
        pop_shares, inc_shares = lorenz_curve_data(values)
        
        assert len(pop_shares) == len(inc_shares)
        assert pop_shares[0] == 0.0
        assert pop_shares[-1] == 1.0
        assert inc_shares[0] == 0.0
        assert inc_shares[-1] == 1.0
        
        # For high inequality, income shares should be lower than population shares
        # for most of the population
        for i in range(1, len(pop_shares) - 1):
            if pop_shares[i] < 0.9:  # Bottom 90%
                assert inc_shares[i] < pop_shares[i]
    
    def test_custom_points(self):
        """Test Lorenz curve data with custom number of points."""
        values = list(range(1, 101))
        pop_shares, inc_shares = lorenz_curve_data(values, num_points=50)
        
        assert len(pop_shares) == 50
        assert len(inc_shares) == 50
    
    def test_empty_list(self):
        """Test Lorenz curve data with empty list."""
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            lorenz_curve_data([])

class TestTheilIndex:
    """Test cases for Theil index calculation."""
    
    def test_perfect_equality(self):
        """Test Theil index for perfect equality."""
        values = [100] * 100
        theil = theil_index(values)
        assert theil == 0.0
    
    def test_inequality(self):
        """Test Theil index for inequality."""
        values = [10] * 90 + [1000] * 10
        theil = theil_index(values)
        assert theil > 0.0
    
    def test_empty_list(self):
        """Test Theil index with empty list."""
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            theil_index([])

class TestAtkinsonIndex:
    """Test cases for Atkinson index calculation."""
    
    def test_perfect_equality(self):
        """Test Atkinson index for perfect equality."""
        values = [100] * 100
        atkinson = atkinson_index(values)
        assert atkinson == 0.0
    
    def test_inequality(self):
        """Test Atkinson index for inequality."""
        values = [10] * 90 + [1000] * 10
        atkinson = atkinson_index(values)
        assert 0.0 < atkinson < 1.0
    
    def test_different_epsilon(self):
        """Test Atkinson index with different epsilon values."""
        values = [10] * 90 + [1000] * 10
        atkinson1 = atkinson_index(values, epsilon=0.5)
        atkinson2 = atkinson_index(values, epsilon=2.0)
        
        assert atkinson1 != atkinson2
        assert 0.0 < atkinson1 < 1.0
        assert 0.0 < atkinson2 < 1.0
    
    def test_invalid_epsilon(self):
        """Test Atkinson index with invalid epsilon."""
        values = [10, 20, 30]
        with pytest.raises(ValueError, match="Epsilon must be positive"):
            atkinson_index(values, epsilon=0)
    
    def test_empty_list(self):
        """Test Atkinson index with empty list."""
        with pytest.raises(ValueError, match="Values list cannot be empty"):
            atkinson_index([])

class TestCalculateAllMetrics:
    """Test cases for calculate_all_metrics function."""
    
    def test_all_metrics_calculation(self):
        """Test calculation of all metrics."""
        values = [10] * 80 + [100] * 15 + [1000] * 5
        metrics = calculate_all_metrics(values)
        
        # Check that all expected metrics are present
        expected_metrics = ['gini', 'palma_ratio', 'theil_index', 'atkinson_index']
        for metric in expected_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
        
        # Check that values are reasonable
        assert 0.0 <= metrics['gini'] <= 1.0
        assert metrics['palma_ratio'] >= 0.0
        assert metrics['theil_index'] >= 0.0
        assert 0.0 <= metrics['atkinson_index'] <= 1.0
    
    def test_empty_list(self):
        """Test calculate_all_metrics with empty list."""
        metrics = calculate_all_metrics([])
        assert metrics == {}

class TestValidateMetricValues:
    """Test cases for validate_metric_values function."""
    
    def test_valid_metrics(self):
        """Test validation of valid metrics."""
        metrics = {
            'gini': 0.5,
            'palma_ratio': 1.2,
            'theil_index': 0.3,
            'atkinson_index': 0.4,
            'top_10_share': 0.3,
            'bottom_50_share': 0.2
        }
        
        validation = validate_metric_values(metrics)
        
        for metric, is_valid in validation.items():
            assert is_valid == True
    
    def test_invalid_metrics(self):
        """Test validation of invalid metrics."""
        metrics = {
            'gini': 1.5,  # Should be <= 1
            'palma_ratio': -0.1,  # Should be >= 0
            'theil_index': -0.1,  # Should be >= 0
            'atkinson_index': 1.5,  # Should be <= 1
            'top_10_share': 1.5,  # Should be <= 1
            'bottom_50_share': -0.1  # Should be >= 0
        }
        
        validation = validate_metric_values(metrics)
        
        for metric, is_valid in validation.items():
            assert is_valid == False

if __name__ == "__main__":
    pytest.main([__file__]) 