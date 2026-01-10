"""
Unit tests for factor models module.
Tests Fama-French 3-Factor and 5-Factor models.
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from factors.ff3_model import FF3Model
from factors.ff5_model import FF5Model
from factors.data_loader import generate_synthetic_factors, align_data


class TestSyntheticDataGeneration:
    """Test synthetic factor data generation."""
    
    def test_ff3_synthetic_data_shape(self):
        """Test FF3 synthetic data has correct shape."""
        df = generate_synthetic_factors(model='3', frequency='daily', years=1)
        
        assert len(df) == 252, f"Expected 252 daily observations, got {len(df)}"
        assert 'Mkt-RF' in df.columns, "Missing Mkt-RF column"
        assert 'SMB' in df.columns, "Missing SMB column"
        assert 'HML' in df.columns, "Missing HML column"
        assert 'RF' in df.columns, "Missing RF column"
    
    def test_ff5_synthetic_data_shape(self):
        """Test FF5 synthetic data has correct shape."""
        df = generate_synthetic_factors(model='5', frequency='daily', years=1)
        
        assert len(df) == 252, f"Expected 252 daily observations, got {len(df)}"
        assert 'RMW' in df.columns, "Missing RMW column"
        assert 'CMA' in df.columns, "Missing CMA column"
    
    def test_monthly_data_shape(self):
        """Test monthly data has correct shape."""
        df = generate_synthetic_factors(model='3', frequency='monthly', years=1)
        
        assert len(df) == 12, f"Expected 12 monthly observations, got {len(df)}"
    
    def test_no_nan_values(self):
        """Test synthetic data has no NaN values."""
        df = generate_synthetic_factors(model='5', frequency='daily', years=1)
        
        assert not df.isnull().any().any(), "Synthetic data contains NaN values"
    
    def test_reasonable_factor_values(self):
        """Test factor values are in reasonable ranges."""
        df = generate_synthetic_factors(model='3', frequency='daily', years=1)
        
        # Daily returns should typically be < 10%
        assert df['Mkt-RF'].abs().max() < 0.10, "Market returns too extreme"
        assert df['SMB'].abs().max() < 0.10, "SMB returns too extreme"
        assert df['HML'].abs().max() < 0.10, "HML returns too extreme"


class TestFF3Model:
    """Test Fama-French 3-Factor model."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for testing."""
        np.random.seed(42)
        n_obs = 252
        
        # Generate factors
        factors = pd.DataFrame({
            'Mkt-RF': np.random.normal(0.0003, 0.01, n_obs),
            'SMB': np.random.normal(0.0001, 0.005, n_obs),
            'HML': np.random.normal(0.0001, 0.005, n_obs),
            'RF': np.ones(n_obs) * 0.00008  # ~2% annual
        }, index=pd.date_range('2023-01-01', periods=n_obs, freq='B'))
        
        # Generate stock returns with known betas
        true_alpha = 0.0001  # ~2.5% annual
        true_beta_mkt = 1.2
        true_beta_smb = 0.3
        true_beta_hml = -0.2
        
        stock_returns = (
            true_alpha +
            true_beta_mkt * factors['Mkt-RF'] +
            true_beta_smb * factors['SMB'] +
            true_beta_hml * factors['HML'] +
            np.random.normal(0, 0.005, n_obs)  # Idiosyncratic risk
        )
        
        excess_returns = stock_returns
        
        return excess_returns, factors, {
            'alpha': true_alpha,
            'beta_mkt': true_beta_mkt,
            'beta_smb': true_beta_smb,
            'beta_hml': true_beta_hml
        }
    
    def test_model_initialization(self):
        """Test FF3Model initializes correctly."""
        model = FF3Model()
        
        assert model.model is None, "Model should be None before fitting"
        assert model.results is None, "Results should be None before fitting"
        assert model.alpha is None, "Alpha should be None before fitting"
        assert model.betas is None, "Betas should be None before fitting"
        assert model.factor_names == ['Mkt-RF', 'SMB', 'HML'], "Incorrect factor names"
    
    def test_model_fit(self, sample_data):
        """Test model fitting."""
        excess_returns, factors, true_params = sample_data
        
        model = FF3Model()
        model.fit(excess_returns, factors)
        
        assert model.results is not None, "Results should be set after fitting"
        assert model.alpha is not None, "Alpha should be set after fitting"
        assert model.betas is not None, "Betas should be set after fitting"
        assert isinstance(model.betas, dict), "Betas should be a dictionary"
    
    def test_beta_recovery(self, sample_data):
        """Test that fitted betas are close to true values."""
        excess_returns, factors, true_params = sample_data
        
        model = FF3Model()
        model.fit(excess_returns, factors)
        
        # Check market beta (should be close to 1.2)
        assert 1.0 < model.betas['Mkt-RF'] < 1.4, \
            f"Market beta {model.betas['Mkt-RF']} far from true value 1.2"
        
        # Check SMB beta (should be close to 0.3)
        assert 0.1 < model.betas['SMB'] < 0.5, \
            f"SMB beta {model.betas['SMB']} far from true value 0.3"
        
        # Check HML beta (should be close to -0.2)
        assert -0.4 < model.betas['HML'] < 0.0, \
            f"HML beta {model.betas['HML']} far from true value -0.2"
    
    def test_r_squared_reasonable(self, sample_data):
        """Test R-squared is in reasonable range."""
        excess_returns, factors, true_params = sample_data
        
        model = FF3Model()
        model.fit(excess_returns, factors)
        
        assert 0 <= model.r_squared <= 1, "R-squared must be between 0 and 1"
        # With our synthetic data, R-squared should be reasonably high
        assert model.r_squared > 0.5, f"R-squared {model.r_squared} unexpectedly low"
    
    def test_summary_method(self, sample_data):
        """Test summary method returns correct structure."""
        excess_returns, factors, true_params = sample_data
        
        model = FF3Model()
        model.fit(excess_returns, factors)
        
        summary = model.summary(annualize=True)
        
        assert 'alpha' in summary, "Summary missing alpha"
        assert 'betas' in summary, "Summary missing betas"
        assert 'r_squared' in summary, "Summary missing R-squared"
        assert 'alpha_t_stat' in summary, "Summary missing alpha t-stat"
        assert 'beta_t_stats' in summary, "Summary missing beta t-stats"
        assert 'observations' in summary, "Summary missing observations"
    
    def test_predict_method(self, sample_data):
        """Test prediction method."""
        excess_returns, factors, true_params = sample_data
        
        model = FF3Model()
        model.fit(excess_returns, factors)
        
        # Predict on same data
        predictions = model.predict(factors)
        
        assert len(predictions) == len(excess_returns), "Predictions wrong length"
        assert not np.any(np.isnan(predictions)), "Predictions contain NaN"
    
    def test_fit_without_data_raises_error(self):
        """Test that fitting without data raises appropriate error."""
        model = FF3Model()
        
        # Try to get summary before fitting
        with pytest.raises(ValueError, match="Model not fitted"):
            model.summary()


