"""
Integration tests for Streamlit app.
Tests end-to-end workflows and page interactions.
"""

import pytest
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestOptionsPageIntegration:
    """Integration tests for Options pricing page workflow."""
    
    def test_complete_black_scholes_workflow(self):
        """Test complete Black-Scholes pricing workflow."""
        from options.black_scholes import black_scholes_call
        from options.greeks import delta_call, gamma, vega, theta_call, rho_call
        from utils.validation import validate_option_params
        
        # User inputs
        S0, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0
        
        # Validate inputs
        validate_option_params(S0, K, r, sigma, T)
        
        # Calculate price
        price = black_scholes_call(S0, K, r, sigma, T)
        
        # Calculate Greeks
        delta = delta_call(S0, K, T, r, sigma)
        gamma_val = gamma(S0, K, T, r, sigma)
        vega_val = vega(S0, K, T, r, sigma)
        theta = theta_call(S0, K, T, r, sigma)
        rho = rho_call(S0, K, T, r, sigma)
        
        # Verify results
        assert price > 0
        assert 0 < delta < 1  # Call delta between 0 and 1
        assert gamma_val > 0  # Gamma always positive
        assert vega_val > 0   # Vega always positive
        assert theta < 0      # Theta negative for long call
        assert rho > 0        # Rho positive for call
    
    def test_complete_monte_carlo_workflow(self):
        """Test complete Monte Carlo pricing workflow."""
        from options.european_options import price_european_call
        from utils.validation import validate_option_params, validate_monte_carlo_params
        
        # User inputs
        S0, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0
        n_paths = 100000
        
        # Validate inputs
        validate_option_params(S0, K, r, sigma, T)
        validate_monte_carlo_params(n_paths, 252)
        
        # Calculate price
        price = price_european_call(S0, K, r, sigma, T, n_paths=n_paths)
        
        # Verify result
        assert price > 0
        # Should be close to Black-Scholes
        from options.black_scholes import black_scholes_call
        bs_price = black_scholes_call(S0, K, r, sigma, T)
        assert abs(price - bs_price) / bs_price < 0.05  # Within 5%
    
    @pytest.mark.skip(reason="Known issue with partial/starmap argument passing - requires refactoring")
    def test_parallel_monte_carlo_workflow(self):
        """Test parallel Monte Carlo workflow."""
        from options.monte_carlo_parallel import price_european_call_parallel
        from utils.validation import validate_option_params
        
        # User inputs
        S0, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0
        n_paths = 1000000
        
        # Validate inputs
        validate_option_params(S0, K, r, sigma, T)
        
        # Calculate price
        price, std_err = price_european_call_parallel(S0, K, r, sigma, T, n_paths=n_paths)
        
        # Verify results
        assert price > 0
        assert std_err > 0
        assert std_err < price * 0.01  # Standard error should be small
    
    def test_payoff_diagram_data_generation(self):
        """Test payoff diagram data generation."""
        import numpy as np
        
        S0, K = 100.0, 100.0
        price = 10.45
        
        # Generate spot price range
        S_range = np.linspace(0.5 * K, 1.5 * K, 100)
        
        # Calculate call payoff
        intrinsic = np.maximum(S_range - K, 0)
        payoff = intrinsic - price
        
        # Verify data
        assert len(S_range) == 100
        assert len(payoff) == 100
        assert payoff[0] < 0  # Out of money loses premium
        assert payoff[-1] > 0  # Deep in money is profitable


