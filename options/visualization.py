"""
Visualization tools for option pricing analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from options.gbm import simulate_gbm
from options.greeks import delta_call, gamma, vega, theta_call
from options.black_scholes import black_scholes_call


def plot_gbm_paths(S0=100, mu=0.08, sigma=0.20, T=1.0, n_paths=20, n_steps=252):
    """Plot sample GBM paths."""
    paths = simulate_gbm(S0, mu, sigma, T, n_paths, n_steps)
    t = np.linspace(0, T, n_steps)
    
    plt.figure(figsize=(10, 6))
    for i in range(n_paths):
        plt.plot(t, paths[i], alpha=0.7, linewidth=0.8)
    
    plt.axhline(y=S0, color='black', linestyle='--', label=f'Initial: ${S0}')
    plt.xlabel('Time (years)')
    plt.ylabel('Stock Price ($)')
    plt.title(f'GBM Stock Price Paths (μ={mu*100:.0f}%, σ={sigma*100:.0f}%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()


def plot_option_payoff(K=100, option_type='call', premium=None):
    """Plot option payoff diagram."""
    S = np.linspace(50, 150, 200)
    
    if option_type == 'call':
        payoff = np.maximum(S - K, 0)
        title = 'Call Option'
    else:
        payoff = np.maximum(K - S, 0)
        title = 'Put Option'
    
    if premium:
        payoff = payoff - premium
        title += f' (Premium: ${premium:.2f})'
    
    plt.figure(figsize=(10, 6))
    plt.plot(S, payoff, 'b-', linewidth=2)
    plt.axhline(y=0, color='black', linewidth=0.5)
    plt.axvline(x=K, color='red', linestyle='--', label=f'Strike: ${K}')
    
    plt.fill_between(S, payoff, 0, where=(payoff > 0), alpha=0.3, color='green', label='Profit')
    plt.fill_between(S, payoff, 0, where=(payoff < 0), alpha=0.3, color='red', label='Loss')
    
    plt.xlabel('Stock Price at Expiry ($)')
    plt.ylabel('Profit/Loss ($)')
    plt.title(f'{title} Payoff Diagram')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()


def plot_greeks_vs_spot(K=100, T=0.25, r=0.05, sigma=0.20):
    """Plot how Greeks change with spot price."""
    S = np.linspace(70, 130, 100)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Delta
    deltas = [delta_call(s, K, T, r, sigma) for s in S]
    axes[0, 0].plot(S, deltas, 'b-', linewidth=2)
    axes[0, 0].axvline(x=K, color='red', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('Spot Price ($)')
    axes[0, 0].set_ylabel('Delta')
    axes[0, 0].set_title('Delta vs Spot')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Gamma
    gammas = [gamma(s, K, T, r, sigma) for s in S]
    axes[0, 1].plot(S, gammas, 'g-', linewidth=2)
    axes[0, 1].axvline(x=K, color='red', linestyle='--', alpha=0.5)
    axes[0, 1].set_xlabel('Spot Price ($)')
    axes[0, 1].set_ylabel('Gamma')
    axes[0, 1].set_title('Gamma vs Spot')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Vega
    vegas = [vega(s, K, T, r, sigma) for s in S]
    axes[1, 0].plot(S, vegas, 'm-', linewidth=2)
    axes[1, 0].axvline(x=K, color='red', linestyle='--', alpha=0.5)
    axes[1, 0].set_xlabel('Spot Price ($)')
    axes[1, 0].set_ylabel('Vega (per 1% vol)')
    axes[1, 0].set_title('Vega vs Spot')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Theta
    thetas = [theta_call(s, K, T, r, sigma) for s in S]
    axes[1, 1].plot(S, thetas, 'r-', linewidth=2)
    axes[1, 1].axvline(x=K, color='red', linestyle='--', alpha=0.5)
    axes[1, 1].set_xlabel('Spot Price ($)')
    axes[1, 1].set_ylabel('Theta (per day)')
    axes[1, 1].set_title('Theta vs Spot')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle(f'Greeks vs Spot Price (K=${K}, T={T}y, σ={sigma*100:.0f}%)', fontsize=14)
    plt.tight_layout()
    return fig


def plot_convergence(S0=100, K=100, T=0.25, r=0.05, sigma=0.20):
    """Plot Monte Carlo convergence to Black-Scholes price."""
    from options.european_options import price_european_call as monte_carlo_call
    
    bs_price = black_scholes_call(S0, K, T, r, sigma)
    
    path_counts = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000]
    prices = []
    errors = []
    
    for n in path_counts:
        price, std = monte_carlo_call(S0, K, T, r, sigma, n)
        prices.append(price)
        errors.append(1.96 * std)  # 95% CI
    
    plt.figure(figsize=(10, 6))
    plt.errorbar(path_counts, prices, yerr=errors, fmt='o-', capsize=5, label='MC Price ± 95% CI')
    plt.axhline(y=bs_price, color='red', linestyle='--', label=f'Black-Scholes: ${bs_price:.4f}')
    
    plt.xscale('log')
    plt.xlabel('Number of Paths')
    plt.ylabel('Option Price ($)')
    plt.title('Monte Carlo Convergence to Black-Scholes')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()


def plot_implied_vol_smile(strikes, ivs, S0=100, label='Market'):
    """Plot implied volatility smile/skew."""
    plt.figure(figsize=(10, 6))
    
    moneyness = strikes / S0
    plt.plot(moneyness, np.array(ivs) * 100, 'o-', linewidth=2, markersize=8, label=label)
    
    plt.axvline(x=1.0, color='gray', linestyle='--', alpha=0.5, label='ATM')
    plt.xlabel('Moneyness (K/S)')
    plt.ylabel('Implied Volatility (%)')
    plt.title('Implied Volatility Smile')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()


if __name__ == "__main__":
    # Generate all example plots
    print("Generating visualization examples...")
    
    # 1. GBM paths
    fig1 = plot_gbm_paths()
    fig1.savefig('plots/gbm_paths.png', dpi=150)
    print("  Saved: plots/gbm_paths.png")
    
    # 2. Option payoff
    fig2 = plot_option_payoff(K=100, option_type='call', premium=5.50)
    fig2.savefig('plots/call_payoff.png', dpi=150)
    print("  Saved: plots/call_payoff.png")
    
    # 3. Greeks
    fig3 = plot_greeks_vs_spot()
    fig3.savefig('plots/greeks.png', dpi=150)
    print("  Saved: plots/greeks.png")
    
    # 4. Convergence
    fig4 = plot_convergence()
    fig4.savefig('plots/convergence.png', dpi=150)
    print("  Saved: plots/convergence.png")
    
    plt.show()
