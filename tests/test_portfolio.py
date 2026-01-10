"""
Unit tests for portfolio optimization module.
Tests Markowitz, Risk Parity, and backtesting.
"""

import pytest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from portfolio.markowitz import (
    portfolio_return, portfolio_volatility, portfolio_sharpe,
    optimize_sharpe, optimize_min_variance, optimize_target_return
)
from portfolio.risk_parity import (
    risk_contribution, risk_contribution_pct,
    optimize_risk_parity, inverse_volatility_weights
)


class TestPortfolioMetrics:
    """Test basic portfolio calculations."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample portfolio data."""
        mean_returns = np.array([0.10, 0.12, 0.08])
        cov_matrix = np.array([
            [0.04, 0.01, 0.02],
            [0.01, 0.09, 0.03],
            [0.02, 0.03, 0.16]
        ])
        return mean_returns, cov_matrix
    
    def test_portfolio_return(self, sample_data):
        """Test portfolio return calculation."""
        mean_returns, _ = sample_data
        weights = np.array([0.4, 0.3, 0.3])
        
        ret = portfolio_return(weights, mean_returns)
        expected = 0.4 * 0.10 + 0.3 * 0.12 + 0.3 * 0.08
        
        assert abs(ret - expected) < 1e-10, "Portfolio return calculation error"
    
    def test_portfolio_volatility(self, sample_data):
        """Test portfolio volatility calculation."""
        _, cov_matrix = sample_data
        weights = np.array([1.0, 0.0, 0.0])  # 100% in first asset
        
        vol = portfolio_volatility(weights, cov_matrix)
        expected = np.sqrt(cov_matrix[0, 0])
        
        assert abs(vol - expected) < 1e-10, "Single asset vol calculation error"
    
    def test_portfolio_sharpe(self, sample_data):
        """Test Sharpe ratio calculation."""
        mean_returns, cov_matrix = sample_data
        weights = np.array([0.4, 0.3, 0.3])
        
        sharpe = portfolio_sharpe(weights, mean_returns, cov_matrix, risk_free_rate=0.02)
        
        ret = portfolio_return(weights, mean_returns)
        vol = portfolio_volatility(weights, cov_matrix)
        expected = (ret - 0.02) / vol
        
        assert abs(sharpe - expected) < 1e-10, "Sharpe ratio calculation error"


class TestMarkowitz:
    """Test mean-variance optimization."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample portfolio data."""
        mean_returns = np.array([0.10, 0.12, 0.08, 0.15])
        vols = np.array([0.15, 0.20, 0.10, 0.25])
        corr = np.array([
            [1.0, 0.3, 0.2, 0.4],
            [0.3, 1.0, 0.1, 0.5],
            [0.2, 0.1, 1.0, 0.3],
            [0.4, 0.5, 0.3, 1.0]
        ])
        cov_matrix = np.outer(vols, vols) * corr
        return mean_returns, cov_matrix
    
    def test_optimize_sharpe_weights_sum_to_one(self, sample_data):
        """Test optimized weights sum to 1."""
        mean_returns, cov_matrix = sample_data
        
        result = optimize_sharpe(mean_returns, cov_matrix)
        
        assert abs(np.sum(result['weights']) - 1.0) < 1e-6, "Weights don't sum to 1"
    
    def test_optimize_sharpe_long_only(self, sample_data):
        """Test long-only constraint."""
        mean_returns, cov_matrix = sample_data
        
        result = optimize_sharpe(mean_returns, cov_matrix, allow_short=False)
        
        assert np.all(result['weights'] >= -1e-6), "Negative weights in long-only"
    
    def test_optimize_sharpe_improves_equal_weight(self, sample_data):
        """Test optimized Sharpe exceeds equal weight."""
        mean_returns, cov_matrix = sample_data
        n = len(mean_returns)
        
        # Equal weight Sharpe
        eq_weights = np.ones(n) / n
        eq_sharpe = portfolio_sharpe(eq_weights, mean_returns, cov_matrix)
        
        # Optimized Sharpe
        result = optimize_sharpe(mean_returns, cov_matrix)
        
        assert result['sharpe'] >= eq_sharpe - 0.01, "Optimization didn't improve Sharpe"
    
    def test_min_variance_has_lowest_vol(self, sample_data):
        """Test min variance portfolio has lowest volatility."""
        mean_returns, cov_matrix = sample_data
        
        result = optimize_min_variance(mean_returns, cov_matrix)
        
        # Check against equal weight
        n = len(mean_returns)
        eq_weights = np.ones(n) / n
        eq_vol = portfolio_volatility(eq_weights, cov_matrix)
        
        assert result['volatility'] <= eq_vol + 0.01, "Min var doesn't minimize vol"
    
    def test_target_return_achieves_target(self, sample_data):
        """Test target return optimization."""
        mean_returns, cov_matrix = sample_data
        target = 0.11
        
        weights, vol = optimize_target_return(mean_returns, cov_matrix, target)
        
        if weights is not None:
            actual_return = portfolio_return(weights, mean_returns)
            assert abs(actual_return - target) < 1e-4, "Didn't achieve target return"


