"""
Unit tests for Streamlit app components.
Tests individual functions and components in isolation.
"""

import pytest
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from portfolio.markowitz import optimize_sharpe, optimize_min_variance
from portfolio.risk_parity import optimize_risk_parity, inverse_volatility_weights
from portfolio.efficient_frontier import compute_efficient_frontier
from factors.ff3_model import FF3Model
from factors.ff5_model import FF5Model
from factors.data_loader import generate_synthetic_factors


class TestPortfolioComponents:
    """Test portfolio optimization components used in Streamlit app."""
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """Generate sample portfolio data."""
        np.random.seed(42)
        n_assets = 5
        mean_returns = np.array([0.12, 0.10, 0.14, 0.08, 0.11])
        vols = np.array([0.20, 0.15, 0.25, 0.10, 0.18])
        
        corr = np.array([
            [1.0, 0.3, 0.4, 0.2, 0.35],
            [0.3, 1.0, 0.35, 0.25, 0.3],
            [0.4, 0.35, 1.0, 0.3, 0.4],
            [0.2, 0.25, 0.3, 1.0, 0.2],
            [0.35, 0.3, 0.4, 0.2, 1.0]
        ])
        
        cov_matrix = np.outer(vols, vols) * corr
        
        return mean_returns, cov_matrix
    
    def test_max_sharpe_optimization(self, sample_portfolio_data):
        """Test Maximum Sharpe Ratio optimization."""
        mean_returns, cov_matrix = sample_portfolio_data
        
        result = optimize_sharpe(mean_returns, cov_matrix, risk_free_rate=0.02)
        
        assert 'weights' in result
        assert 'return' in result
        assert 'volatility' in result
        assert 'sharpe' in result
        
        # Weights should sum to 1
        assert abs(result['weights'].sum() - 1.0) < 1e-6
        
        # All weights should be non-negative (long-only)
        assert np.all(result['weights'] >= -1e-6)
        
        # Sharpe ratio should be positive
        assert result['sharpe'] > 0
    
    def test_min_variance_optimization(self, sample_portfolio_data):
        """Test Minimum Variance optimization."""
        mean_returns, cov_matrix = sample_portfolio_data
        
        result = optimize_min_variance(mean_returns, cov_matrix)
        
        assert 'weights' in result
        assert 'volatility' in result
        
        # Weights should sum to 1
        assert abs(result['weights'].sum() - 1.0) < 1e-6
        
        # Should have lower volatility than equal weight
        equal_weight_vol = np.sqrt(np.dot(np.ones(5)/5, np.dot(cov_matrix, np.ones(5)/5)))
        assert result['volatility'] <= equal_weight_vol + 1e-6
    
    def test_risk_parity_optimization(self, sample_portfolio_data):
        """Test Risk Parity optimization."""
        _, cov_matrix = sample_portfolio_data
        
        result = optimize_risk_parity(cov_matrix)
        
        assert 'weights' in result
        assert 'risk_contributions' in result
        
        # Weights should sum to 1
        assert abs(result['weights'].sum() - 1.0) < 1e-6
        
        # Risk contributions should be approximately equal
        risk_contrib = result['risk_contributions']
        assert np.std(risk_contrib) < 0.05  # Low standard deviation
    
    def test_inverse_volatility_weights(self, sample_portfolio_data):
        """Test Inverse Volatility weighting."""
        _, cov_matrix = sample_portfolio_data
        
        weights = inverse_volatility_weights(cov_matrix)
        
        # Weights should sum to 1
        assert abs(weights.sum() - 1.0) < 1e-6
        
        # All weights should be positive
        assert np.all(weights > 0)
    
    def test_efficient_frontier_computation(self, sample_portfolio_data):
        """Test efficient frontier computation."""
        mean_returns, cov_matrix = sample_portfolio_data
        
        result = compute_efficient_frontier(
            mean_returns, cov_matrix, n_points=20
        )
        
        assert len(result['returns']) <= 20  # May be less if some targets fail
        assert len(result['volatilities']) == len(result['returns'])
        assert len(result['weights']) == len(result['returns'])
        
        # Returns should be in ascending order
        assert np.all(np.diff(result['returns']) >= -1e-6)
        
        # All portfolios should have weights summing to 1
        for weights in result['weights']:
            assert abs(weights.sum() - 1.0) < 1e-6


