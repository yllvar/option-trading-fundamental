"""
Performance-optimized Monte Carlo simulation with parallel processing.
Uses multiprocessing for significant speedup on multi-core systems.
"""

import numpy as np
from multiprocessing import Pool, cpu_count
from functools import partial
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import get_default_logger, PerformanceLogger
from utils.validation import validate_option_params, validate_monte_carlo_params

logger = get_default_logger(__name__)


def _simulate_batch(batch_size: int, S0: float, r: float, sigma: float, T: float, K: float, option_type: str, seed: int = None) -> tuple:
    """
    Simulate a batch of option prices (worker function for parallel processing).
    
    Parameters:
    -----------
    batch_size : int
        Number of paths in this batch
    S0, r, sigma, T, K : float
        Option parameters
    option_type : str
        'call' or 'put'
    seed : int, optional
        Random seed for reproducibility
    
    Returns:
    --------
    tuple : (sum of payoffs, sum of squared payoffs, count)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Simulate terminal prices
    Z = np.random.standard_normal(batch_size)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    
    # Calculate payoffs
    if option_type == 'call':
        payoffs = np.maximum(ST - K, 0)
    else:  # put
        payoffs = np.maximum(K - ST, 0)
    
    # Discount to present value
    discounted_payoffs = np.exp(-r * T) * payoffs
    
    return (
        np.sum(discounted_payoffs),
        np.sum(discounted_payoffs ** 2),
        batch_size
    )


def price_european_call_parallel(
    S0: float,
    K: float,
    r: float,
    sigma: float,
    T: float,
    n_paths: int = 100000,
    n_workers: int = None
) -> tuple:
    """
    Price European call option using parallel Monte Carlo simulation.
    
    Parameters:
    -----------
    S0 : float
        Current stock price
    K : float
        Strike price
    r : float
        Risk-free rate (annualized)
    sigma : float
        Volatility (annualized)
    T : float
        Time to maturity (years)
    n_paths : int
        Total number of simulation paths
    n_workers : int, optional
        Number of parallel workers (default: CPU count)
    
    Returns:
    --------
    tuple : (price, standard_error)
    
    Raises:
    -------
    ValidationError : If parameters are invalid
    """
    # Validate inputs
    validate_option_params(S0, K, r, sigma, T)
    validate_monte_carlo_params(n_paths, 252)  # Use 252 as dummy n_steps
    
    logger.info(f"Pricing call option: S0={S0}, K={K}, r={r}, sigma={sigma}, T={T}, n_paths={n_paths}")
    
    with PerformanceLogger(logger, f"Parallel MC call pricing ({n_paths} paths)"):
        # Determine number of workers
        if n_workers is None:
            n_workers = min(cpu_count(), 8)  # Cap at 8 to avoid overhead
        
        # Split work into batches
        batch_size = n_paths // n_workers
        batches = [batch_size] * n_workers
        # Handle remainder
        batches[-1] += n_paths - sum(batches)
        
        # Create worker function with fixed parameters
        worker = partial(
            _simulate_batch,
            S0=S0, r=r, sigma=sigma, T=T, K=K, option_type='call'
        )
        
        # Run parallel simulation
        with Pool(processes=n_workers) as pool:
            # Use different seeds for each batch
            results = pool.starmap(
                worker,
                [(batch, i * 12345) for i, batch in enumerate(batches)]
            )
        
        # Aggregate results
        total_sum = sum(r[0] for r in results)
        total_sum_sq = sum(r[1] for r in results)
        total_count = sum(r[2] for r in results)
        
        # Calculate price and standard error
        price = total_sum / total_count
        variance = (total_sum_sq / total_count) - (price ** 2)
        std_error = np.sqrt(variance / total_count)
        
        logger.info(f"Call price: ${price:.4f} ± ${std_error:.4f}")
        
        return price, std_error


def price_european_put_parallel(
    S0: float,
    K: float,
    r: float,
    sigma: float,
    T: float,
    n_paths: int = 100000,
    n_workers: int = None
) -> tuple:
    """
    Price European put option using parallel Monte Carlo simulation.
    
    Parameters:
    -----------
    S0 : float
        Current stock price
    K : float
        Strike price
    r : float
        Risk-free rate (annualized)
    sigma : float
        Volatility (annualized)
    T : float
        Time to maturity (years)
    n_paths : int
        Total number of simulation paths
    n_workers : int, optional
        Number of parallel workers (default: CPU count)
    
    Returns:
    --------
    tuple : (price, standard_error)
    
    Raises:
    -------
    ValidationError : If parameters are invalid
    """
    # Validate inputs
    validate_option_params(S0, K, r, sigma, T)
    validate_monte_carlo_params(n_paths, 252)
    
    logger.info(f"Pricing put option: S0={S0}, K={K}, r={r}, sigma={sigma}, T={T}, n_paths={n_paths}")
    
    with PerformanceLogger(logger, f"Parallel MC put pricing ({n_paths} paths)"):
        # Determine number of workers
        if n_workers is None:
            n_workers = min(cpu_count(), 8)
        
        # Split work into batches
        batch_size = n_paths // n_workers
        batches = [batch_size] * n_workers
        batches[-1] += n_paths - sum(batches)
        
        # Create worker function
        worker = partial(
            _simulate_batch,
            S0=S0, r=r, sigma=sigma, T=T, K=K, option_type='put'
        )
        
        # Run parallel simulation
        with Pool(processes=n_workers) as pool:
            results = pool.starmap(
                worker,
                [(batch, i * 12345) for i, batch in enumerate(batches)]
            )
        
        # Aggregate results
        total_sum = sum(r[0] for r in results)
        total_sum_sq = sum(r[1] for r in results)
        total_count = sum(r[2] for r in results)
        
        # Calculate price and standard error
        price = total_sum / total_count
        variance = (total_sum_sq / total_count) - (price ** 2)
        std_error = np.sqrt(variance / total_count)
        
        logger.info(f"Put price: ${price:.4f} ± ${std_error:.4f}")
        
        return price, std_error


def compare_performance():
    """Compare serial vs parallel Monte Carlo performance."""
    from options.european_options import price_european_call
    from options.black_scholes import black_scholes_call
    import time
    
    print("=" * 60)
    print("Monte Carlo Performance Comparison")
    print("=" * 60)
    
    # Parameters
    S0, K, r, sigma, T = 100, 100, 0.05, 0.20, 1.0
    n_paths = 1_000_000
    
    # Black-Scholes (reference)
    bs_price = black_scholes_call(S0, K, r, sigma, T)
    print(f"\nBlack-Scholes price: ${bs_price:.4f}")
    
    # Serial Monte Carlo
    print(f"\nSerial Monte Carlo ({n_paths:,} paths)...")
    start = time.time()
    serial_price = price_european_call(S0, K, r, sigma, T, n_paths=n_paths)
    serial_time = time.time() - start
    serial_error = abs(serial_price - bs_price)
    print(f"  Price: ${serial_price:.4f}")
    print(f"  Error: ${serial_error:.4f}")
    print(f"  Time: {serial_time:.2f}s")
    
    # Parallel Monte Carlo
    print(f"\nParallel Monte Carlo ({n_paths:,} paths, {cpu_count()} cores)...")
    start = time.time()
    parallel_price, std_err = price_european_call_parallel(
        S0, K, r, sigma, T, n_paths=n_paths
    )
    parallel_time = time.time() - start
    parallel_error = abs(parallel_price - bs_price)
    print(f"  Price: ${parallel_price:.4f} ± ${std_err:.4f}")
    print(f"  Error: ${parallel_error:.4f}")
    print(f"  Time: {parallel_time:.2f}s")
    
    # Speedup
    speedup = serial_time / parallel_time
    print(f"\n{'='*60}")
    print(f"Speedup: {speedup:.2f}x")
    print(f"Efficiency: {speedup/cpu_count()*100:.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Run performance comparison
    compare_performance()
    
    # Test validation
    print("\n\nTesting input validation...")
    try:
        price_european_call_parallel(-100, 100, 0.05, 0.20, 1.0)
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"✓ Caught expected error: {e}")
    
    print("\nAll tests passed!")
