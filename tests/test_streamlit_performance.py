"""
Performance tests for Streamlit app.
Tests execution time and resource usage of key operations.
"""

import pytest
import sys
from pathlib import Path
import numpy as np
import time
from functools import wraps

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def measure_time(func):
    """Decorator to measure execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        execution_time = end - start
        return result, execution_time
    return wrapper


class TestOptionsPerformance:
    """Performance tests for Options pricing operations."""
    
    def test_black_scholes_performance(self):
        """Test Black-Scholes calculation performance."""
        from options.black_scholes import black_scholes_call
        
        S0, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0
        
        start = time.time()
        for _ in range(1000):
            price = black_scholes_call(S0, K, r, sigma, T)
        end = time.time()
        
        avg_time = (end - start) / 1000
        
        # Should be very fast (< 1ms per calculation)
        assert avg_time < 0.001
        print(f"\nBlack-Scholes avg time: {avg_time*1000:.4f}ms")
    
    def test_greeks_calculation_performance(self):
        """Test Greeks calculation performance."""
        from options.greeks import delta_call, gamma, vega, theta_call, rho_call
        
        S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        
        start = time.time()
        for _ in range(1000):
            delta = delta_call(S0, K, T, r, sigma)
            gamma_val = gamma(S0, K, T, r, sigma)
            vega_val = vega(S0, K, T, r, sigma)
            theta = theta_call(S0, K, T, r, sigma)
            rho = rho_call(S0, K, T, r, sigma)
        end = time.time()
        
        avg_time = (end - start) / 1000
        
        # All Greeks should be calculated quickly (< 5ms total)
        assert avg_time < 0.005
        print(f"\nGreeks calculation avg time: {avg_time*1000:.4f}ms")
    
    def test_monte_carlo_performance(self):
        """Test Monte Carlo simulation performance."""
        from options.european_options import price_european_call
        
        S0, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0
        n_paths = 100000
        
        start = time.time()
        price = price_european_call(S0, K, r, sigma, T, n_paths=n_paths)
        end = time.time()
        
        execution_time = end - start
        
        # Should complete in reasonable time (< 2 seconds for 100k paths)
        assert execution_time < 2.0
        print(f"\nMonte Carlo (100k paths) time: {execution_time:.4f}s")
    
    def test_parallel_monte_carlo_performance(self):
        """Test parallel Monte Carlo performance and speedup."""
        from options.european_options import price_european_call
        from options.monte_carlo_parallel import price_european_call_parallel
        
        S0, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0
        n_paths = 1000000
        
        # Serial Monte Carlo
        start = time.time()
        price_serial = price_european_call(S0, K, r, sigma, T, n_paths=n_paths)
        serial_time = time.time() - start
        
        # Parallel Monte Carlo
        start = time.time()
        price_parallel, std_err = price_european_call_parallel(
            S0, K, r, sigma, T, n_paths=n_paths
        )
        parallel_time = time.time() - start
        
        speedup = serial_time / parallel_time
        
        # Parallel should be faster
        assert parallel_time < serial_time
        # Should achieve reasonable speedup (> 1.5x)
        assert speedup > 1.5
        
        print(f"\nSerial MC time: {serial_time:.4f}s")
        print(f"Parallel MC time: {parallel_time:.4f}s")
        print(f"Speedup: {speedup:.2f}x")
    
    @pytest.mark.slow
    def test_payoff_diagram_generation_performance(self):
        """Test payoff diagram data generation performance."""
        import numpy as np
        
        K = 100.0
        price = 10.45
        
        start = time.time()
        for _ in range(100):
            S_range = np.linspace(0.5 * K, 1.5 * K, 100)
            intrinsic = np.maximum(S_range - K, 0)
            payoff = intrinsic - price
        end = time.time()
        
        avg_time = (end - start) / 100
        
        # Should be very fast (< 1ms)
        assert avg_time < 0.001
        print(f"\nPayoff diagram generation avg time: {avg_time*1000:.4f}ms")


class TestPortfolioPerformance:
    """Performance tests for Portfolio optimization operations."""
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """Generate sample portfolio data."""
        np.random.seed(42)
        n_assets = 5
        mean_returns = np.array([0.12, 0.10, 0.14, 0.08, 0.11])
        vols = np.array([0.20, 0.15, 0.25, 0.10, 0.18])
        corr = np.eye(n_assets) + 0.3 * (np.ones((n_assets, n_assets)) - np.eye(n_assets))
        cov_matrix = np.outer(vols, vols) * corr
        return mean_returns, cov_matrix
    
    def test_max_sharpe_optimization_performance(self, sample_portfolio_data):
        """Test Maximum Sharpe Ratio optimization performance."""
        from portfolio.markowitz import optimize_sharpe
        
        mean_returns, cov_matrix = sample_portfolio_data
        
        start = time.time()
        result = optimize_sharpe(mean_returns, cov_matrix, risk_free_rate=0.02)
        end = time.time()
        
        execution_time = end - start
        
        # Should be fast (< 0.5 seconds for 5 assets)
        assert execution_time < 0.5
        print(f"\nMax Sharpe optimization time: {execution_time:.4f}s")
    
    def test_min_variance_optimization_performance(self, sample_portfolio_data):
        """Test Minimum Variance optimization performance."""
        from portfolio.markowitz import optimize_min_variance
        
        mean_returns, cov_matrix = sample_portfolio_data
        
        start = time.time()
        result = optimize_min_variance(mean_returns, cov_matrix)
        end = time.time()
        
        execution_time = end - start
        
        # Should be fast (< 0.5 seconds)
        assert execution_time < 0.5
        print(f"\nMin Variance optimization time: {execution_time:.4f}s")
    
    def test_risk_parity_optimization_performance(self, sample_portfolio_data):
        """Test Risk Parity optimization performance."""
        from portfolio.risk_parity import optimize_risk_parity
        
        _, cov_matrix = sample_portfolio_data
        
        start = time.time()
        result = optimize_risk_parity(cov_matrix)
        end = time.time()
        
        execution_time = end - start
        
        # Should be reasonably fast (< 1 second for 5 assets)
        assert execution_time < 1.0
        print(f"\nRisk Parity optimization time: {execution_time:.4f}s")
    
    def test_efficient_frontier_performance(self, sample_portfolio_data):
        """Test efficient frontier computation performance."""
        from portfolio.efficient_frontier import compute_efficient_frontier
        
        mean_returns, cov_matrix = sample_portfolio_data
        
        start = time.time()
        result = compute_efficient_frontier(
            mean_returns, cov_matrix, n_points=50
        )
        end = time.time()
        
        execution_time = end - start
        
        # Should complete in reasonable time (< 5 seconds for 50 portfolios)
        assert execution_time < 5.0
        print(f"\nEfficient frontier (50 portfolios) time: {execution_time:.4f}s")
    
    def test_large_portfolio_performance(self):
        """Test optimization performance with larger portfolio."""
        from portfolio.markowitz import optimize_sharpe
        
        # 20-asset portfolio
        np.random.seed(42)
        n_assets = 20
        mean_returns = np.random.uniform(0.05, 0.15, n_assets)
        vols = np.random.uniform(0.10, 0.30, n_assets)
        corr = np.eye(n_assets) + 0.2 * (np.ones((n_assets, n_assets)) - np.eye(n_assets))
        cov_matrix = np.outer(vols, vols) * corr
        
        start = time.time()
        result = optimize_sharpe(mean_returns, cov_matrix)
        end = time.time()
        
        execution_time = end - start
        
        # Should still be reasonable (< 2 seconds for 20 assets)
        assert execution_time < 2.0
        print(f"\nLarge portfolio (20 assets) optimization time: {execution_time:.4f}s")


class TestFactorModelsPerformance:
    """Performance tests for Factor Models operations."""
    
    def test_ff3_model_fitting_performance(self):
        """Test FF3 model fitting performance."""
        from factors.ff3_model import FF3Model
        from factors.data_loader import generate_synthetic_factors
        
        # 3 years of daily data
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=3)
        
        np.random.seed(42)
        n_obs = len(factor_data)
        stock_returns = (
            0.0001 +
            1.2 * factor_data['Mkt-RF'] +
            0.3 * factor_data['SMB'] +
            -0.2 * factor_data['HML'] +
            np.random.normal(0, 0.01, n_obs)
        )
        
        start = time.time()
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        summary = model.summary(annualize=True)
        end = time.time()
        
        execution_time = end - start
        
        # Should be fast (< 0.5 seconds)
        assert execution_time < 0.5
        print(f"\nFF3 model fitting time: {execution_time:.4f}s")
    
    def test_ff5_model_fitting_performance(self):
        """Test FF5 model fitting performance."""
        from factors.ff5_model import FF5Model
        from factors.data_loader import generate_synthetic_factors
        
        # 3 years of daily data
        factor_data = generate_synthetic_factors(model='5', frequency='daily', years=3)
        
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
        
        start = time.time()
        model = FF5Model()
        model.fit(stock_returns, factor_data)
        summary = model.summary(annualize=True)
        end = time.time()
        
        execution_time = end - start
        
        # Should be fast (< 0.5 seconds)
        assert execution_time < 0.5
        print(f"\nFF5 model fitting time: {execution_time:.4f}s")
    
    def test_synthetic_data_generation_performance(self):
        """Test synthetic data generation performance."""
        from factors.data_loader import generate_synthetic_factors
        
        start = time.time()
        for _ in range(10):
            factor_data = generate_synthetic_factors(model='5', frequency='daily', years=5)
        end = time.time()
        
        avg_time = (end - start) / 10
        
        # Should be very fast (< 0.1 seconds per generation)
        assert avg_time < 0.1
        print(f"\nSynthetic data generation avg time: {avg_time:.4f}s")
    
    def test_prediction_performance(self):
        """Test model prediction performance."""
        from factors.ff3_model import FF3Model
        from factors.data_loader import generate_synthetic_factors
        
        # Fit model
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=1)
        
        np.random.seed(42)
        stock_returns = (
            0.0001 +
            1.2 * factor_data['Mkt-RF'] +
            np.random.normal(0, 0.01, len(factor_data))
        )
        
        model = FF3Model()
        model.fit(stock_returns, factor_data)
        
        # Test prediction performance
        start = time.time()
        for _ in range(100):
            predictions = model.predict(factor_data)
        end = time.time()
        
        avg_time = (end - start) / 100
        
        # Should be very fast (< 10ms)
        assert avg_time < 0.01
        print(f"\nModel prediction avg time: {avg_time*1000:.4f}ms")


class TestMemoryUsage:
    """Tests for memory efficiency."""
    
    def test_large_monte_carlo_memory(self):
        """Test memory usage of large Monte Carlo simulation."""
        from options.monte_carlo_parallel import price_european_call_parallel
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure memory before
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run large simulation
        S0, K, r, sigma, T = 100.0, 100.0, 0.05, 0.20, 1.0
        price, std_err = price_european_call_parallel(
            S0, K, r, sigma, T, n_paths=5_000_000
        )
        
        # Measure memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        mem_used = mem_after - mem_before
        
        # Should not use excessive memory (< 500MB for 5M paths)
        assert mem_used < 500
        print(f"\nMemory used for 5M paths: {mem_used:.2f}MB")
    
    def test_efficient_frontier_memory(self):
        """Test memory usage of efficient frontier computation."""
        from portfolio.efficient_frontier import compute_efficient_frontier
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure memory before
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate large portfolio
        np.random.seed(42)
        n_assets = 50
        mean_returns = np.random.uniform(0.05, 0.15, n_assets)
        vols = np.random.uniform(0.10, 0.30, n_assets)
        corr = np.eye(n_assets) + 0.2 * (np.ones((n_assets, n_assets)) - np.eye(n_assets))
        cov_matrix = np.outer(vols, vols) * corr
        
        # Compute frontier
        result = compute_efficient_frontier(
            mean_returns, cov_matrix, n_points=100
        )
        
        # Measure memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        mem_used = mem_after - mem_before
        
        # Should not use excessive memory (< 100MB)
        assert mem_used < 100
        print(f"\nMemory used for efficient frontier (50 assets, 100 portfolios): {mem_used:.2f}MB")


class TestConcurrentOperations:
    """Tests for concurrent operations performance."""
    
    def test_multiple_optimizations_concurrently(self):
        """Test running multiple optimizations."""
        from portfolio.markowitz import optimize_sharpe
        
        np.random.seed(42)
        n_portfolios = 10
        
        start = time.time()
        for i in range(n_portfolios):
            mean_returns = np.random.uniform(0.05, 0.15, 5)
            vols = np.random.uniform(0.10, 0.30, 5)
            corr = np.eye(5) + 0.3 * (np.ones((5, 5)) - np.eye(5))
            cov_matrix = np.outer(vols, vols) * corr
            
            result = optimize_sharpe(mean_returns, cov_matrix)
        end = time.time()
        
        total_time = end - start
        avg_time = total_time / n_portfolios
        
        # Should handle multiple optimizations efficiently
        assert avg_time < 0.5
        print(f"\nAverage time per optimization (10 portfolios): {avg_time:.4f}s")
    
    def test_multiple_factor_analyses_concurrently(self):
        """Test running multiple factor analyses."""
        from factors.ff3_model import FF3Model
        from factors.data_loader import generate_synthetic_factors
        
        factor_data = generate_synthetic_factors(model='3', frequency='daily', years=1)
        
        n_stocks = 10
        
        start = time.time()
        for i in range(n_stocks):
            np.random.seed(42 + i)
            stock_returns = (
                0.0001 +
                (1.0 + i*0.1) * factor_data['Mkt-RF'] +
                np.random.normal(0, 0.01, len(factor_data))
            )
            
            model = FF3Model()
            model.fit(stock_returns, factor_data)
            summary = model.summary()
        end = time.time()
        
        total_time = end - start
        avg_time = total_time / n_stocks
        
        # Should handle multiple analyses efficiently
        assert avg_time < 0.5
        print(f"\nAverage time per factor analysis (10 stocks): {avg_time:.4f}s")


# Performance benchmarks summary
def print_performance_summary():
    """Print performance benchmarks summary."""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARKS SUMMARY")
    print("="*60)
    print("\nOptions Pricing:")
    print("  Black-Scholes:           < 1ms")
    print("  Greeks (all 5):          < 5ms")
    print("  Monte Carlo (100k):      < 2s")
    print("  Parallel MC (1M):        < 1s (3x speedup)")
    print("\nPortfolio Optimization:")
    print("  Max Sharpe (5 assets):   < 0.5s")
    print("  Min Variance (5 assets): < 0.5s")
    print("  Risk Parity (5 assets):  < 1s")
    print("  Efficient Frontier (50): < 5s")
    print("  Large Portfolio (20):    < 2s")
    print("\nFactor Models:")
    print("  FF3 Fitting (3 years):   < 0.5s")
    print("  FF5 Fitting (3 years):   < 0.5s")
    print("  Synthetic Data Gen:      < 0.1s")
    print("  Model Prediction:        < 10ms")
    print("\nMemory Usage:")
    print("  Monte Carlo (5M paths):  < 500MB")
    print("  Efficient Frontier:      < 100MB")
    print("="*60)


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
    
    # Print summary
    print_performance_summary()