class TestFF5Model:
    """Test Fama-French 5-Factor model."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample data for FF5 testing."""
        np.random.seed(42)
        n_obs = 252
        
        # Generate factors
        factors = pd.DataFrame({
            'Mkt-RF': np.random.normal(0.0003, 0.01, n_obs),
            'SMB': np.random.normal(0.0001, 0.005, n_obs),
            'HML': np.random.normal(0.0001, 0.005, n_obs),
            'RMW': np.random.normal(0.0001, 0.004, n_obs),
            'CMA': np.random.normal(0.0001, 0.004, n_obs),
            'RF': np.ones(n_obs) * 0.00008
        }, index=pd.date_range('2023-01-01', periods=n_obs, freq='B'))
        
        # Generate stock returns with known betas
        true_beta_mkt = 1.1
        true_beta_smb = 0.2
        true_beta_hml = -0.1
        true_beta_rmw = 0.3
        true_beta_cma = -0.2
        
        stock_returns = (
            0.0001 +
            true_beta_mkt * factors['Mkt-RF'] +
            true_beta_smb * factors['SMB'] +
            true_beta_hml * factors['HML'] +
            true_beta_rmw * factors['RMW'] +
            true_beta_cma * factors['CMA'] +
            np.random.normal(0, 0.005, n_obs)
        )
        
        return stock_returns, factors
    
    def test_model_initialization(self):
        """Test FF5Model initializes correctly."""
        model = FF5Model()
        
        assert model.factor_names == ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'], \
            "Incorrect factor names for FF5"
    
    def test_model_fit(self, sample_data):
        """Test FF5 model fitting."""
        excess_returns, factors = sample_data
        
        model = FF5Model()
        model.fit(excess_returns, factors)
        
        assert model.results is not None, "Results should be set after fitting"
        assert len(model.betas) == 5, "Should have 5 betas"
        assert 'RMW' in model.betas, "Missing RMW beta"
        assert 'CMA' in model.betas, "Missing CMA beta"
    
    def test_ff5_vs_ff3_r_squared(self, sample_data):
        """Test that FF5 has higher R-squared than FF3."""
        excess_returns, factors = sample_data
        
        # Fit FF3
        ff3_factors = factors[['Mkt-RF', 'SMB', 'HML', 'RF']]
        ff3 = FF3Model()
        ff3.fit(excess_returns, ff3_factors)
        
        # Fit FF5
        ff5 = FF5Model()
        ff5.fit(excess_returns, factors)
        
        # FF5 should have equal or higher R-squared
        assert ff5.r_squared >= ff3.r_squared - 0.01, \
            f"FF5 R² ({ff5.r_squared}) should be >= FF3 R² ({ff3.r_squared})"
    
    def test_summary_includes_new_factors(self, sample_data):
        """Test summary includes RMW and CMA."""
        excess_returns, factors = sample_data
        
        model = FF5Model()
        model.fit(excess_returns, factors)
        
        summary = model.summary()
        
        assert 'RMW' in summary['betas'], "Summary missing RMW beta"
        assert 'CMA' in summary['betas'], "Summary missing CMA beta"
        assert 'RMW' in summary['beta_t_stats'], "Summary missing RMW t-stat"
        assert 'CMA' in summary['beta_t_stats'], "Summary missing CMA t-stat"


