"""Generate all visualization plots for monte-carlo-options project."""

import numpy as np
import matplotlib.pyplot as plt
from options.gbm import simulate_gbm
from options.greeks import delta_call, gamma, vega, theta_call
from options.black_scholes import black_scholes_call
from options.european_options import price_european_call, price_european_put

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

print("="*60)
print("MONTE CARLO OPTIONS - GENERATING PLOTS")
print("="*60)

# 1. GBM Paths
print("\n1. GBM Stock Price Paths...")
np.random.seed(42)
S0, mu, sigma, T = 100, 0.08, 0.20, 1.0
n_paths = 30
dt = 1/252
t, paths = simulate_gbm(S0, mu, sigma, T, dt, n_paths)

fig, ax = plt.subplots(figsize=(12, 7))
for i in range(n_paths):
    ax.plot(t, paths[i], alpha=0.6, linewidth=0.8)
ax.axhline(y=S0, color='black', linestyle='--', linewidth=2, label=f'Initial: ${S0}')
ax.set_xlabel('Time (years)', fontsize=12)
ax.set_ylabel('Stock Price ($)', fontsize=12)
ax.set_title('Geometric Brownian Motion: Stock Price Simulation\n(μ=8%, σ=20%, 30 paths)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plots/gbm_paths.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/gbm_paths.png")

# 2. Option Payoff Diagrams
print("2. Option Payoff Diagrams...")
S = np.linspace(50, 150, 200)
K = 100
call_payoff = np.maximum(S - K, 0)
put_payoff = np.maximum(K - S, 0)
call_premium = 10.45  # typical ATM premium
put_premium = 8.05

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Call
ax = axes[0]
ax.plot(S, call_payoff - call_premium, 'b-', linewidth=2.5)
ax.axhline(y=0, color='black', linewidth=1)
ax.axvline(x=K, color='red', linestyle='--', linewidth=1.5, label=f'Strike: ${K}')
ax.fill_between(S, call_payoff - call_premium, 0, 
                where=(call_payoff - call_premium > 0), alpha=0.3, color='green', label='Profit')
ax.fill_between(S, call_payoff - call_premium, 0, 
                where=(call_payoff - call_premium < 0), alpha=0.3, color='red', label='Loss')
ax.set_xlabel('Stock Price at Expiry ($)', fontsize=11)
ax.set_ylabel('Profit/Loss ($)', fontsize=11)
ax.set_title(f'Long Call Option (Premium: ${call_premium:.2f})', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.set_xlim(50, 150)
ax.set_ylim(-20, 40)

# Put
ax = axes[1]
ax.plot(S, put_payoff - put_premium, 'r-', linewidth=2.5)
ax.axhline(y=0, color='black', linewidth=1)
ax.axvline(x=K, color='red', linestyle='--', linewidth=1.5, label=f'Strike: ${K}')
ax.fill_between(S, put_payoff - put_premium, 0, 
                where=(put_payoff - put_premium > 0), alpha=0.3, color='green', label='Profit')
ax.fill_between(S, put_payoff - put_premium, 0, 
                where=(put_payoff - put_premium < 0), alpha=0.3, color='red', label='Loss')
ax.set_xlabel('Stock Price at Expiry ($)', fontsize=11)
ax.set_ylabel('Profit/Loss ($)', fontsize=11)
ax.set_title(f'Long Put Option (Premium: ${put_premium:.2f})', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.set_xlim(50, 150)
ax.set_ylim(-20, 40)

plt.tight_layout()
plt.savefig('plots/option_payoffs.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/option_payoffs.png")

# 3. Greeks vs Spot Price
print("3. Greeks Surface...")
K, T, r, sigma = 100, 0.25, 0.05, 0.20
S = np.linspace(70, 130, 100)

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# Delta
deltas = [delta_call(s, K, T, r, sigma) for s in S]
ax = axes[0, 0]
ax.plot(S, deltas, 'b-', linewidth=2.5)
ax.axvline(x=K, color='red', linestyle='--', alpha=0.7, label='ATM')
ax.fill_between(S, deltas, alpha=0.2)
ax.set_xlabel('Spot Price ($)', fontsize=11)
ax.set_ylabel('Delta (Δ)', fontsize=11)
ax.set_title('Delta: Sensitivity to Spot Price', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Gamma
gammas = [gamma(s, K, T, r, sigma) for s in S]
ax = axes[0, 1]
ax.plot(S, gammas, 'g-', linewidth=2.5)
ax.axvline(x=K, color='red', linestyle='--', alpha=0.7, label='ATM (max Γ)')
ax.fill_between(S, gammas, alpha=0.2, color='green')
ax.set_xlabel('Spot Price ($)', fontsize=11)
ax.set_ylabel('Gamma (Γ)', fontsize=11)
ax.set_title('Gamma: Rate of Delta Change', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Vega
vegas = [vega(s, K, T, r, sigma) for s in S]
ax = axes[1, 0]
ax.plot(S, vegas, 'm-', linewidth=2.5)
ax.axvline(x=K, color='red', linestyle='--', alpha=0.7, label='ATM (max ν)')
ax.fill_between(S, vegas, alpha=0.2, color='magenta')
ax.set_xlabel('Spot Price ($)', fontsize=11)
ax.set_ylabel('Vega (ν)', fontsize=11)
ax.set_title('Vega: Sensitivity to Volatility', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Theta
thetas = [theta_call(s, K, T, r, sigma) for s in S]
ax = axes[1, 1]
ax.plot(S, thetas, 'orange', linewidth=2.5)
ax.axvline(x=K, color='red', linestyle='--', alpha=0.7, label='ATM')
ax.axhline(y=0, color='black', linewidth=0.5)
ax.fill_between(S, thetas, alpha=0.2, color='orange')
ax.set_xlabel('Spot Price ($)', fontsize=11)
ax.set_ylabel('Theta (Θ)', fontsize=11)
ax.set_title('Theta: Time Decay', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/greeks.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/greeks.png")

# 4. MC vs Black-Scholes Convergence
print("4. MC vs Black-Scholes Convergence...")
S0, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20
n_sims_list = [10, 50, 100, 500, 1000, 5000, 10000, 50000]
bs_price = black_scholes_call(S0, K, T, r, sigma)
mc_prices = []
mc_errors = []

np.random.seed(42)
for n in n_sims_list:
    prices = [price_european_call(S0, K, r, sigma, T, n) for _ in range(30)]
    mc_prices.append(np.mean(prices))
    mc_errors.append(np.std(prices))

fig, ax = plt.subplots(figsize=(12, 7))
ax.errorbar(n_sims_list, mc_prices, yerr=mc_errors, fmt='bo-', linewidth=2, 
            markersize=8, capsize=5, label='Monte Carlo ± 1σ')
ax.axhline(y=bs_price, color='red', linestyle='--', linewidth=2.5, 
           label=f'Black-Scholes: ${bs_price:.4f}')
ax.fill_between([n_sims_list[0]*0.8, n_sims_list[-1]*1.2], 
                bs_price - 0.01, bs_price + 0.01, alpha=0.2, color='red')

ax.set_xscale('log')
ax.set_xlabel('Number of Simulations', fontsize=12)
ax.set_ylabel('Option Price ($)', fontsize=12)
ax.set_title('Monte Carlo Convergence to Black-Scholes Price\n(ATM Call, S₀=K=$100, T=0.25y, σ=20%)', 
             fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plots/mc_convergence.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plots/mc_convergence.png")

print("\n" + "="*60)
print("✓ All monte-carlo-options plots generated!")
print("="*60)
plt.close('all')
