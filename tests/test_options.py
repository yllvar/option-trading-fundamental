"""
Unit tests for options pricing module.
Tests Black-Scholes, Monte Carlo, Greeks, and variance reduction.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from options.black_scholes import black_scholes_call, black_scholes_put
from options.european_options import price_european_call, price_european_put
from options.gbm import simulate_gbm
from options.greeks import (
    delta_call, delta_put, gamma, vega, 
    theta_call, theta_put, rho_call, rho_put
)


class TestBlackScholes:
    """Test Black-Scholes analytical pricing."""
    
    def test_atm_call_price(self):
        """Test at-the-money call option pricing."""
        price = black_scholes_call(S0=100, K=100, r=0.05, sigma=0.20, T=1.0)
        # Expected price around $10.45 for these parameters
        assert 10.0 < price < 11.0, f"ATM call price {price} outside expected range"
    
    def test_atm_put_price(self):
        """Test at-the-money put option pricing."""
        price = black_scholes_put(S0=100, K=100, r=0.05, sigma=0.20, T=1.0)
        # Expected price around $5.57 for these parameters
        assert 5.0 < price < 6.5, f"ATM put price {price} outside expected range"
    
    def test_put_call_parity(self):
        """Test put-call parity: C - P = S - K*exp(-rT)."""
        S0, K, r, sigma, T = 100, 100, 0.05, 0.20, 1.0
        
        call = black_scholes_call(S0, K, r, sigma, T)
        put = black_scholes_put(S0, K, r, sigma, T)
        
        lhs = call - put
        rhs = S0 - K * np.exp(-r * T)
        
        assert abs(lhs - rhs) < 1e-10, f"Put-call parity violated: {lhs} != {rhs}"
    
    def test_deep_itm_call(self):
        """Test deep in-the-money call behaves like stock."""
        # Deep ITM call should be worth approximately S - K*exp(-rT)
        S0, K, r, sigma, T = 150, 100, 0.05, 0.20, 1.0
        
        call = black_scholes_call(S0, K, r, sigma, T)
        intrinsic = S0 - K * np.exp(-r * T)
        
        # Call should be close to intrinsic value
        assert call > intrinsic, "Deep ITM call should exceed intrinsic value"
        assert call < intrinsic + 5, "Deep ITM call should be close to intrinsic"
    
    def test_deep_otm_call(self):
        """Test deep out-of-the-money call has low value."""
        S0, K, r, sigma, T = 100, 150, 0.05, 0.20, 1.0
        
        call = black_scholes_call(S0, K, r, sigma, T)
        
        assert call < 2.0, f"Deep OTM call {call} should be near zero"
        assert call > 0, "Call price must be positive"
    
    def test_zero_volatility(self):
        """Test option pricing with zero volatility."""
        S0, K, r, T = 100, 100, 0.05, 1.0
        sigma = 1e-10  # Near zero
        
        call = black_scholes_call(S0, K, r, sigma, T)
        # With zero vol, ATM call worth S - K*exp(-rT)
        expected = max(S0 - K * np.exp(-r * T), 0)
        
        assert abs(call - expected) < 0.1, "Zero vol pricing incorrect"


class TestMonteCarlo:
    """Test Monte Carlo option pricing."""
    
    def test_mc_converges_to_bs(self):
        """Test Monte Carlo converges to Black-Scholes."""
        S0, K, r, sigma, T = 100, 100, 0.05, 0.20, 1.0
        
        bs_price = black_scholes_call(S0, K, r, sigma, T)
        mc_price = price_european_call(S0, K, r, sigma, T, n_paths=100000)
        
        # MC should be within 2% of BS with 100k paths
        error = abs(mc_price - bs_price) / bs_price
        assert error < 0.02, f"MC error {error*100:.2f}% too high"
    
    def test_mc_put_call_parity(self):
        """Test put-call parity holds for Monte Carlo."""
        S0, K, r, sigma, T = 100, 100, 0.05, 0.20, 1.0
        
        call = price_european_call(S0, K, r, sigma, T, n_paths=50000)
        put = price_european_put(S0, K, r, sigma, T, n_paths=50000)
        
        lhs = call - put
        rhs = S0 - K * np.exp(-r * T)
        
        # Allow 5% error for MC
        error = abs(lhs - rhs) / abs(rhs)
        assert error < 0.05, f"MC put-call parity error {error*100:.2f}%"
    
    def test_mc_positive_prices(self):
        """Test Monte Carlo always returns positive prices."""
        prices = []
        for K in [80, 100, 120]:
            call = price_european_call(100, K, 0.05, 0.20, 1.0, n_paths=10000)
            put = price_european_put(100, K, 0.05, 0.20, 1.0, n_paths=10000)
            prices.extend([call, put])
        
        assert all(p > 0 for p in prices), "All option prices must be positive"


class TestGBM:
    """Test Geometric Brownian Motion simulation."""
    
    def test_gbm_initial_price(self):
        """Test GBM starts at correct initial price."""
        S0 = 100
        t, S = simulate_gbm(S0, mu=0.05, sigma=0.20, T=1.0, dt=1/252, n_paths=100)
        
        # All paths should start at S0
        assert np.allclose(S[:, 0], S0), "GBM doesn't start at S0"
    
    def test_gbm_mean_drift(self):
        """Test GBM has correct expected drift."""
        S0, mu, sigma, T = 100, 0.08, 0.20, 1.0
        t, S = simulate_gbm(S0, mu, sigma, T, dt=1/252, n_paths=10000)
        
        # Expected terminal value: S0 * exp(mu * T)
        expected = S0 * np.exp(mu * T)
        actual = np.mean(S[:, -1])
        
        # Should be within 5% with 10k paths
        error = abs(actual - expected) / expected
        assert error < 0.05, f"GBM mean drift error {error*100:.2f}%"
    
    def test_gbm_positive_prices(self):
        """Test GBM never produces negative prices."""
        t, S = simulate_gbm(100, 0.05, 0.30, 1.0, 1/252, 1000)
        
        assert np.all(S > 0), "GBM produced negative prices"


class TestGreeks:
    """Test option Greeks calculations."""
    
    def test_delta_range(self):
        """Test delta is in valid range."""
        S, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20
        
        delta_c = delta_call(S, K, T, r, sigma)
        delta_p = delta_put(S, K, T, r, sigma)
        
        assert 0 <= delta_c <= 1, f"Call delta {delta_c} out of range [0,1]"
        assert -1 <= delta_p <= 0, f"Put delta {delta_p} out of range [-1,0]"
    
    def test_delta_put_call_relation(self):
        """Test delta_put = delta_call - 1."""
        S, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20
        
        delta_c = delta_call(S, K, T, r, sigma)
        delta_p = delta_put(S, K, T, r, sigma)
        
        assert abs(delta_p - (delta_c - 1)) < 1e-10, "Delta relation violated"
    
    def test_gamma_positive(self):
        """Test gamma is always positive."""
        test_cases = [
            (80, 100, 0.25, 0.05, 0.20),   # OTM
            (100, 100, 0.25, 0.05, 0.20),  # ATM
            (120, 100, 0.25, 0.05, 0.20),  # ITM
        ]
        
        for S, K, T, r, sigma in test_cases:
            g = gamma(S, K, T, r, sigma)
            assert g > 0, f"Gamma {g} should be positive for S={S}"
    
    def test_gamma_peaks_at_atm(self):
        """Test gamma is highest at-the-money."""
        K, T, r, sigma = 100, 0.25, 0.05, 0.20
        
        gamma_otm = gamma(80, K, T, r, sigma)
        gamma_atm = gamma(100, K, T, r, sigma)
        gamma_itm = gamma(120, K, T, r, sigma)
        
        assert gamma_atm > gamma_otm, "ATM gamma should exceed OTM"
        assert gamma_atm > gamma_itm, "ATM gamma should exceed ITM"
    
    def test_vega_positive(self):
        """Test vega is always positive."""
        S, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20
        
        v = vega(S, K, T, r, sigma)
        assert v > 0, "Vega must be positive"
    
    def test_theta_call_negative(self):
        """Test theta is typically negative for calls."""
        # For most calls, theta is negative (time decay)
        S, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20
        
        theta = theta_call(S, K, T, r, sigma)
        assert theta < 0, "ATM call theta should be negative"
    
    def test_rho_call_positive(self):
        """Test rho is positive for calls."""
        S, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20
        
        rho = rho_call(S, K, T, r, sigma)
        assert rho > 0, "Call rho should be positive"
    
    def test_rho_put_negative(self):
        """Test rho is negative for puts."""
        S, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20
        
        rho = rho_put(S, K, T, r, sigma)
        assert rho < 0, "Put rho should be negative"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_time_to_maturity(self):
        """Test option value at expiration."""
        S0, K, r, sigma = 110, 100, 0.05, 0.20
        T = 1e-10  # Near zero
        
        call = black_scholes_call(S0, K, r, sigma, T)
        intrinsic = max(S0 - K, 0)
        
        assert abs(call - intrinsic) < 0.01, "At expiry, call = intrinsic value"
    
    def test_very_high_volatility(self):
        """Test pricing with very high volatility."""
        S0, K, r, T = 100, 100, 0.05, 1.0
        sigma = 2.0  # 200% volatility
        
        call = black_scholes_call(S0, K, r, sigma, T)
        
        # High vol call should be valuable
        assert call > 20, "High vol call should be expensive"
        assert call < S0, "Call can't exceed stock price"
    
    def test_very_long_maturity(self):
        """Test pricing with long time to maturity."""
        S0, K, r, sigma = 100, 100, 0.05, 0.20
        T = 10.0  # 10 years
        
        call = black_scholes_call(S0, K, r, sigma, T)
        
        # Long-dated call should be valuable
        assert call > 30, "Long-dated call should be expensive"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
