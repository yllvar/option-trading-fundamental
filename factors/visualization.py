"""
Visualization tools for factor model analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ff3_model import FF3Model
from data_loader import fetch_ff_factors, fetch_stock_returns, align_data


def plot_rolling_betas(ticker, window=252, period='5y'):
    """
    Plot rolling factor betas over time.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker
    window : int
        Rolling window size (trading days)
    period : str
        Data period
    """
    # Fetch data
    stock_returns = fetch_stock_returns(ticker, period=period)
    ff_factors = fetch_ff_factors(model='3', frequency='daily')
    excess_returns, factors = align_data(stock_returns, ff_factors)
    
    # Rolling regression
    factor_names = ['Mkt-RF', 'SMB', 'HML']
    rolling_betas = {f: [] for f in factor_names}
    rolling_alpha = []
    dates = []
    
    for i in range(window, len(excess_returns)):
        # Window data
        y = excess_returns.iloc[i-window:i]
        X = factors.iloc[i-window:i]
        
        # Fit model
        model = FF3Model()
        model.fit(y, X)
        
        for f in factor_names:
            rolling_betas[f].append(model.betas[f])
        rolling_alpha.append(model.alpha * 252)  # Annualized
        dates.append(excess_returns.index[i])
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Market beta
    ax = axes[0, 0]
    ax.plot(dates, rolling_betas['Mkt-RF'], 'b-', linewidth=1)
    ax.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    ax.fill_between(dates, rolling_betas['Mkt-RF'], 1, alpha=0.3)
    ax.set_title(f'{ticker} Rolling Market Beta')
    ax.set_ylabel('Beta')
    ax.grid(True, alpha=0.3)
    
    # SMB beta
    ax = axes[0, 1]
    ax.plot(dates, rolling_betas['SMB'], 'g-', linewidth=1)
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax.fill_between(dates, rolling_betas['SMB'], 0, alpha=0.3)
    ax.set_title(f'{ticker} Rolling SMB Beta (Size)')
    ax.set_ylabel('Beta')
    ax.grid(True, alpha=0.3)
    
    # HML beta
    ax = axes[1, 0]
    ax.plot(dates, rolling_betas['HML'], 'm-', linewidth=1)
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax.fill_between(dates, rolling_betas['HML'], 0, alpha=0.3)
    ax.set_title(f'{ticker} Rolling HML Beta (Value)')
    ax.set_ylabel('Beta')
    ax.grid(True, alpha=0.3)
    
    # Alpha
    ax = axes[1, 1]
    ax.plot(dates, np.array(rolling_alpha) * 100, 'orange', linewidth=1)
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax.fill_between(dates, np.array(rolling_alpha) * 100, 0, alpha=0.3)
    ax.set_title(f'{ticker} Rolling Alpha (Annualized)')
    ax.set_ylabel('Alpha (%)')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle(f'Rolling Factor Analysis: {ticker} ({window}-day window)', fontsize=14)
    plt.tight_layout()
    
    return fig


def plot_factor_exposure_comparison(tickers, period='3y'):
    """
    Compare factor exposures across multiple stocks.
    """
    ff_factors = fetch_ff_factors(model='3', frequency='daily')
    factor_names = ['Mkt-RF', 'SMB', 'HML']
    
    results = []
    
    for ticker in tickers:
        stock_returns = fetch_stock_returns(ticker, period=period)
        excess_returns, factors = align_data(stock_returns, ff_factors)
        
        model = FF3Model()
        model.fit(excess_returns, factors)
        
        results.append({
            'ticker': ticker,
            'Mkt-RF': model.betas['Mkt-RF'],
            'SMB': model.betas['SMB'],
            'HML': model.betas['HML'],
            'Alpha': model.alpha * 252
        })
    
    df = pd.DataFrame(results)
    df = df.set_index('ticker')
    
    # Plot
    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(tickers)))
    
    # Market Beta
    ax = axes[0]
    bars = ax.bar(df.index, df['Mkt-RF'], color=colors)
    ax.axhline(y=1, color='r', linestyle='--', alpha=0.5, label='Market')
    ax.set_title('Market Beta')
    ax.set_ylabel('Beta')
    ax.tick_params(axis='x', rotation=45)
    
    # SMB Beta
    ax = axes[1]
    colors_smb = ['green' if x > 0 else 'red' for x in df['SMB']]
    ax.bar(df.index, df['SMB'], color=colors_smb, alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax.set_title('Size Beta (SMB)')
    ax.set_ylabel('Beta')
    ax.tick_params(axis='x', rotation=45)
    
    # HML Beta
    ax = axes[2]
    colors_hml = ['green' if x > 0 else 'red' for x in df['HML']]
    ax.bar(df.index, df['HML'], color=colors_hml, alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax.set_title('Value Beta (HML)')
    ax.set_ylabel('Beta')
    ax.tick_params(axis='x', rotation=45)
    
    # Alpha
    ax = axes[3]
    colors_alpha = ['green' if x > 0 else 'red' for x in df['Alpha']]
    ax.bar(df.index, df['Alpha'] * 100, color=colors_alpha, alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax.set_title('Alpha (Annualized)')
    ax.set_ylabel('Alpha (%)')
    ax.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Factor Exposure Comparison', fontsize=14)
    plt.tight_layout()
    
    return fig, df


def plot_cumulative_factor_returns(period='5y'):
    """
    Plot cumulative returns of Fama-French factors.
    """
    ff_factors = fetch_ff_factors(model='3', frequency='daily')
    
    # Cumulative returns
    cum_returns = (1 + ff_factors[['Mkt-RF', 'SMB', 'HML']]).cumprod()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(cum_returns.index, cum_returns['Mkt-RF'], 'b-', 
            linewidth=1.5, label='Market (Mkt-RF)')
    ax.plot(cum_returns.index, cum_returns['SMB'], 'g-', 
            linewidth=1.5, label='Size (SMB)')
    ax.plot(cum_returns.index, cum_returns['HML'], 'r-', 
            linewidth=1.5, label='Value (HML)')
    
    ax.axhline(y=1, color='black', linestyle='--', alpha=0.3)
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Return (Growth of $1)')
    ax.set_title('Fama-French Factor Cumulative Returns')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add annotations
    final_vals = cum_returns.iloc[-1]
    for factor in ['Mkt-RF', 'SMB', 'HML']:
        years = len(cum_returns) / 252
        cagr = (final_vals[factor] ** (1/years) - 1) * 100
        ax.annotate(f'{factor}: {cagr:.1f}% CAGR', 
                   xy=(cum_returns.index[-1], final_vals[factor]),
                   xytext=(10, 0), textcoords='offset points')
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Example visualizations
    
    # 1. Rolling betas for Apple
    print("Generating rolling beta plot...")
    fig1 = plot_rolling_betas('AAPL', window=252, period='5y')
    
    # 2. Factor exposure comparison
    print("Generating factor comparison...")
    tickers = ['AAPL', 'MSFT', 'JPM', 'XOM', 'JNJ']
    fig2, exposure_df = plot_factor_exposure_comparison(tickers, period='3y')
    
    print("\nFactor Exposures:")
    print(exposure_df.round(3))
    
    # 3. Cumulative factor returns
    print("Generating factor returns plot...")
    fig3 = plot_cumulative_factor_returns(period='10y')
    
    plt.show()
