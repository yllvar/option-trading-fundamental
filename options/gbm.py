"""
Geometric Brownian Motion simulation for stock prices.
"""
import numpy as np


def simulate_gbm(S0, mu, sigma, T, dt, n_paths):
    """
    Simulate stock price paths using Geometric Brownian Motion.
    
    Parameters:
    -----------
    S0 : float
        Initial stock price
    mu : float
        Drift (expected return)
    sigma : float
        Volatility
    T : float
        Time to maturity (years)
    dt : float
        Time step
    n_paths : int
        Number of simulation paths
        
    Returns:
    --------
    tuple: (time_points, price_paths)
    """
    n_steps = int(T / dt)
    t = np.linspace(0, T, n_steps + 1)
    
    # Generate random increments
    dW = np.random.normal(0, np.sqrt(dt), (n_paths, n_steps))
    
    # Initialize price array
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0
    
    # Simulate paths using exact solution
    for i in range(n_steps):
        S[:, i+1] = S[:, i] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * dW[:, i])
    
    return t, S


if __name__ == "__main__":
    # Test simulation
    S0 = 100      # Initial price
    mu = 0.05     # 5% expected return
    sigma = 0.2   # 20% volatility
    T = 1.0       # 1 year
    dt = 1/252    # Daily steps
    n_paths = 5
    
    t, S = simulate_gbm(S0, mu, sigma, T, dt, n_paths)
    
    print(f"Simulated {n_paths} paths over {T} year(s)")
    print(f"Initial price: ${S0}")
    print(f"Final prices: {S[:, -1]}")