class TestFactorModelComponents:
    """Test factor model components used in Streamlit app."""
    
    @pytest.fixture
    def sample_factor_data(self):
        """Generate sample factor data."""
        np.random.seed(42)
        
        # Generate FF3 data
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=1)
        
        # Generate stock returns
        n_obs = len(factor_data)
        stock_returns = (
            0.0001 +
            1.2 * factor_data['Mkt-RF'] +
            0.3 * factor_data['SMB'] +
            -0.2 * factor_data['HML'] +
            np.random.normal(0, 0.01, n_obs)
        )
        
        return stock_returns, factor_data
    
    def test_ff3_model_fitting(self, sample_factor_data):
        """Test FF3 model fitting."""
        stock_returns, factor_data = sample_factor_data
        
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        
        assert model.results is not None
        assert model.alpha is not None
        assert model.betas is not None
        assert model.r_squared is not None
        
        # Should have 3 betas
        assert len(model.betas) == 3
        assert 'Mkt-RF' in model.betas
        assert 'SMB' in model.betas
        assert 'HML' in model.betas
    
    def test_ff3_summary(self, sample_factor_data):
        """Test FF3 summary generation."""
        stock_returns, factor_data = sample_factor_data
        
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        summary = model.summary(annualize=True)
        
        assert 'alpha' in summary
        assert 'betas' in summary
        assert 'r_squared' in summary
        assert 'alpha_t_stat' in summary
        assert 'alpha_p_value' in summary
        assert 'beta_t_stats' in summary
        assert 'beta_p_values' in summary
        assert 'observations' in summary
    
    def test_ff5_model_fitting(self):
        """Test FF5 model fitting."""
        np.random.seed(42)
        
        # Generate FF5 data
        factor_data = generate_synthetic_factors(model='5', frequency='daily', years=1)
        
        # Generate stock returns
        n_obs = len(factor_data)
        stock_returns = (
            0.0001 +
            1.1 * factor_data['Mkt-RF'] +
            0.2 * factor_data['SMB'] +
            -0.1 * factor_data['HML'] +
            0.25 * factor_data['RMW'] +
            -0.15 * factor_data['CMA'] +
            np.random.normal(0, 0.01, n_obs)
        )
        
        model = FF5Model()
        model.fit(stock_returns, factor_data)
        
        assert model.results is not None
        
        # Should have 5 betas
        assert len(model.betas) == 5
        assert 'RMW' in model.betas
        assert 'CMA' in model.betas
    
    def test_synthetic_data_generation(self):
        """Test synthetic factor data generation."""
        # Daily data
        df_daily = generate_synthetic_factors(model='3', frequency='daily', years=1)
        assert len(df_daily) == 252
        assert 'Mkt-RF' in df_daily.columns
        assert 'SMB' in df_daily.columns
        assert 'HML' in df_daily.columns
        assert 'RF' in df_daily.columns
        
        # Monthly data
        df_monthly = generate_synthetic_factors(model='3', frequency='monthly', years=1)
        assert len(df_monthly) == 12
        
        # FF5 data
        df_ff5 = generate_synthetic_factors(model='5', frequency='daily', years=1)
        assert 'RMW' in df_ff5.columns
        assert 'CMA' in df_ff5.columns
        
        # No NaN values
        assert not df_daily.isnull().any().any()
        assert not df_monthly.isnull().any().any()
        assert not df_ff5.isnull().any().any()


class TestDataValidation:
    """Test data validation used in Streamlit app."""
    
    def test_valid_covariance_matrix(self):
        """Test validation of valid covariance matrix."""
        from utils.validation import validate_covariance_matrix
        
        # Valid covariance matrix
        cov = np.array([
            [0.04, 0.006, 0.008],
            [0.006, 0.0225, 0.00525],
            [0.008, 0.00525, 0.0625]
        ])
        
        # Should not raise
        validate_covariance_matrix(cov)
    
    def test_invalid_covariance_matrix(self):
        """Test validation of invalid covariance matrix."""
        from utils.validation import validate_covariance_matrix, ValidationError
        
        # Non-symmetric matrix
        cov = np.array([
            [0.04, 0.006, 0.008],
            [0.007, 0.0225, 0.00525],  # Not symmetric
            [0.008, 0.00525, 0.0625]
        ])
        
        with pytest.raises(ValidationError):
            validate_covariance_matrix(cov)
    
    def test_valid_weights(self):
        """Test validation of valid portfolio weights."""
        from utils.validation import validate_weights
        
        weights = np.array([0.3, 0.25, 0.2, 0.15, 0.1])
        
        # Should not raise
        validate_weights(weights, allow_short=False)
    
    def test_invalid_weights_sum(self):
        """Test validation of weights that don't sum to 1."""
        from utils.validation import validate_weights, ValidationError
        
        weights = np.array([0.3, 0.25, 0.2, 0.15])  # Sums to 0.9
        
        with pytest.raises(ValidationError):
            validate_weights(weights, allow_short=False)
    
    def test_invalid_weights_negative(self):
        """Test validation of negative weights when not allowed."""
        from utils.validation import validate_weights, ValidationError
        
        weights = np.array([0.4, 0.3, 0.5, -0.2])  # Has negative
        
        with pytest.raises(ValidationError):
            validate_weights(weights, allow_short=False)


