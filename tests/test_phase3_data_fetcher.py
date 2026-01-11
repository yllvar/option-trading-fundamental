"""
Unit tests for Phase 3 data fetching utilities.
Tests real data fetching, validation, and synthetic fallback.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

# Mock streamlit for caching
sys.modules['streamlit'] = MagicMock()

from utils.data_fetcher import (
    calculate_returns,
    calculate_statistics,
    estimate_volatility,
    generate_synthetic_prices,
    DataValidator
)


class TestReturnCalculations:
    """Test return calculation functions."""
    
    def test_calculate_returns_simple(self):
        """Test simple returns calculation."""
        prices = pd.Series([100, 105, 103, 108])
        
        returns = calculate_returns(prices, method='simple')
        
        assert len(returns) == 3  # One less than prices
        assert abs(returns.iloc[0] - 0.05) < 1e-10  # (105-100)/100
        assert abs(returns.iloc[1] - (-0.019047619)) < 1e-6  # (103-105)/105
    
    def test_calculate_returns_log(self):
        """Test log returns calculation."""
        prices = pd.Series([100, 105, 103])
        
        returns = calculate_returns(prices, method='log')
        
        assert len(returns) == 2
        assert returns.iloc[0] > 0  # Price increased
        assert returns.iloc[1] < 0  # Price decreased
    
    def test_calculate_returns_dataframe(self):
        """Test returns calculation on DataFrame."""
        prices = pd.DataFrame({
            'A': [100, 105, 110],
            'B': [50, 52, 51]
        })
        
        returns = calculate_returns(prices, method='simple')
        
        assert isinstance(returns, pd.DataFrame)
        assert returns.shape == (2, 2)
        assert 'A' in returns.columns
        assert 'B' in returns.columns
    
    def test_calculate_returns_invalid_method(self):
        """Test that invalid method raises error."""
        prices = pd.Series([100, 105])
        
        with pytest.raises(ValueError):
            calculate_returns(prices, method='invalid')


class TestStatisticsCalculation:
    """Test statistics calculation functions."""
    
    def test_calculate_statistics_basic(self):
        """Test basic statistics calculation."""
        returns = pd.Series([0.01, -0.01, 0.02, -0.005, 0.015])
        
        stats = calculate_statistics(returns)
        
        assert 'mean' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'skew' in stats
        assert 'kurt' in stats
        assert 'annual_return' in stats
        assert 'annual_volatility' in stats
        assert 'sharpe' in stats
    
    def test_calculate_statistics_annualization(self):
        """Test annualization of statistics."""
        # Daily returns with mean 0.001 (0.1%)
        returns = pd.Series([0.001] * 100)
        
        stats = calculate_statistics(returns)
        
        # Annual return should be ~0.001 * 252
        assert abs(stats['annual_return'] - 0.252) < 0.01
        
        # Annual volatility should be std * sqrt(252)
        expected_vol = returns.std() * np.sqrt(252)
        assert abs(stats['annual_volatility'] - expected_vol) < 1e-10
    
    def test_calculate_statistics_sharpe(self):
        """Test Sharpe ratio calculation."""
        returns = pd.Series([0.01] * 100)  # Constant positive returns
        
        stats = calculate_statistics(returns)
        
        # Sharpe = annual_return / annual_volatility
        expected_sharpe = stats['annual_return'] / stats['annual_volatility']
        assert abs(stats['sharpe'] - expected_sharpe) < 1e-10


class TestVolatilityEstimation:
    """Test volatility estimation."""
    
    def test_estimate_volatility_basic(self):
        """Test basic volatility estimation."""
        # Generate prices with known volatility
        np.random.seed(42)
        n = 252
        returns = np.random.normal(0.0005, 0.01, n)  # ~15% annual vol
        prices = pd.Series(100 * np.exp(np.cumsum(returns)))
        
        vol = estimate_volatility(prices, window=30)
        
        assert isinstance(vol, (float, np.floating))
        assert vol > 0
        assert vol < 1  # Should be reasonable (< 100%)
    
    def test_estimate_volatility_window_size(self):
        """Test volatility estimation with different window sizes."""
        np.random.seed(42)
        returns = np.random.normal(0, 0.01, 100)
        prices = pd.Series(100 * np.exp(np.cumsum(returns)))
        
        vol_30 = estimate_volatility(prices, window=30)
        vol_60 = estimate_volatility(prices, window=60)
        
        # Both should be positive
        assert vol_30 > 0
        assert vol_60 > 0


class TestSyntheticDataGeneration:
    """Test synthetic data generation."""
    
    def test_generate_synthetic_prices_basic(self):
        """Test basic synthetic price generation."""
        df = generate_synthetic_prices('TEST', period='1y')
        
        assert isinstance(df, pd.DataFrame)
        assert 'Open' in df.columns
        assert 'High' in df.columns
        assert 'Low' in df.columns
        assert 'Close' in df.columns
        assert 'Adj Close' in df.columns
        assert 'Volume' in df.columns
        
        # Should have approximately 252 trading days
        assert 240 < len(df) < 260
    
    def test_generate_synthetic_prices_different_periods(self):
        """Test synthetic data generation for different periods."""
        df_1mo = generate_synthetic_prices('TEST', period='1mo')
        df_1y = generate_synthetic_prices('TEST', period='1y')
        df_5y = generate_synthetic_prices('TEST', period='5y')
        
        # Longer periods should have more data
        assert len(df_1mo) < len(df_1y) < len(df_5y)
        
        # 1 month should be ~20 days
        assert 15 < len(df_1mo) < 30
        
        # 5 years should be ~1260 days
        assert 1200 < len(df_5y) < 1300
    
    def test_generate_synthetic_prices_consistency(self):
        """Test that same ticker generates same data."""
        df1 = generate_synthetic_prices('AAPL', period='1y')
        df2 = generate_synthetic_prices('AAPL', period='1y')
        
        # Should be identical (same seed based on ticker)
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_generate_synthetic_prices_different_tickers(self):
        """Test that different tickers generate different data."""
        df1 = generate_synthetic_prices('AAPL', period='1y')
        df2 = generate_synthetic_prices('MSFT', period='1y')
        
        # Should be different
        assert not df1['Close'].equals(df2['Close'])
    
    def test_generate_synthetic_prices_realistic(self):
        """Test that synthetic prices are realistic."""
        df = generate_synthetic_prices('TEST', period='1y')
        
        # High should be >= Close
        assert (df['High'] >= df['Close']).all()
        
        # Low should be <= Close
        assert (df['Low'] <= df['Close']).all()
        
        # Volume should be positive
        assert (df['Volume'] > 0).all()
        
        # Prices should be positive
        assert (df['Close'] > 0).all()


class TestDataValidator:
    """Test data validation functionality."""
    
    def test_validate_date_range_valid(self):
        """Test validation of valid date range."""
        start = datetime(2020, 1, 1)
        end = datetime(2021, 1, 1)
        
        # Should not raise
        assert DataValidator.validate_date_range(start, end)
    
    def test_validate_date_range_invalid_order(self):
        """Test validation with start after end."""
        start = datetime(2021, 1, 1)
        end = datetime(2020, 1, 1)
        
        with pytest.raises(ValueError, match="Start date must be before end date"):
            DataValidator.validate_date_range(start, end)
    
    def test_validate_date_range_future(self):
        """Test validation with future end date."""
        start = datetime(2020, 1, 1)
        end = datetime.now() + timedelta(days=365)
        
        with pytest.raises(ValueError, match="cannot be in the future"):
            DataValidator.validate_date_range(start, end)
    
    def test_validate_date_range_string_dates(self):
        """Test validation with string dates."""
        # Should not raise
        assert DataValidator.validate_date_range('2020-01-01', '2021-01-01')
    
    def test_check_data_quality_sufficient(self):
        """Test data quality check with sufficient data."""
        data = pd.DataFrame({
            'A': range(100),
            'B': range(100, 200)
        })
        
        issues = DataValidator.check_data_quality(data, min_observations=30)
        
        assert issues is None
    
    def test_check_data_quality_insufficient(self):
        """Test data quality check with insufficient data."""
        data = pd.DataFrame({
            'A': range(10)
        })
        
        issues = DataValidator.check_data_quality(data, min_observations=30)
        
        assert issues is not None
        assert len(issues) > 0
        assert 'Insufficient data' in issues[0]
    
    def test_check_data_quality_missing_values(self):
        """Test data quality check with missing values."""
        data = pd.DataFrame({
            'A': [1, 2, None, 4, 5]
        })
        
        issues = DataValidator.check_data_quality(data)
        
        assert issues is not None
        assert any('missing values' in issue for issue in issues)
    
    def test_check_data_quality_zero_values(self):
        """Test data quality check with zero values."""
        data = pd.DataFrame({
            'A': [1, 2, 0, 4, 5]
        })
        
        issues = DataValidator.check_data_quality(data)
        
        assert issues is not None
        assert any('zero values' in issue for issue in issues)


class TestEdgeCases:
    """Test edge cases for data fetching."""
    
    def test_calculate_returns_single_price(self):
        """Test returns calculation with single price."""
        prices = pd.Series([100])
        
        returns = calculate_returns(prices)
        
        assert len(returns) == 0
    
    def test_calculate_returns_two_prices(self):
        """Test returns calculation with two prices."""
        prices = pd.Series([100, 105])
        
        returns = calculate_returns(prices)
        
        assert len(returns) == 1
        assert abs(returns.iloc[0] - 0.05) < 1e-10
    
    def test_estimate_volatility_insufficient_data(self):
        """Test volatility estimation with insufficient data."""
        prices = pd.Series([100, 101, 102])
        
        # Should still work but may give NaN
        vol = estimate_volatility(prices, window=30)
        
        # Result might be NaN due to insufficient data
        assert isinstance(vol, (float, np.floating)) or np.isnan(vol)
    
    def test_synthetic_prices_unknown_period(self):
        """Test synthetic data with unknown period."""
        # Should default to 1y
        df = generate_synthetic_prices('TEST', period='unknown')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