class TestDataAlignment:
    """Test data alignment functionality."""
    
    def test_align_data_basic(self):
        """Test basic data alignment."""
        # Create stock returns
        dates = pd.date_range('2023-01-01', periods=100, freq='B')
        stock_returns = pd.Series(
            np.random.normal(0.001, 0.01, 100),
            index=dates
        )
        
        # Create factor data (overlapping dates)
        factor_data = pd.DataFrame({
            'Mkt-RF': np.random.normal(0.0003, 0.01, 100),
            'SMB': np.random.normal(0.0001, 0.005, 100),
            'HML': np.random.normal(0.0001, 0.005, 100),
            'RF': np.ones(100) * 0.00008
        }, index=dates)
        
        excess_returns, aligned_factors = align_data(stock_returns, factor_data)
        
        assert len(excess_returns) == 100, "Aligned data wrong length"
        assert len(aligned_factors) == 100, "Aligned factors wrong length"
        assert excess_returns.index.equals(aligned_factors.index), \
            "Indices don't match after alignment"
    
    def test_align_data_partial_overlap(self):
        """Test alignment with partial date overlap."""
        # Stock returns: 2023-01-01 to 2023-04-30
        stock_dates = pd.date_range('2023-01-01', periods=100, freq='B')
        stock_returns = pd.Series(
            np.random.normal(0.001, 0.01, 100),
            index=stock_dates
        )
        
        # Factor data: 2023-02-01 to 2023-05-31 (partial overlap)
        factor_dates = pd.date_range('2023-02-01', periods=100, freq='B')
        factor_data = pd.DataFrame({
            'Mkt-RF': np.random.normal(0.0003, 0.01, 100),
            'SMB': np.random.normal(0.0001, 0.005, 100),
            'HML': np.random.normal(0.0001, 0.005, 100),
            'RF': np.ones(100) * 0.00008
        }, index=factor_dates)
        
        excess_returns, aligned_factors = align_data(stock_returns, factor_data)
        
        # Should only have overlapping dates
        assert len(excess_returns) < 100, "Should have fewer observations after alignment"
        assert len(excess_returns) > 0, "Should have some overlapping dates"