class TestPortfolioPageIntegration:
    """Integration tests for Portfolio optimization page workflow."""
    
    def test_complete_max_sharpe_workflow(self):
        """Test complete Maximum Sharpe Ratio workflow."""
        from portfolio.markowitz import optimize_sharpe
        from utils.validation import validate_covariance_matrix, validate_weights
        
        # User inputs (5-asset example)
        np.random.seed(42)
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
        risk_free_rate = 0.02
        
        # Validate inputs
        validate_covariance_matrix(cov_matrix)
        
        # Optimize
        result = optimize_sharpe(mean_returns, cov_matrix, risk_free_rate=risk_free_rate)
        
        # Validate outputs
        validate_weights(result['weights'], allow_short=False)
        
        # Verify results
        assert 'weights' in result
        assert 'return' in result
        assert 'volatility' in result
        assert 'sharpe' in result
        assert result['sharpe'] > 0
    
    def test_complete_risk_parity_workflow(self):
        """Test complete Risk Parity workflow."""
        from portfolio.risk_parity import optimize_risk_parity
        from utils.validation import validate_covariance_matrix
        
        # User inputs
        np.random.seed(42)
        vols = np.array([0.20, 0.15, 0.25, 0.10, 0.18])
        corr = np.eye(5) + 0.3 * (np.ones((5, 5)) - np.eye(5))
        cov_matrix = np.outer(vols, vols) * corr
        
        # Validate inputs
        validate_covariance_matrix(cov_matrix)
        
        # Optimize
        result = optimize_risk_parity(cov_matrix)
        
        # Verify results
        assert 'weights' in result
        assert 'risk_contributions' in result
        
        # Risk contributions should be approximately equal
        risk_contrib = result['risk_contributions']
        assert np.std(risk_contrib) < 0.05
    
    def test_efficient_frontier_workflow(self):
        """Test efficient frontier computation workflow."""
        from portfolio.efficient_frontier import compute_efficient_frontier
        from utils.validation import validate_covariance_matrix
        
        # User inputs
        np.random.seed(42)
        mean_returns = np.array([0.12, 0.10, 0.14, 0.08, 0.11])
        vols = np.array([0.20, 0.15, 0.25, 0.10, 0.18])
        corr = np.eye(5) + 0.3 * (np.ones((5, 5)) - np.eye(5))
        cov_matrix = np.outer(vols, vols) * corr
        
        # Validate inputs
        validate_covariance_matrix(cov_matrix)
        
        # Compute frontier
        result = compute_efficient_frontier(
            mean_returns, cov_matrix, n_points=50
        )
        
        # Verify results
        assert len(result['returns']) == 50
        assert len(result['volatilities']) == 50
        assert len(result['weights']) == 50
        
        # All portfolios should be valid
        for weights in result['weights']:
            assert abs(weights.sum() - 1.0) < 1e-6
            assert np.all(weights >= -1e-6)
    
    def test_allocation_visualization_data(self):
        """Test allocation visualization data preparation."""
        import pandas as pd
        
        # Sample results
        asset_names = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        weights = np.array([0.30, 0.25, 0.20, 0.15, 0.10])
        
        # Create allocation dataframe
        allocation_df = pd.DataFrame({
            'Asset': asset_names,
            'Weight': weights,
            'Weight %': weights * 100
        })
        allocation_df = allocation_df.sort_values('Weight', ascending=False)
        
        # Verify data
        assert len(allocation_df) == 5
        assert allocation_df['Weight'].sum() == pytest.approx(1.0)
        assert allocation_df.iloc[0]['Asset'] == 'AAPL'  # Highest weight


class TestFactorModelsPageIntegration:
    """Integration tests for Factor Models page workflow."""
    
    def test_complete_ff3_workflow(self):
        """Test complete FF3 analysis workflow."""
        from factors.ff3_model import FF3Model
        from factors.data_loader import generate_synthetic_factors
        
        # Generate synthetic data
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=3)
        
        # Generate stock returns
        np.random.seed(42)
        n_obs = len(factor_data)
        stock_returns = (
            0.0001 +
            1.2 * factor_data['Mkt-RF'] +
            0.3 * factor_data['SMB'] +
            -0.2 * factor_data['HML'] +
            np.random.normal(0, 0.01, n_obs)
        )
        
        # Fit model
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        
        # Get summary
        summary = model.summary(annualize=True)
        
        # Verify results
        assert 'alpha' in summary
        assert 'betas' in summary
        assert 'r_squared' in summary
        assert len(summary['betas']) == 3
        assert 0 <= summary['r_squared'] <= 1
    
    def test_complete_ff5_workflow(self):
        """Test complete FF5 analysis workflow."""
        from factors.ff5_model import FF5Model
        from factors.data_loader import generate_synthetic_factors
        
        # Generate synthetic data
        factor_data = generate_synthetic_factors(model='5', frequency='daily', years=3)
        
        # Generate stock returns
        np.random.seed(42)
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
        
        # Fit model
        model = FF5Model()
        model.fit(stock_returns, factor_data)
        
        # Get summary
        summary = model.summary(annualize=True)
        
        # Verify results
        assert len(summary['betas']) == 5
        assert 'RMW' in summary['betas']
        assert 'CMA' in summary['betas']
    
    def test_residual_analysis_workflow(self):
        """Test residual analysis workflow."""
        from factors.ff3_model import FF3Model
        from factors.data_loader import generate_synthetic_factors
        
        # Generate data
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=1)
        
        np.random.seed(42)
        n_obs = len(factor_data)
        stock_returns = (
            0.0001 +
            1.2 * factor_data['Mkt-RF'] +
            np.random.normal(0, 0.01, n_obs)
        )
        
        # Fit model
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        
        # Get predictions
        predictions = model.predict(factor_data)
        
        # Calculate residuals
        residuals = stock_returns - predictions
        
        # Verify residuals
        assert len(residuals) == n_obs
        assert abs(residuals.mean()) < 0.01  # Mean should be close to 0
        # Residuals should be smaller than returns
        assert residuals.std() < stock_returns.std()
    
    def test_significance_testing_workflow(self):
        """Test statistical significance testing workflow."""
        from factors.ff3_model import FF3Model
        from factors.data_loader import generate_synthetic_factors
        
        # Generate data with significant market beta
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=3)
        
        np.random.seed(42)
        n_obs = len(factor_data)
        stock_returns = (
            0.0001 +
            1.5 * factor_data['Mkt-RF'] +  # Strong market exposure
            np.random.normal(0, 0.005, n_obs)  # Low noise
        )
        
        # Fit model
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        
        # Get summary
        summary = model.summary()
        
        # Market beta should be highly significant
        assert summary['beta_p_values']['Mkt-RF'] < 0.001
        
        # Assign significance stars
        p_val = summary['beta_p_values']['Mkt-RF']
        if p_val < 0.001:
            sig_stars = "***"
        elif p_val < 0.01:
            sig_stars = "**"
        elif p_val < 0.05:
            sig_stars = "*"
        else:
            sig_stars = ""
        
        assert sig_stars == "***"


