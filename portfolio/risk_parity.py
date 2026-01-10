"""
Risk Parity Portfolio Optimization.
Allocates capital so each asset contributes equally to portfolio risk.
"""

import numpy as np
from scipy.optimize import minimize


def risk_contribution(weights, cov_matrix):
    """
    Calculate the risk contribution of each asset.
    
    Risk contribution = w_i * (Σw)_i / σ_p
    
    Parameters:
    -----------
    weights : np.array
        Portfolio weights
    cov_matrix : np.array
        Covariance matrix
    
    Returns:
    --------
    np.array : Risk contribution of each asset
    """
    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    marginal_contrib = np.dot(cov_matrix, weights)
    risk_contrib = weights * marginal_contrib / portfolio_vol
    return risk_contrib


def risk_contribution_pct(weights, cov_matrix):
    """
    Calculate percentage risk contribution of each asset.
    Should sum to 100% (or 1.0).
    """
    rc = risk_contribution(weights, cov_matrix)
    return rc / rc.sum()


def risk_parity_objective(weights, cov_matrix, target_risk=None):
    """
    Objective function for risk parity optimization.
    
    Minimizes the sum of squared differences between each asset's
    risk contribution and the target (equal) risk contribution.
    
    If target_risk is None, targets equal risk contribution (1/n).
    """
    n_assets = len(weights)
    
    if target_risk is None:
        target_risk = np.ones(n_assets) / n_assets
    
    rc_pct = risk_contribution_pct(weights, cov_matrix)
    
    # Sum of squared differences from target
    return np.sum((rc_pct - target_risk) ** 2)


def optimize_risk_parity(cov_matrix, target_risk=None):
    """
    Find the risk parity portfolio.
    
    Parameters:
    -----------
    cov_matrix : np.array
        Covariance matrix (annualized)
    target_risk : np.array, optional
        Target risk contribution per asset. Default: equal (1/n)
    
    Returns:
    --------
    dict : {
        'weights': optimal weights,
        'risk_contributions': risk contribution percentages,
        'volatility': portfolio volatility
    }
    """
    n_assets = cov_matrix.shape[0]
    
    # Initial guess: inverse volatility weights
    vols = np.sqrt(np.diag(cov_matrix))
    init_weights = (1 / vols) / (1 / vols).sum()
    
    # Constraints
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    ]
    
    # Bounds: long-only
    bounds = tuple((0.01, 1) for _ in range(n_assets))  # min 1% per asset
    
    # Optimize
    result = minimize(
        risk_parity_objective,
        init_weights,
        args=(cov_matrix, target_risk),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'ftol': 1e-12}
    )
    
    optimal_weights = result.x
    portfolio_vol = np.sqrt(np.dot(optimal_weights.T, 
                                    np.dot(cov_matrix, optimal_weights)))
    
    return {
        'weights': optimal_weights,
        'risk_contributions': risk_contribution_pct(optimal_weights, cov_matrix),
        'volatility': portfolio_vol,
        'success': result.success
    }


def inverse_volatility_weights(cov_matrix):
    """
    Simple inverse volatility weighting.
    A naive risk-based allocation (not true risk parity).
    """
    vols = np.sqrt(np.diag(cov_matrix))
    weights = (1 / vols) / (1 / vols).sum()
    return weights


