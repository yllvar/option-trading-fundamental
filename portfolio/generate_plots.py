"""Generate all visualization plots for portfolio-optimization project."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from markowitz import (
    portfolio_return, portfolio_volatility, 
    optimize_min_variance, optimize_sharpe, optimize_target_return
)
from efficient_frontier import compute_efficient_frontier, generate_random_portfolios
from risk_parity import optimize_risk_parity, risk_contribution

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

print("="*60)
print("PORTFOLIO OPTIMIZATION - GENERATING PLOTS")
print("="*60)

# Create plots directory
import os
os.makedirs('plots', exist_ok=True)

# Fetch data
print("\nFetching market data...")
tickers = ['SPY', 'TLT', 'GLD', 'VNQ', 'EFA']  # Diversified portfolio
ticker_names = ['US Equities', 'US Bonds', 'Gold', 'Real Estate', 'Intl Equities']
data = yf.download(tickers, start='2019-01-01', end='2024-01-01', progress=False, auto_adjust=True)['Close']
returns = data.pct_change().dropna()

# Annualized stats
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252
risk_free_rate = 0.04

print(f"   ✓ Downloaded {len(returns)} days of data for {len(tickers)} assets")

# 1. Efficient Frontier
print("\n1. Efficient Frontier with Random Portfolios...")

# Random portfolios
np.random.seed(42)
n_portfolios = 5000
random_weights = np.random.dirichlet(np.ones(len(tickers)), n_portfolios)
random_returns = [portfolio_return(w, mean_returns) for w in random_weights]
random_vols = [portfolio_volatility(w, cov_matrix) for w in random_weights]
random_sharpes = [(r - risk_free_rate) / v for r, v in zip(random_returns, random_vols)]

# Efficient frontier
frontier = compute_efficient_frontier(mean_returns.values, cov_matrix.values, 
                                       n_points=100, allow_short=False, 
                                       risk_free_rate=risk_free_rate)

# Key portfolios
min_var = optimize_min_variance(mean_returns.values, cov_matrix.values, allow_short=False)
max_sharpe = optimize_sharpe(mean_returns.values, cov_matrix.values, 
                              risk_free_rate=risk_free_rate, allow_short=False)

fig, ax = plt.subplots(figsize=(12, 8))

# Random portfolios (colored by Sharpe)
scatter = ax.scatter(random_vols, random_returns, c=random_sharpes, 
                     cmap='RdYlGn', alpha=0.5, s=10)
cbar = plt.colorbar(scatter, ax=ax, label='Sharpe Ratio')

# Efficient frontier
ax.plot(frontier['volatilities'], frontier['returns'], 'b-', linewidth=3, 
        label='Efficient Frontier')

# Min variance portfolio
ax.scatter(min_var['volatility'], min_var['return'], c='blue', marker='*', 
           s=400, edgecolor='black', linewidth=2, label='Min Variance', zorder=5)

# Max Sharpe portfolio
ax.scatter(max_sharpe['volatility'], max_sharpe['return'], c='gold', marker='*',
           s=400, edgecolor='black', linewidth=2, label='Max Sharpe', zorder=5)

# Capital Market Line
cml_x = np.linspace(0, max(random_vols) * 0.8, 100)
cml_y = risk_free_rate + max_sharpe['sharpe'] * cml_x
ax.plot(cml_x, cml_y, 'g--', linewidth=2, label=f'CML (Sharpe={max_sharpe["sharpe"]:.2f})')

ax.set_xlabel('Annualized Volatility', fontsize=12)
ax.set_ylabel('Annualized Return', fontsize=12)
ax.set_title('Mean-Variance Efficient Frontier\n(SPY, TLT, GLD, VNQ, EFA: 2019-2024)', 
             fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=10)
ax.set_xlim(0, max(random_vols) * 1.1)
ax.set_ylim(min(random_returns) * 0.9, max(random_returns) * 1.1)

plt.tight_layout()
plt.savefig('plots/efficient_frontier.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/efficient_frontier.png")

# 2. Optimal Portfolio Allocation
print("2. Optimal Portfolio Allocations...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Min Variance
ax = axes[0]
colors = plt.cm.Set2(np.linspace(0, 1, len(tickers)))
ax.pie(min_var['weights'], labels=ticker_names, autopct='%1.1f%%', colors=colors,
       startangle=90, explode=[0.02]*len(tickers))
ax.set_title(f'Minimum Variance\nReturn: {min_var["return"]*100:.1f}%, Vol: {min_var["volatility"]*100:.1f}%',
             fontsize=12, fontweight='bold')

# Max Sharpe
ax = axes[1]
ax.pie(max_sharpe['weights'], labels=ticker_names, autopct='%1.1f%%', colors=colors,
       startangle=90, explode=[0.02]*len(tickers))
ax.set_title(f'Maximum Sharpe\nReturn: {max_sharpe["return"]*100:.1f}%, Vol: {max_sharpe["volatility"]*100:.1f}%',
             fontsize=12, fontweight='bold')

# Equal Weight
ax = axes[2]
eq_weights = np.ones(len(tickers)) / len(tickers)
eq_ret = portfolio_return(eq_weights, mean_returns)
eq_vol = portfolio_volatility(eq_weights, cov_matrix)
ax.pie(eq_weights, labels=ticker_names, autopct='%1.1f%%', colors=colors,
       startangle=90, explode=[0.02]*len(tickers))
ax.set_title(f'Equal Weight\nReturn: {eq_ret*100:.1f}%, Vol: {eq_vol*100:.1f}%',
             fontsize=12, fontweight='bold')

plt.suptitle('Portfolio Allocation Comparison', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('plots/portfolio_allocations.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/portfolio_allocations.png")

# 3. Risk Parity Comparison
print("3. Risk Parity Analysis...")

# Calculate risk parity weights
rp_result = optimize_risk_parity(cov_matrix.values)
rp_weights = rp_result['weights']
rp_rc = risk_contribution(rp_weights, cov_matrix.values)
rp_ret = portfolio_return(rp_weights, mean_returns)
rp_vol = portfolio_volatility(rp_weights, cov_matrix)

# Max Sharpe risk contributions
ms_rc = risk_contribution(max_sharpe['weights'], cov_matrix.values)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Weight comparison
ax = axes[0]
x = np.arange(len(tickers))
width = 0.25

bars1 = ax.bar(x - width, eq_weights, width, label='Equal Weight', color='steelblue', alpha=0.8)
bars2 = ax.bar(x, rp_weights, width, label='Risk Parity', color='darkorange', alpha=0.8)
bars3 = ax.bar(x + width, max_sharpe['weights'], width, label='Max Sharpe', color='green', alpha=0.8)

ax.set_xlabel('Asset', fontsize=11)
ax.set_ylabel('Weight', fontsize=11)
ax.set_title('Portfolio Weights Comparison', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ticker_names, rotation=45, ha='right')
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

# Risk contribution comparison
ax = axes[1]
bars1 = ax.bar(x - width, np.ones(len(tickers))/len(tickers), width, 
               label='Equal Weight RC', color='steelblue', alpha=0.8)
bars2 = ax.bar(x, rp_rc / rp_rc.sum(), width, 
               label='Risk Parity RC', color='darkorange', alpha=0.8)
bars3 = ax.bar(x + width, ms_rc / ms_rc.sum(), width, 
               label='Max Sharpe RC', color='green', alpha=0.8)

ax.axhline(y=1/len(tickers), color='red', linestyle='--', linewidth=2, 
           label='Target (Equal RC)')

ax.set_xlabel('Asset', fontsize=11)
ax.set_ylabel('Risk Contribution (%)', fontsize=11)
ax.set_title('Risk Contribution Comparison', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ticker_names, rotation=45, ha='right')
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('plots/risk_parity.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/risk_parity.png")

# 4. Cumulative Returns Backtest
print("4. Backtest: Cumulative Returns...")

# Compute portfolio returns
port_returns = pd.DataFrame(index=returns.index)
port_returns['Equal Weight'] = (returns * eq_weights).sum(axis=1)
port_returns['Max Sharpe'] = (returns * max_sharpe['weights']).sum(axis=1)
port_returns['Risk Parity'] = (returns * rp_weights).sum(axis=1)
port_returns['Min Variance'] = (returns * min_var['weights']).sum(axis=1)

# Cumulative returns
cum_returns = (1 + port_returns).cumprod()

fig, ax = plt.subplots(figsize=(14, 8))

colors = {'Equal Weight': 'steelblue', 'Max Sharpe': 'green', 
          'Risk Parity': 'darkorange', 'Min Variance': 'purple'}

for col in cum_returns.columns:
    ax.plot(cum_returns.index, cum_returns[col], label=col, 
            color=colors[col], linewidth=2)

ax.axhline(y=1, color='black', linestyle='--', alpha=0.5)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Cumulative Return ($1 invested)', fontsize=12)
ax.set_title('Portfolio Strategy Backtest (2019-2024)\nIncluding COVID Crash & Recovery', 
             fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)

# Annotate key events
ax.annotate('COVID Crash', xy=(pd.Timestamp('2020-03-23'), cum_returns.loc['2020-03-23'].min()),
            xytext=(pd.Timestamp('2020-06-01'), 0.7),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10, color='red')

plt.tight_layout()
plt.savefig('plots/backtest_cumulative.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/backtest_cumulative.png")

# 5. Drawdown Analysis
print("5. Drawdown Analysis...")

def compute_drawdown(cum_ret):
    running_max = cum_ret.cummax()
    drawdown = (cum_ret - running_max) / running_max
    return drawdown

fig, ax = plt.subplots(figsize=(14, 6))

for col in cum_returns.columns:
    dd = compute_drawdown(cum_returns[col])
    ax.fill_between(dd.index, dd, 0, alpha=0.3, label=col, color=colors[col])
    ax.plot(dd.index, dd, color=colors[col], linewidth=1)

ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Drawdown (%)', fontsize=12)
ax.set_title('Portfolio Drawdowns (2019-2024)', fontsize=14, fontweight='bold')
ax.legend(loc='lower left', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.4, 0.05)

plt.tight_layout()
plt.savefig('plots/drawdowns.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/drawdowns.png")

print("\n" + "="*60)
print("✓ All portfolio-optimization plots generated!")
print("="*60)
plt.close('all')
