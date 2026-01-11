"""
European option pricing using Monte Carlo simulation.
"""
import numpy as np
from options.gbm import simulate_gbm


def price_european_call(S0, K, r, sigma, T, n_paths=10000, n_steps=252):
    """
    Price a European call option using Monte Carlo simulation.
    
    Parameters:
    -----------
    S0 : float
        Initial stock price
    K : float
        Strike price
    r : float
        Risk-free rate
    sigma : float
        Volatility
    T : float
        Time to maturity (years)
    n_paths : int
        Number of simulation paths
    n_steps : int
        Number of time steps
        
    Returns:
    --------
    float: Option price
    """
    dt = T / n_steps
    
    # Simulate under risk-neutral measure (mu = r)
    _, S = simulate_gbm(S0, r, sigma, T, dt, n_paths)
    
    # Calculate payoffs at maturity
    payoffs = np.maximum(S[:, -1] - K, 0)
    
    # Discount to present value
    price = np.exp(-r * T) * np.mean(payoffs)
    
    return price


def price_european_put(S0, K, r, sigma, T, n_paths=10000, n_steps=252):
    """
    Price a European put option using Monte Carlo simulation.
    """
    dt = T / n_steps
    _, S = simulate_gbm(S0, r, sigma, T, dt, n_paths)
    payoffs = np.maximum(K - S[:, -1], 0)
    price = np.exp(-r * T) * np.mean(payoffs)
    return price


if __name__ == "__main__":
    # Parameters
    S0 = 100      # Stock price
    K = 100       # Strike (at-the-money)
    r = 0.05      # Risk-free rate
    sigma = 0.2   # Volatility
    T = 1.0       # 1 year
    
    call_price = price_european_call(S0, K, r, sigma, T)
    put_price = price_european_put(S0, K, r, sigma, T)
    
    print(f"European Call Price: ${call_price:.4f}")
    print(f"European Put Price: ${put_price:.4f}")
    
    # Check put-call parity: C - P = S0 - K*exp(-rT)
    parity_lhs = call_price - put_price
    parity_rhs = S0 - K * np.exp(-r * T)
    print(f"\nPut-Call Parity Check:")
    print(f"  C - P = ${parity_lhs:.4f}")
    print(f"  S - Ke^(-rT) = ${parity_rhs:.4f}")
