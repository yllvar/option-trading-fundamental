"""
Efficient Frontier computation and visualization.
The efficient frontier represents optimal risk-return tradeoffs.
"""

import numpy as np
import matplotlib.pyplot as plt
from markowitz import (
    portfolio_return, portfolio_volatility, portfolio_sharpe,
    optimize_min_variance, optimize_sharpe, optimize_target_return
)


def compute_efficient_frontier(mean_returns, cov_matrix, n_points=100, 
                                allow_short=False, risk_free_rate=0.02):
    """
    Compute the efficient frontier.
    
    Parameters:
    -----------
    mean_returns : np.array
        Expected returns (annualized)
    cov_matrix : np.array
        Covariance matrix (annualized)
    n_points : int
        Number of points on the frontier
    allow_short : bool
        Allow short selling
    risk_free_rate : float
        Risk-free rate for Sharpe calculation
    
    Returns:
    --------
    dict : {
        'returns': array of expected returns,
        'volatilities': array of volatilities,
        'weights': list of weight arrays,
        'sharpes': array of Sharpe ratios
    }
    """
    # Find min variance portfolio
    min_var = optimize_min_variance(mean_returns, cov_matrix, allow_short)
    min_ret = min_var['return']
    
    # Find max return (100% in highest return asset)
    if allow_short:
        max_ret = np.max(mean_returns) * 1.5  # Allow for leverage
    else:
        max_ret = np.max(mean_returns)
    
    # Target returns for frontier
    target_returns = np.linspace(min_ret, max_ret, n_points)
    
    frontier_vols = []
    frontier_weights = []
    frontier_sharpes = []
    valid_returns = []
    
    for target in target_returns:
        weights, vol = optimize_target_return(
            mean_returns, cov_matrix, target, allow_short
        )
        if weights is not None:
            frontier_vols.append(vol)
            frontier_weights.append(weights)
            sharpe = (target - risk_free_rate) / vol
            frontier_sharpes.append(sharpe)
            valid_returns.append(target)
    
    return {
        'returns': np.array(valid_returns),
        'volatilities': np.array(frontier_vols),
        'weights': frontier_weights,
        'sharpes': np.array(frontier_sharpes)
    }


def generate_random_portfolios(mean_returns, cov_matrix, n_portfolios=5000,
                                risk_free_rate=0.02):
    """
    Generate random portfolios for Monte Carlo visualization.
    
    Returns:
    --------
    dict : {'returns': array, 'volatilities': array, 'sharpes': array}
    """
    n_assets = len(mean_returns)
    
    returns = []
    volatilities = []
    sharpes = []
    
    for _ in range(n_portfolios):
        # Random weights
        weights = np.random.random(n_assets)
        weights /= weights.sum()
        
        ret = portfolio_return(weights, mean_returns)
        vol = portfolio_volatility(weights, cov_matrix)
        sharpe = (ret - risk_free_rate) / vol
        
        returns.append(ret)
        volatilities.append(vol)
        sharpes.append(sharpe)
    
    return {
        'returns': np.array(returns),
        'volatilities': np.array(volatilities),
        'sharpes': np.array(sharpes)
    }