def compare_allocations(mean_returns, cov_matrix, risk_free_rate=0.02):
    """
    Compare different allocation strategies.
    """
    from markowitz import (
        optimize_sharpe, optimize_min_variance, 
        portfolio_return, portfolio_volatility, portfolio_sharpe
    )
    
    n_assets = len(mean_returns)
    
    results = {}
    
    # Equal weight
    eq_weights = np.ones(n_assets) / n_assets
    results['Equal Weight'] = {
        'weights': eq_weights,
        'return': portfolio_return(eq_weights, mean_returns),
        'volatility': portfolio_volatility(eq_weights, cov_matrix),
        'sharpe': portfolio_sharpe(eq_weights, mean_returns, cov_matrix, risk_free_rate),
        'risk_contrib': risk_contribution_pct(eq_weights, cov_matrix)
    }
    
    # Inverse volatility
    iv_weights = inverse_volatility_weights(cov_matrix)
    results['Inverse Vol'] = {
        'weights': iv_weights,
        'return': portfolio_return(iv_weights, mean_returns),
        'volatility': portfolio_volatility(iv_weights, cov_matrix),
        'sharpe': portfolio_sharpe(iv_weights, mean_returns, cov_matrix, risk_free_rate),
        'risk_contrib': risk_contribution_pct(iv_weights, cov_matrix)
    }
    
    # Risk parity
    rp = optimize_risk_parity(cov_matrix)
    results['Risk Parity'] = {
        'weights': rp['weights'],
        'return': portfolio_return(rp['weights'], mean_returns),
        'volatility': rp['volatility'],
        'sharpe': portfolio_sharpe(rp['weights'], mean_returns, cov_matrix, risk_free_rate),
        'risk_contrib': rp['risk_contributions']
    }
    
    # Max Sharpe
    ms = optimize_sharpe(mean_returns, cov_matrix, risk_free_rate)
    results['Max Sharpe'] = {
        'weights': ms['weights'],
        'return': ms['return'],
        'volatility': ms['volatility'],
        'sharpe': ms['sharpe'],
        'risk_contrib': risk_contribution_pct(ms['weights'], cov_matrix)
    }
    
    # Min Variance
    mv = optimize_min_variance(mean_returns, cov_matrix)
    results['Min Variance'] = {
        'weights': mv['weights'],
        'return': mv['return'],
        'volatility': mv['volatility'],
        'sharpe': mv['sharpe'],
        'risk_contrib': risk_contribution_pct(mv['weights'], cov_matrix)
    }
    
    return results


if __name__ == "__main__":
    import pandas as pd
    
    # Example with realistic parameters
    tickers = ['US Equity', 'Intl Equity', 'US Bonds', 'Commodities', 'REITs']
    n_assets = len(tickers)
    
    # Expected returns
    mean_returns = np.array([0.08, 0.07, 0.03, 0.04, 0.06])
    
    # Volatilities (typical values)
    vols = np.array([0.16, 0.18, 0.04, 0.15, 0.18])
    
    # Correlation matrix
    corr = np.array([
        [1.00, 0.80, 0.10, 0.20, 0.60],
        [0.80, 1.00, 0.05, 0.25, 0.55],
        [0.10, 0.05, 1.00, -0.10, 0.15],
        [0.20, 0.25, -0.10, 1.00, 0.30],
        [0.60, 0.55, 0.15, 0.30, 1.00]
    ])
    
    cov_matrix = np.outer(vols, vols) * corr
    
    print("="*70)
    print("Risk Parity vs Other Allocation Strategies")
    print("="*70)
    
    # Compare strategies
    results = compare_allocations(mean_returns, cov_matrix)
    
    # Print comparison table
    print(f"\n{'Strategy':<15} {'Return':>8} {'Vol':>8} {'Sharpe':>8}")
    print("-"*45)
    for name, data in results.items():
        print(f"{name:<15} {data['return']*100:>7.2f}% {data['volatility']*100:>7.2f}% {data['sharpe']:>8.3f}")
    
    # Detailed risk parity analysis
    print("\n" + "="*70)
    print("Risk Parity Portfolio Detail")
    print("="*70)
    rp = optimize_risk_parity(cov_matrix)
    
    print(f"\n{'Asset':<15} {'Weight':>10} {'Risk Contrib':>15}")
    print("-"*45)
    for i, ticker in enumerate(tickers):
        print(f"{ticker:<15} {rp['weights'][i]*100:>9.1f}% {rp['risk_contributions'][i]*100:>14.1f}%")
    
    print(f"\nPortfolio Volatility: {rp['volatility']*100:.2f}%")
    print(f"Risk contribution std: {np.std(rp['risk_contributions'])*100:.4f}%")
    print("(Should be near 0 for perfect risk parity)")