class TestRiskParity:
    """Test risk parity optimization."""
    
    @pytest.fixture
    def sample_cov(self):
        """Sample covariance matrix."""
        vols = np.array([0.15, 0.20, 0.10, 0.25])
        corr = np.array([
            [1.0, 0.3, 0.2, 0.4],
            [0.3, 1.0, 0.1, 0.5],
            [0.2, 0.1, 1.0, 0.3],
            [0.4, 0.5, 0.3, 1.0]
        ])
        return np.outer(vols, vols) * corr
    
    def test_risk_parity_weights_sum_to_one(self, sample_cov):
        """Test risk parity weights sum to 1."""
        result = optimize_risk_parity(sample_cov)
        
        assert abs(np.sum(result['weights']) - 1.0) < 1e-6, "Weights don't sum to 1"
    
    def test_risk_parity_equal_contributions(self, sample_cov):
        """Test risk contributions are approximately equal."""
        result = optimize_risk_parity(sample_cov)
        
        rc = result['risk_contributions']
        
        # Standard deviation of risk contributions should be small
        rc_std = np.std(rc)
        assert rc_std < 0.05, f"Risk contributions not equal, std={rc_std}"
    
    def test_risk_contributions_sum_to_one(self, sample_cov):
        """Test risk contribution percentages sum to 1."""
        weights = np.array([0.3, 0.3, 0.2, 0.2])
        
        rc_pct = risk_contribution_pct(weights, sample_cov)
        
        assert abs(np.sum(rc_pct) - 1.0) < 1e-10, "Risk contributions don't sum to 1"
    
    def test_inverse_vol_weights(self, sample_cov):
        """Test inverse volatility weighting."""
        weights = inverse_volatility_weights(sample_cov)
        
        assert abs(np.sum(weights) - 1.0) < 1e-10, "Inv vol weights don't sum to 1"
        assert np.all(weights > 0), "Inv vol weights should be positive"
        
        # Lower vol assets should have higher weights
        vols = np.sqrt(np.diag(sample_cov))
        # Asset 2 (index 2) has lowest vol, should have highest weight
        assert weights[2] == np.max(weights), "Lowest vol doesn't have highest weight"


class TestConstraints:
    """Test optimization constraints."""
    
    def test_weights_non_negative_long_only(self):
        """Test long-only constraint is enforced."""
        mean_returns = np.array([0.10, 0.12, 0.08])
        cov_matrix = np.array([
            [0.04, 0.01, 0.02],
            [0.01, 0.09, 0.03],
            [0.02, 0.03, 0.16]
        ])
        
        result = optimize_sharpe(mean_returns, cov_matrix, allow_short=False)
        
        assert np.all(result['weights'] >= -1e-6), "Long-only constraint violated"
    
    def test_weights_sum_constraint(self):
        """Test weights sum to 1 constraint."""
        mean_returns = np.array([0.10, 0.12, 0.08])
        cov_matrix = np.array([
            [0.04, 0.01, 0.02],
            [0.01, 0.09, 0.03],
            [0.02, 0.03, 0.16]
        ])
        
        result = optimize_sharpe(mean_returns, cov_matrix)
        
        assert abs(np.sum(result['weights']) - 1.0) < 1e-6, "Sum constraint violated"


class TestEdgeCases:
    """Test edge cases in portfolio optimization."""
    
    def test_single_asset_portfolio(self):
        """Test portfolio with single asset."""
        mean_returns = np.array([0.10])
        cov_matrix = np.array([[0.04]])
        
        result = optimize_sharpe(mean_returns, cov_matrix)
        
        assert abs(result['weights'][0] - 1.0) < 1e-6, "Single asset weight != 1"
    
    def test_uncorrelated_assets(self):
        """Test portfolio with uncorrelated assets."""
        mean_returns = np.array([0.10, 0.12, 0.08])
        vols = np.array([0.15, 0.20, 0.10])
        cov_matrix = np.diag(vols ** 2)  # Zero correlation
        
        result = optimize_sharpe(mean_returns, cov_matrix)
        
        # Should prefer highest Sharpe ratio asset
        sharpes = (mean_returns - 0.02) / vols
        best_asset = np.argmax(sharpes)
        
        # Best asset should have significant weight
        assert result['weights'][best_asset] > 0.3, "Didn't favor best Sharpe asset"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