def plot_efficient_frontier(mean_returns, cov_matrix, tickers=None,
                            risk_free_rate=0.02, show_random=True,
                            show_cml=True, save_path=None):
    """
    Plot the efficient frontier with key portfolios.
    
    Parameters:
    -----------
    mean_returns : np.array
        Expected returns
    cov_matrix : np.array
        Covariance matrix
    tickers : list, optional
        Asset names for legend
    risk_free_rate : float
        Risk-free rate
    show_random : bool
        Show Monte Carlo random portfolios
    show_cml : bool
        Show Capital Market Line
    save_path : str, optional
        Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Random portfolios
    if show_random:
        random_pf = generate_random_portfolios(
            mean_returns, cov_matrix, n_portfolios=5000, 
            risk_free_rate=risk_free_rate
        )
        scatter = ax.scatter(
            random_pf['volatilities'] * 100,
            random_pf['returns'] * 100,
            c=random_pf['sharpes'],
            cmap='viridis',
            alpha=0.5,
            s=10,
            label='Random Portfolios'
        )
        plt.colorbar(scatter, label='Sharpe Ratio')
    
    # Efficient frontier
    frontier = compute_efficient_frontier(
        mean_returns, cov_matrix, n_points=100, risk_free_rate=risk_free_rate
    )
    ax.plot(
        frontier['volatilities'] * 100,
        frontier['returns'] * 100,
        'r-',
        linewidth=3,
        label='Efficient Frontier'
    )
    
    # Maximum Sharpe portfolio
    max_sharpe = optimize_sharpe(mean_returns, cov_matrix, risk_free_rate)
    ax.scatter(
        max_sharpe['volatility'] * 100,
        max_sharpe['return'] * 100,
        marker='*',
        s=500,
        c='gold',
        edgecolors='black',
        label=f"Max Sharpe (SR={max_sharpe['sharpe']:.2f})"
    )
    
    # Minimum variance portfolio
    min_var = optimize_min_variance(mean_returns, cov_matrix)
    ax.scatter(
        min_var['volatility'] * 100,
        min_var['return'] * 100,
        marker='o',
        s=300,
        c='blue',
        edgecolors='black',
        label=f"Min Variance (σ={min_var['volatility']*100:.1f}%)"
    )
    
    # Capital Market Line
    if show_cml:
        # Line from risk-free to tangent portfolio
        x_cml = np.linspace(0, max_sharpe['volatility'] * 1.5 * 100, 100)
        y_cml = risk_free_rate * 100 + max_sharpe['sharpe'] * x_cml
        ax.plot(x_cml, y_cml, 'g--', linewidth=2, label='Capital Market Line')
        ax.scatter(0, risk_free_rate * 100, marker='s', s=100, c='green',
                   label=f'Risk-Free Rate ({risk_free_rate*100:.1f}%)')
    
    # Individual assets
    n_assets = len(mean_returns)
    asset_vols = np.sqrt(np.diag(cov_matrix))
    
    for i in range(n_assets):
        label = tickers[i] if tickers else f'Asset {i+1}'
        ax.scatter(
            asset_vols[i] * 100,
            mean_returns[i] * 100,
            marker='D',
            s=150,
            edgecolors='black',
            label=label
        )
    
    ax.set_xlabel('Volatility (%)', fontsize=12)
    ax.set_ylabel('Expected Return (%)', fontsize=12)
    ax.set_title('Efficient Frontier - Mean-Variance Optimization', fontsize=14)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved figure to {save_path}")
    
    return fig


if __name__ == "__main__":
    # Example with synthetic data
    np.random.seed(42)
    
    tickers = ['Tech', 'Healthcare', 'Finance', 'Energy', 'Consumer']
    n_assets = len(tickers)
    
    # Expected returns
    mean_returns = np.array([0.15, 0.10, 0.08, 0.12, 0.09])
    
    # Correlation matrix
    corr = np.array([
        [1.0, 0.3, 0.4, 0.2, 0.5],
        [0.3, 1.0, 0.3, 0.1, 0.4],
        [0.4, 0.3, 1.0, 0.5, 0.3],
        [0.2, 0.1, 0.5, 1.0, 0.2],
        [0.5, 0.4, 0.3, 0.2, 1.0]
    ])
    
    # Volatilities
    vols = np.array([0.25, 0.15, 0.18, 0.22, 0.14])
    
    # Covariance matrix
    cov_matrix = np.outer(vols, vols) * corr
    
    # Plot
    fig = plot_efficient_frontier(
        mean_returns, cov_matrix, tickers,
        risk_free_rate=0.02,
        show_random=True,
        show_cml=True
    )
    
    plt.show()
