"""
Portfolio backtesting with rebalancing.
Tests allocation strategies on historical data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_loader import fetch_prices, calculate_returns
from markowitz import optimize_sharpe, optimize_min_variance
from risk_parity import optimize_risk_parity


def backtest_portfolio(prices, weights, rebalance_freq='M'):
    """
    Backtest a static portfolio allocation.
    
    Parameters:
    -----------
    prices : pd.DataFrame
        Historical prices
    weights : np.array
        Portfolio weights
    rebalance_freq : str
        Rebalancing frequency: 'D' (daily), 'W' (weekly), 
        'M' (monthly), 'Q' (quarterly), 'Y' (yearly), None (buy and hold)
    
    Returns:
    --------
    pd.Series : Portfolio value over time (starting at 1)
    """
    returns = prices.pct_change().dropna()
    
    if rebalance_freq is None:
        # Buy and hold - just track weighted returns
        portfolio_returns = returns.dot(weights)
        portfolio_value = (1 + portfolio_returns).cumprod()
    else:
        # Rebalancing
        portfolio_value = [1.0]
        current_weights = weights.copy()
        
        # Get rebalance dates
        rebalance_dates = returns.resample(rebalance_freq).last().index
        
        for i in range(len(returns)):
            date = returns.index[i]
            daily_return = returns.iloc[i]
            
            # Portfolio return for the day
            port_ret = np.dot(current_weights, daily_return)
            portfolio_value.append(portfolio_value[-1] * (1 + port_ret))
            
            # Rebalance if needed
            if date in rebalance_dates:
                current_weights = weights.copy()
        
        portfolio_value = pd.Series(portfolio_value[1:], index=returns.index)
    
    return portfolio_value


def calculate_metrics(portfolio_value, risk_free_rate=0.02):
    """
    Calculate portfolio performance metrics.
    
    Returns:
    --------
    dict : Performance metrics
    """
    returns = portfolio_value.pct_change().dropna()
    
    # Annualization factor
    periods_per_year = 252
    
    # Total return
    total_return = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1
    
    # Annualized return
    years = len(returns) / periods_per_year
    ann_return = (1 + total_return) ** (1 / years) - 1
    
    # Annualized volatility
    ann_vol = returns.std() * np.sqrt(periods_per_year)
    
    # Sharpe ratio
    sharpe = (ann_return - risk_free_rate) / ann_vol
    
    # Maximum drawdown
    cummax = portfolio_value.cummax()
    drawdown = (portfolio_value - cummax) / cummax
    max_drawdown = drawdown.min()
    
    # Sortino ratio (downside deviation)
    downside_returns = returns[returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(periods_per_year)
    sortino = (ann_return - risk_free_rate) / downside_vol if downside_vol > 0 else np.inf
    
    # Calmar ratio
    calmar = ann_return / abs(max_drawdown) if max_drawdown != 0 else np.inf
    
    return {
        'total_return': total_return,
        'ann_return': ann_return,
        'ann_volatility': ann_vol,
        'sharpe': sharpe,
        'sortino': sortino,
        'max_drawdown': max_drawdown,
        'calmar': calmar
    }


def run_backtest(tickers, start_date, end_date, strategies=None, 
                  rebalance_freq='M', lookback=252):
    """
    Run backtest comparing multiple strategies.
    
    Parameters:
    -----------
    tickers : list
        Asset tickers
    start_date, end_date : str
        Date range
    strategies : list, optional
        List of strategy names to test
    rebalance_freq : str
        Rebalancing frequency
    lookback : int
        Lookback period for optimization (trading days)
    
    Returns:
    --------
    dict : Results for each strategy
    """
    # Fetch data
    print(f"Fetching data for {tickers}...")
    prices = fetch_prices(tickers, start_date=start_date, end_date=end_date)
    returns = calculate_returns(prices, method='simple')
    
    n_assets = len(tickers)
    
    if strategies is None:
        strategies = ['Equal Weight', 'Inverse Vol', 'Risk Parity', 
                     'Min Variance', 'Max Sharpe']
    
    results = {}
    
    for strategy in strategies:
        print(f"Backtesting {strategy}...")
        
        # Calculate weights based on strategy
        # Using first `lookback` days for optimization
        opt_returns = returns.iloc[:lookback]
        mean_ret = opt_returns.mean() * 252
        cov_mat = opt_returns.cov() * 252
        
        if strategy == 'Equal Weight':
            weights = np.ones(n_assets) / n_assets
        elif strategy == 'Inverse Vol':
            vols = np.sqrt(np.diag(cov_mat))
            weights = (1 / vols) / (1 / vols).sum()
        elif strategy == 'Risk Parity':
            rp = optimize_risk_parity(cov_mat.values)
            weights = rp['weights']
        elif strategy == 'Min Variance':
            mv = optimize_min_variance(mean_ret.values, cov_mat.values)
            weights = mv['weights']
        elif strategy == 'Max Sharpe':
            ms = optimize_sharpe(mean_ret.values, cov_mat.values)
            weights = ms['weights']
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Backtest on remaining data
        test_prices = prices.iloc[lookback:]
        portfolio_value = backtest_portfolio(test_prices, weights, rebalance_freq)
        metrics = calculate_metrics(portfolio_value)
        
        results[strategy] = {
            'weights': weights,
            'portfolio_value': portfolio_value,
            'metrics': metrics
        }
    
    return results


def plot_backtest_results(results, tickers=None, save_path=None):
    """
    Plot backtest comparison.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Portfolio value
    ax1 = axes[0, 0]
    for strategy, data in results.items():
        ax1.plot(data['portfolio_value'], label=strategy, linewidth=1.5)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Portfolio Value')
    ax1.set_title('Portfolio Growth (Starting at $1)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Drawdown
    ax2 = axes[0, 1]
    for strategy, data in results.items():
        pv = data['portfolio_value']
        drawdown = (pv - pv.cummax()) / pv.cummax()
        ax2.fill_between(drawdown.index, drawdown.values * 100, alpha=0.3)
        ax2.plot(drawdown.index, drawdown.values * 100, label=strategy)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_title('Drawdown Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Risk-Return scatter
    ax3 = axes[1, 0]
    for strategy, data in results.items():
        m = data['metrics']
        ax3.scatter(m['ann_volatility'] * 100, m['ann_return'] * 100, 
                   s=100, label=strategy)
        ax3.annotate(strategy, (m['ann_volatility'] * 100 + 0.2, 
                               m['ann_return'] * 100))
    ax3.set_xlabel('Annualized Volatility (%)')
    ax3.set_ylabel('Annualized Return (%)')
    ax3.set_title('Risk-Return Tradeoff')
    ax3.grid(True, alpha=0.3)
    
    # 4. Metrics table
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    metrics_data = []
    for strategy, data in results.items():
        m = data['metrics']
        metrics_data.append([
            strategy,
            f"{m['ann_return']*100:.1f}%",
            f"{m['ann_volatility']*100:.1f}%",
            f"{m['sharpe']:.2f}",
            f"{m['max_drawdown']*100:.1f}%"
        ])
    
    table = ax4.table(
        cellText=metrics_data,
        colLabels=['Strategy', 'Return', 'Vol', 'Sharpe', 'Max DD'],
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    ax4.set_title('Performance Metrics', y=0.8)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


if __name__ == "__main__":
    # Example backtest
    tickers = ['SPY', 'AGG', 'GLD', 'VNQ', 'EFA']  # Diversified ETFs
    
    results = run_backtest(
        tickers,
        start_date='2018-01-01',
        end_date='2023-12-31',
        rebalance_freq='M'
    )
    
    # Print summary
    print("\n" + "="*70)
    print("Backtest Results Summary")
    print("="*70)
    
    print(f"\n{'Strategy':<15} {'Return':>10} {'Vol':>10} {'Sharpe':>10} {'Max DD':>10}")
    print("-"*60)
    for strategy, data in results.items():
        m = data['metrics']
        print(f"{strategy:<15} {m['ann_return']*100:>9.1f}% {m['ann_volatility']*100:>9.1f}% "
              f"{m['sharpe']:>10.2f} {m['max_drawdown']*100:>9.1f}%")
    
    # Plot
    fig = plot_backtest_results(results, tickers)
    plt.show()
