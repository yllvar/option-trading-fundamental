"""
Markowitz Mean-Variance Optimization.
Classic portfolio optimization framework from Modern Portfolio Theory.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def portfolio_return(weights, mean_returns):
    """
    Calculate expected portfolio return.
    
    Parameters:
    -----------
    weights : np.array
        Portfolio weights (sum to 1)
    mean_returns : np.array
        Expected returns for each asset (annualized)
    
    Returns:
    --------
    float : Expected portfolio return
    """
    return np.dot(weights, mean_returns)


def portfolio_volatility(weights, cov_matrix):
    """
    Calculate portfolio volatility (standard deviation).
    
    Parameters:
    -----------
    weights : np.array
        Portfolio weights
    cov_matrix : np.array
        Covariance matrix of returns (annualized)
    
    Returns:
    --------
    float : Portfolio standard deviation
    """
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


def portfolio_sharpe(weights, mean_returns, cov_matrix, risk_free_rate=0.02):
    """
    Calculate portfolio Sharpe ratio.
    
    Sharpe = (E[R_p] - R_f) / σ_p
    """
    ret = portfolio_return(weights, mean_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    return (ret - risk_free_rate) / vol


def neg_sharpe(weights, mean_returns, cov_matrix, risk_free_rate):
    """Negative Sharpe for minimization."""
    return -portfolio_sharpe(weights, mean_returns, cov_matrix, risk_free_rate)


def optimize_sharpe(mean_returns, cov_matrix, risk_free_rate=0.02, 
                    allow_short=False):
    """
    Find the maximum Sharpe ratio portfolio.
    
    Parameters:
    -----------
    mean_returns : np.array
        Expected returns (annualized)
    cov_matrix : np.array
        Covariance matrix (annualized)
    risk_free_rate : float
        Risk-free rate (annualized)
    allow_short : bool
        If True, allow negative weights (short selling)
    
    Returns:
    --------
    dict : {'weights': optimal weights, 'return': expected return, 
            'volatility': portfolio vol, 'sharpe': Sharpe ratio}
    """
    n_assets = len(mean_returns)
    
    # Initial guess: equal weights
    init_weights = np.ones(n_assets) / n_assets
    
    # Constraints: weights sum to 1
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    
    # Bounds: no short selling unless specified
    if allow_short:
        bounds = tuple((-1, 1) for _ in range(n_assets))
    else:
        bounds = tuple((0, 1) for _ in range(n_assets))
    
    # Optimize
    result = minimize(
        neg_sharpe,
        init_weights,
        args=(mean_returns, cov_matrix, risk_free_rate),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    optimal_weights = result.x
    
    return {
        'weights': optimal_weights,
        'return': portfolio_return(optimal_weights, mean_returns),
        'volatility': portfolio_volatility(optimal_weights, cov_matrix),
        'sharpe': portfolio_sharpe(optimal_weights, mean_returns, cov_matrix, 
                                   risk_free_rate)
    }


def optimize_min_variance(mean_returns, cov_matrix, allow_short=False):
    """
    Find the minimum variance portfolio.
    
    Returns:
    --------
    dict : Portfolio statistics
    """
    n_assets = len(mean_returns)
    init_weights = np.ones(n_assets) / n_assets
    
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    
    if allow_short:
        bounds = tuple((-1, 1) for _ in range(n_assets))
    else:
        bounds = tuple((0, 1) for _ in range(n_assets))
    
    result = minimize(
        portfolio_volatility,
        init_weights,
        args=(cov_matrix,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    optimal_weights = result.x
    
    return {
        'weights': optimal_weights,
        'return': portfolio_return(optimal_weights, mean_returns),
        'volatility': portfolio_volatility(optimal_weights, cov_matrix),
        'sharpe': portfolio_sharpe(optimal_weights, mean_returns, cov_matrix)
    }


def optimize_target_return(mean_returns, cov_matrix, target_return, 
                           allow_short=False):
    """
    Find minimum variance portfolio for a target return.
    Used to trace the efficient frontier.
    """
    n_assets = len(mean_returns)
    init_weights = np.ones(n_assets) / n_assets
    
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        {'type': 'eq', 'fun': lambda w: portfolio_return(w, mean_returns) - target_return}
    ]
    
    if allow_short:
        bounds = tuple((-1, 1) for _ in range(n_assets))
    else:
        bounds = tuple((0, 1) for _ in range(n_assets))
    
    result = minimize(
        portfolio_volatility,
        init_weights,
        args=(cov_matrix,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if result.success:
        return result.x, portfolio_volatility(result.x, cov_matrix)
    else:
        return None, None


if __name__ == "__main__":
    # Example with synthetic data
    np.random.seed(42)
    
    # 5 assets
    tickers = ['Asset A', 'Asset B', 'Asset C', 'Asset D', 'Asset E']
    n_assets = len(tickers)
    
    # Expected returns (annualized)
    mean_returns = np.array([0.12, 0.10, 0.14, 0.08, 0.11])
    
    # Generate random correlation matrix
    corr = np.array([
        [1.0, 0.3, 0.2, 0.1, 0.4],
        [0.3, 1.0, 0.5, 0.2, 0.3],
        [0.2, 0.5, 1.0, 0.3, 0.2],
        [0.1, 0.2, 0.3, 1.0, 0.1],
        [0.4, 0.3, 0.2, 0.1, 1.0]
    ])
    
    # Volatilities
    vols = np.array([0.20, 0.15, 0.25, 0.10, 0.18])
    
    # Covariance matrix
    cov_matrix = np.outer(vols, vols) * corr
    
    print("="*60)
    print("Mean-Variance Optimization Results")
    print("="*60)
    
    # Maximum Sharpe portfolio
    max_sharpe = optimize_sharpe(mean_returns, cov_matrix)
    print("\nMaximum Sharpe Ratio Portfolio:")
    print(f"  Expected Return: {max_sharpe['return']*100:.2f}%")
    print(f"  Volatility:      {max_sharpe['volatility']*100:.2f}%")
    print(f"  Sharpe Ratio:    {max_sharpe['sharpe']:.3f}")
    print("  Weights:")
    for i, ticker in enumerate(tickers):
        print(f"    {ticker}: {max_sharpe['weights'][i]*100:.1f}%")
    
    # Minimum variance portfolio
    min_var = optimize_min_variance(mean_returns, cov_matrix)
    print("\nMinimum Variance Portfolio:")
    print(f"  Expected Return: {min_var['return']*100:.2f}%")
    print(f"  Volatility:      {min_var['volatility']*100:.2f}%")
    print(f"  Sharpe Ratio:    {min_var['sharpe']:.3f}")
    print("  Weights:")
    for i, ticker in enumerate(tickers):
        print(f"    {ticker}: {min_var['weights'][i]*100:.1f}%")