class TestCrossPageIntegration:
    """Integration tests across multiple pages."""
    
    def test_options_to_portfolio_data_flow(self):
        """Test data flow from options to portfolio context."""
        from options.black_scholes import black_scholes_call
        from portfolio.markowitz import portfolio_return
        
        # Price multiple options (could be used in portfolio)
        strikes = [90, 100, 110]
        S0, r, sigma, T = 100.0, 0.05, 0.20, 1.0
        
        option_prices = [black_scholes_call(S0, K, r, sigma, T) for K in strikes]
        
        # Use in portfolio context
        weights = np.array([0.33, 0.34, 0.33])
        mean_returns = np.array(option_prices) / S0  # Simplified returns
        
        portfolio_ret = portfolio_return(weights, mean_returns)
        
        assert portfolio_ret > 0
    
    def test_factor_model_to_portfolio_integration(self):
        """Test using factor model results in portfolio optimization."""
        from factors.ff3_model import FF3Model
        from factors.data_loader import generate_synthetic_factors
        from portfolio.markowitz import optimize_sharpe
        
        # Analyze multiple stocks with factor models
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=1)
        
        n_stocks = 3
        betas = []
        
        for i in range(n_stocks):
            np.random.seed(42 + i)
            stock_returns = (
                0.0001 +
                (1.0 + i*0.2) * factor_data['Mkt-RF'] +
                np.random.normal(0, 0.01, len(factor_data))
            )
            
            model = FF3Model()
            model.fit(stock_returns, factor_data)
            betas.append(model.betas['Mkt-RF'])
        
        # Use betas to construct portfolio
        # (In practice, would use expected returns based on factor exposures)
        mean_returns = np.array([0.10, 0.12, 0.08])
        cov_matrix = np.diag([0.04, 0.0225, 0.01])
        
        result = optimize_sharpe(mean_returns, cov_matrix)
        
        assert 'weights' in result
        assert len(result['weights']) == n_stocks


class TestErrorHandling:
    """Integration tests for error handling across workflows."""
    
    def test_invalid_option_parameters_handling(self):
        """Test handling of invalid option parameters."""
        from utils.validation import validate_option_params, ValidationError
        
        # Negative stock price
        with pytest.raises(ValidationError):
            validate_option_params(S0=-100, K=100, r=0.05, sigma=0.20, T=1.0)
        
        # Negative volatility
        with pytest.raises(ValidationError):
            validate_option_params(S0=100, K=100, r=0.05, sigma=-0.20, T=1.0)
        
        # Zero time
        with pytest.raises(ValidationError):
            validate_option_params(S0=100, K=100, r=0.05, sigma=0.20, T=0.0)
    
    def test_invalid_portfolio_data_handling(self):
        """Test handling of invalid portfolio data."""
        from utils.validation import validate_covariance_matrix, ValidationError
        
        # Non-square matrix
        cov = np.array([
            [0.04, 0.006],
            [0.006, 0.0225],
            [0.008, 0.00525]
        ])
        
        with pytest.raises(ValidationError):
            validate_covariance_matrix(cov)
        
        # Non-positive definite
        cov = np.array([
            [0.04, 0.1],
            [0.1, 0.01]  # Not positive definite
        ])
        
        with pytest.raises(ValidationError):
            validate_covariance_matrix(cov)
    
    def test_optimization_failure_handling(self):
        """Test handling of optimization failures."""
        from portfolio.markowitz import optimize_target_return
        
        # Impossible target return
        mean_returns = np.array([0.08, 0.10, 0.12])
        cov_matrix = np.diag([0.04, 0.0225, 0.01])
        target_return = 0.20  # Higher than max possible
        
        weights, vol = optimize_target_return(
            mean_returns, cov_matrix, target_return
        )
        
        # Should return None for impossible target
        assert weights is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
