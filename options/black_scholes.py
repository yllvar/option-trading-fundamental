"""
Black-Scholes analytical formulas for comparison.
"""
import numpy as np
from scipy.stats import norm


def black_scholes_call(S0, K, r, sigma, T):
    """
    Analytical Black-Scholes price for European call option.
    """
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    call = S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call


def black_scholes_put(S0, K, r, sigma, T):
    """
    Analytical Black-Scholes price for European put option.
    """
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    put = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)
    return put


if __name__ == "__main__":
    from european_options import price_european_call, price_european_put
    
    # Parameters
    S0 = 100
    K = 100
    r = 0.05
    sigma = 0.2
    T = 1.0
    
    # Analytical prices
    bs_call = black_scholes_call(S0, K, r, sigma, T)
    bs_put = black_scholes_put(S0, K, r, sigma, T)
    
    # Monte Carlo prices
    mc_call = price_european_call(S0, K, r, sigma, T, n_paths=100000)
    mc_put = price_european_put(S0, K, r, sigma, T, n_paths=100000)
    
    print("Comparison: Black-Scholes vs Monte Carlo (100k paths)")
    print("-" * 50)
    print(f"Call - BS: ${bs_call:.4f}, MC: ${mc_call:.4f}, Error: {abs(mc_call - bs_call):.4f}")
    print(f"Put  - BS: ${bs_put:.4f}, MC: ${mc_put:.4f}, Error: {abs(mc_put - bs_put):.4f}")