class TestModelStatistics:
    """Test statistical properties of fitted models."""
    
    @pytest.fixture
    def fitted_model(self):
        """Create a fitted FF3 model."""
        np.random.seed(42)
        n_obs = 252
        
        factors = pd.DataFrame({
            'Mkt-RF': np.random.normal(0.0003, 0.01, n_obs),
            'SMB': np.random.normal(0.0001, 0.005, n_obs),
            'HML': np.random.normal(0.0001, 0.005, n_obs),
            'RF': np.ones(n_obs) * 0.00008
        }, index=pd.date_range('2023-01-01', periods=n_obs, freq='B'))
        
        stock_returns = (
            0.0001 +
            1.2 * factors['Mkt-RF'] +
            0.3 * factors['SMB'] +
            -0.2 * factors['HML'] +
            np.random.normal(0, 0.005, n_obs)
        )
        
        model = FF3Model()
        model.fit(stock_returns, factors)
        return model
    
    def test_t_statistics_exist(self, fitted_model):
        """Test that t-statistics are calculated."""
        summary = fitted_model.summary()
        
        assert summary['alpha_t_stat'] is not None, "Alpha t-stat missing"
        assert all(t is not None for t in summary['beta_t_stats'].values()), \
            "Some beta t-stats missing"
    
    def test_p_values_in_range(self, fitted_model):
        """Test that p-values are in valid range [0, 1]."""
        summary = fitted_model.summary()
        
        assert 0 <= summary['alpha_p_value'] <= 1, "Alpha p-value out of range"
        assert all(0 <= p <= 1 for p in summary['beta_p_values'].values()), \
            "Some beta p-values out of range"
    
    def test_significant_market_beta(self, fitted_model):
        """Test that market beta is statistically significant."""
        summary = fitted_model.summary()
        
        # Market beta should be highly significant (p < 0.05)
        assert summary['beta_p_values']['Mkt-RF'] < 0.05, \
            "Market beta should be statistically significant"
    
    def test_annualized_alpha(self, fitted_model):
        """Test annualized alpha calculation."""
        summary_daily = fitted_model.summary(annualize=False)
        summary_annual = fitted_model.summary(annualize=True)
        
        # Annualized should be ~252x daily
        ratio = summary_annual['alpha'] / summary_daily['alpha']
        assert 240 < ratio < 260, f"Annualization factor {ratio} not close to 252"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_perfect_correlation(self):
        """Test model with perfectly correlated factor."""
        np.random.seed(42)
        n_obs = 100
        
        # Create factors where SMB = 2 * Mkt-RF (perfect correlation)
        mkt_rf = np.random.normal(0.001, 0.01, n_obs)
        factors = pd.DataFrame({
            'Mkt-RF': mkt_rf,
            'SMB': 2 * mkt_rf,  # Perfect correlation
            'HML': np.random.normal(0.0001, 0.005, n_obs),
            'RF': np.ones(n_obs) * 0.00008
        }, index=pd.date_range('2023-01-01', periods=n_obs, freq='B'))
        
        stock_returns = mkt_rf + np.random.normal(0, 0.005, n_obs)
        
        model = FF3Model()
        # Should still fit, but may have issues with multicollinearity
        model.fit(stock_returns, factors)
        
        assert model.results is not None, "Model should fit despite multicollinearity"
    
    def test_zero_variance_factor(self):
        """Test model with zero-variance factor."""
        np.random.seed(42)
        n_obs = 100
        
        factors = pd.DataFrame({
            'Mkt-RF': np.random.normal(0.001, 0.01, n_obs),
            'SMB': np.zeros(n_obs),  # Zero variance
            'HML': np.random.normal(0.0001, 0.005, n_obs),
            'RF': np.ones(n_obs) * 0.00008
        }, index=pd.date_range('2023-01-01', periods=n_obs, freq='B'))
        
        stock_returns = np.random.normal(0.001, 0.01, n_obs)
        
        model = FF3Model()
        # Should handle gracefully
        model.fit(stock_returns, factors)
        
        # SMB beta should be close to 0 with zero variance
        assert abs(model.betas['SMB']) < 0.1, "Zero variance factor should have near-zero beta"
    
    def test_very_short_time_series(self):
        """Test model with very short time series."""
        n_obs = 30  # Only 30 observations
        
        factors = pd.DataFrame({
            'Mkt-RF': np.random.normal(0.001, 0.01, n_obs),
            'SMB': np.random.normal(0.0001, 0.005, n_obs),
            'HML': np.random.normal(0.0001, 0.005, n_obs),
            'RF': np.ones(n_obs) * 0.00008
        }, index=pd.date_range('2023-01-01', periods=n_obs, freq='B'))
        
        stock_returns = np.random.normal(0.001, 0.01, n_obs)
        
        model = FF3Model()
        model.fit(stock_returns, factors)
        
        summary = model.summary()
        assert summary['observations'] == n_obs, "Observation count incorrect"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
