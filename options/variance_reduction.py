"""
Variance reduction techniques for Monte Carlo option pricing.
Demonstrates antithetic variates and control variates.
"""

import numpy as np
from gbm import simulate_gbm
from european_options import price_european_call as monte_carlo_call
from european_options import price_european_put as monte_carlo_put
from black_scholes import black_scholes_call


def antithetic_variates_call(S0, K, T, r, sigma, n_paths=100000):
    """
    Price a call option using antithetic variates variance reduction.
    
    For each random path Z, we also compute the path with -Z.
    This reduces variance because the errors are negatively correlated.
    
    Returns: (price, std_error, variance_reduction_ratio)
    """
    np.random.seed(42)
    
    # Generate standard normal samples
    Z = np.random.standard_normal(n_paths // 2)
    
    # Simulate terminal prices with Z and -Z
    ST_pos = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    ST_neg = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * (-Z))
    
    # Payoffs
    payoff_pos = np.maximum(ST_pos - K, 0)
    payoff_neg = np.maximum(ST_neg - K, 0)
    
    # Antithetic estimator: average of both
    payoff_avg = 0.5 * (payoff_pos + payoff_neg)
    
    # Discounted expectation
    price = np.exp(-r * T) * np.mean(payoff_avg)
    std_error = np.exp(-r * T) * np.std(payoff_avg) / np.sqrt(len(payoff_avg))
    
    # Compare to standard MC variance
    np.random.seed(42)
    _, std_mc = monte_carlo_call(S0, K, T, r, sigma, n_paths)
    variance_reduction = (std_mc / std_error) ** 2
    
    return price, std_error, variance_reduction


def control_variates_call(S0, K, T, r, sigma, n_paths=100000):
    """
    Price a call option using control variates variance reduction.
    
    Uses the underlying asset as a control variate since we know
    E[S_T] = S_0 * exp(rT) exactly.
    
    Returns: (price, std_error, variance_reduction_ratio)
    """
    np.random.seed(42)
    
    # Generate terminal prices
    Z = np.random.standard_normal(n_paths)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    
    # Payoff and control variate
    payoff = np.maximum(ST - K, 0)
    control = ST  # The underlying at maturity
    
    # Known expectation of control
    E_control = S0 * np.exp(r * T)
    
    # Optimal coefficient (minimize variance)
    cov_pc = np.cov(payoff, control)[0, 1]
    var_c = np.var(control)
    beta = cov_pc / var_c
    
    # Adjusted payoff
    payoff_adjusted = payoff - beta * (control - E_control)
    
    # Discounted expectation
    price = np.exp(-r * T) * np.mean(payoff_adjusted)
    std_error = np.exp(-r * T) * np.std(payoff_adjusted) / np.sqrt(n_paths)
    
    # Compare to standard MC
    np.random.seed(42)
    _, std_mc = monte_carlo_call(S0, K, T, r, sigma, n_paths)
    variance_reduction = (std_mc / std_error) ** 2
    
    return price, std_error, variance_reduction


def importance_sampling_call(S0, K, T, r, sigma, n_paths=100000, shift=0.5):
    """
    Price a deep OTM call using importance sampling.
    
    Shifts the drift to make the payoff region more likely to be sampled,
    then corrects with likelihood ratio.
    
    Best for deep out-of-the-money options where standard MC is inefficient.
    """
    np.random.seed(42)
    
    # Original drift and shifted drift
    mu = r - 0.5 * sigma**2
    mu_tilde = mu + shift * sigma  # shift towards higher prices
    
    # Sample under shifted measure
    Z = np.random.standard_normal(n_paths)
    ST = S0 * np.exp(mu_tilde * T + sigma * np.sqrt(T) * Z)
    
    # Likelihood ratio (Radon-Nikodym derivative)
    LR = np.exp(-shift * np.sqrt(T) * Z - 0.5 * shift**2 * T)
    
    # Weighted payoff
    payoff = np.maximum(ST - K, 0) * LR
    
    price = np.exp(-r * T) * np.mean(payoff)
    std_error = np.exp(-r * T) * np.std(payoff) / np.sqrt(n_paths)
    
    return price, std_error


if __name__ == "__main__":
    # Parameters
    S0 = 100
    K = 100
    T = 0.25
    r = 0.05
    sigma = 0.20
    n_paths = 100000
    
    # Black-Scholes (true value)
    bs_price = black_scholes_call(S0, K, T, r, sigma)
    
    # Standard Monte Carlo
    mc_price, mc_std = monte_carlo_call(S0, K, T, r, sigma, n_paths)
    
    print("="*60)
    print("Variance Reduction Comparison")
    print("="*60)
    print(f"Parameters: S={S0}, K={K}, T={T}, r={r}, σ={sigma}")
    print(f"Black-Scholes Price: ${bs_price:.4f}")
    print("-"*60)
    
    print(f"\n{'Method':<25} {'Price':>10} {'Std Err':>10} {'VR Ratio':>10}")
    print("-"*60)
    
    print(f"{'Standard MC':<25} ${mc_price:>9.4f} {mc_std:>10.6f} {'1.00x':>10}")
    
    av_price, av_std, av_vr = antithetic_variates_call(S0, K, T, r, sigma, n_paths)
    print(f"{'Antithetic Variates':<25} ${av_price:>9.4f} {av_std:>10.6f} {av_vr:>9.1f}x")
    
    cv_price, cv_std, cv_vr = control_variates_call(S0, K, T, r, sigma, n_paths)
    print(f"{'Control Variates':<25} ${cv_price:>9.4f} {cv_std:>10.6f} {cv_vr:>9.1f}x")
    
    # Deep OTM example for importance sampling
    print("\n" + "="*60)
    print("Importance Sampling for Deep OTM Call (K=130)")
    print("="*60)
    
    K_otm = 130
    bs_otm = black_scholes_call(S0, K_otm, T, r, sigma)
    mc_otm, mc_otm_std = monte_carlo_call(S0, K_otm, T, r, sigma, n_paths)
    is_otm, is_otm_std = importance_sampling_call(S0, K_otm, T, r, sigma, n_paths, shift=1.0)
    
    print(f"Black-Scholes: ${bs_otm:.6f}")
    print(f"Standard MC:   ${mc_otm:.6f} (std: {mc_otm_std:.6f})")
    print(f"Importance:    ${is_otm:.6f} (std: {is_otm_std:.6f})")