class TestCalculationAccuracy:
    """Test accuracy of calculations used in app."""
    
    def test_portfolio_metrics_accuracy(self):
        """Test portfolio return and volatility calculations."""
        from portfolio.markowitz import portfolio_return, portfolio_volatility
        
        weights = np.array([0.5, 0.5])
        mean_returns = np.array([0.10, 0.12])
        cov_matrix = np.array([
            [0.04, 0.006],
            [0.006, 0.0225]
        ])
        
        ret = portfolio_return(weights, mean_returns)
        vol = portfolio_volatility(weights, cov_matrix)
        
        # Expected return: 0.5*0.10 + 0.5*0.12 = 0.11
        assert abs(ret - 0.11) < 1e-10
        
        # Expected volatility: sqrt(0.5^2*0.04 + 0.5^2*0.0225 + 2*0.5*0.5*0.006)
        expected_vol = np.sqrt(0.25*0.04 + 0.25*0.0225 + 0.5*0.006)
        assert abs(vol - expected_vol) < 1e-10
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        from portfolio.markowitz import portfolio_sharpe
        
        weights = np.array([0.6, 0.4])
        mean_returns = np.array([0.12, 0.08])
        cov_matrix = np.array([
            [0.04, 0.006],
            [0.006, 0.0225]
        ])
        risk_free_rate = 0.02
        
        sharpe = portfolio_sharpe(weights, mean_returns, cov_matrix, risk_free_rate)
        
        # Calculate expected
        ret = 0.6*0.12 + 0.4*0.08
        vol = np.sqrt(0.36*0.04 + 0.16*0.0225 + 2*0.24*0.006)
        expected_sharpe = (ret - risk_free_rate) / vol
        
        assert abs(sharpe - expected_sharpe) < 1e-10


class TestEdgeCases:
    """Test edge cases that might occur in Streamlit app."""
    
    def test_single_asset_portfolio(self):
        """Test optimization with single asset."""
        from portfolio.markowitz import optimize_sharpe
        
        mean_returns = np.array([0.10])
        cov_matrix = np.array([[0.04]])
        
        result = optimize_sharpe(mean_returns, cov_matrix)
        
        # Should allocate 100% to single asset
        assert abs(result['weights'][0] - 1.0) < 1e-6
    
    def test_zero_correlation_assets(self):
        """Test portfolio with uncorrelated assets."""
        from portfolio.markowitz import optimize_sharpe
        
        mean_returns = np.array([0.10, 0.12, 0.08])
        vols = np.array([0.15, 0.20, 0.10])
        corr = np.eye(3)  # Zero correlation
        cov_matrix = np.outer(vols, vols) * corr
        
        result = optimize_sharpe(mean_returns, cov_matrix, risk_free_rate=0.02)
        
        # Should still produce valid weights
        assert abs(result['weights'].sum() - 1.0) < 1e-6
        assert np.all(result['weights'] >= -1e-6)
    
    def test_very_short_time_series(self):
        """Test factor model with minimal data."""
        np.random.seed(42)
        
        # Only 30 observations
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=1)
        factor_data = factor_data.iloc[:30]
        
        stock_returns = (
            0.0001 +
            1.2 * factor_data['Mkt-RF'] +
            np.random.normal(0, 0.01, 30)
        )
        
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        
        # Should still fit, though with lower confidence
        assert model.results is not None
        summary = model.summary()
        assert summary['observations'] == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
