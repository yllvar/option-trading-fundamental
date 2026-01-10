# Quant Fundamentals - Complete Documentation

**From-scratch Python implementations of foundational quantitative finance methods**

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Options Pricing](#options-pricing)
5. [Portfolio Optimization](#portfolio-optimization)
6. [Factor Models](#factor-models)
7. [Visualization](#visualization)
8. [API Reference](#api-reference)
9. [Mathematical Background](#mathematical-background)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This repository contains educational implementations of three core quantitative finance domains:

### 🎯 Options Pricing
- **Black-Scholes Model**: Analytical formulas for European options
- **Monte Carlo Simulation**: Numerical pricing with variance reduction
- **Greeks**: Delta, Gamma, Vega, Theta, Rho, Vanna, Volga
- **GBM Simulation**: Geometric Brownian Motion for stock prices

### 📊 Portfolio Optimization
- **Mean-Variance Optimization**: Markowitz (1952) efficient frontier
- **Risk Parity**: Equal risk contribution allocation
- **Backtesting**: Historical performance with rebalancing
- **Efficient Frontier**: Risk-return tradeoff visualization

### 📈 Factor Models
- **Fama-French 3-Factor**: Market, Size, Value
- **Fama-French 5-Factor**: Adds Profitability, Investment
- **Alpha/Beta Decomposition**: Systematic vs idiosyncratic risk

---

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/quant-fundamentals.git
cd quant-fundamentals
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
```
numpy>=1.20.0
pandas>=1.3.0
scipy>=1.7.0
matplotlib>=3.4.0
yfinance>=0.1.70
statsmodels>=0.13.0
requests>=2.26.0
```

### Step 3: Verify Installation
```bash
python -c "import numpy, pandas, scipy, matplotlib, yfinance, statsmodels; print('All dependencies installed!')"
```

---

## Quick Start

### Example 1: Price a Call Option
```python
from options.black_scholes import black_scholes_call
from options.european_options import price_european_call

# Parameters
S0 = 100      # Stock price
K = 100       # Strike (at-the-money)
r = 0.05      # Risk-free rate (5%)
sigma = 0.20  # Volatility (20%)
T = 1.0       # Time to maturity (1 year)

# Analytical price
bs_price = black_scholes_call(S0, K, r, sigma, T)
print(f"Black-Scholes: ${bs_price:.4f}")

# Monte Carlo price
mc_price = price_european_call(S0, K, r, sigma, T, n_paths=100000)
print(f"Monte Carlo: ${mc_price:.4f}")
```

### Example 2: Optimize a Portfolio
```python
from portfolio.markowitz import optimize_sharpe
from portfolio.data_loader import fetch_prices, calculate_returns
import numpy as np

# Fetch data
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
prices = fetch_prices(tickers, period='2y')
returns = calculate_returns(prices)

# Calculate statistics
mean_returns = returns.mean() * 252  # Annualize
cov_matrix = returns.cov() * 252

# Optimize
result = optimize_sharpe(mean_returns, cov_matrix, risk_free_rate=0.02)

print(f"Expected Return: {result['return']*100:.2f}%")
print(f"Volatility: {result['volatility']*100:.2f}%")
print(f"Sharpe Ratio: {result['sharpe']:.3f}")
print("\nWeights:")
for i, ticker in enumerate(tickers):
    print(f"  {ticker}: {result['weights'][i]*100:.1f}%")
```

### Example 3: Analyze Stock with Fama-French
```python
from factors.ff3_model import analyze_stock

# Analyze Apple stock
model = analyze_stock('AAPL', period='5y')

# Results printed automatically:
# - Alpha (annualized)
# - Factor betas (Mkt-RF, SMB, HML)
# - Statistical significance
# - R-squared
# - Interpretation
```

---

## Options Pricing

### Black-Scholes Model

**Analytical formulas for European options**

#### Call Option
```python
from options.black_scholes import black_scholes_call

price = black_scholes_call(
    S0=100,      # Current stock price
    K=105,       # Strike price
    r=0.05,      # Risk-free rate
    sigma=0.25,  # Volatility
    T=0.5        # Time to maturity (years)
)
```

**Formula:**
```
C = S₀N(d₁) - Ke⁻ʳᵀN(d₂)

where:
d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
N(·) = cumulative standard normal distribution
```

#### Put Option
```python
from options.black_scholes import black_scholes_put

price = black_scholes_put(S0, K, r, sigma, T)
```

**Formula:**
```
P = Ke⁻ʳᵀN(-d₂) - S₀N(-d₁)
```

---

### Monte Carlo Simulation

**Numerical pricing using simulated stock paths**

```python
from options.european_options import price_european_call, price_european_put

# Call option
call_price = price_european_call(
    S0=100,
    K=100,
    r=0.05,
    sigma=0.20,
    T=1.0,
    n_paths=100000,  # Number of simulations
    n_steps=252      # Time steps (daily)
)

# Put option
put_price = price_european_put(S0, K, r, sigma, T, n_paths=100000)

# Verify put-call parity: C - P = S₀ - Ke⁻ʳᵀ
import numpy as np
parity_lhs = call_price - put_price
parity_rhs = S0 - K * np.exp(-r * T)
print(f"Put-Call Parity Error: {abs(parity_lhs - parity_rhs):.6f}")
```

**Algorithm:**
1. Simulate stock price paths using GBM
2. Calculate payoff at maturity: max(S_T - K, 0) for calls
3. Discount to present value: e⁻ʳᵀ × E[payoff]

---

### Geometric Brownian Motion

**Simulate stock price paths**

```python
from options.gbm import simulate_gbm

t, S = simulate_gbm(
    S0=100,       # Initial price
    mu=0.08,      # Drift (expected return)
    sigma=0.20,   # Volatility
    T=1.0,        # Time horizon
    dt=1/252,     # Time step (daily)
    n_paths=1000  # Number of paths
)

# S is array of shape (n_paths, n_steps+1)
# Each row is one simulated path
```

**Stochastic Differential Equation:**
```
dS = μS dt + σS dW

Exact solution:
S(t+dt) = S(t) × exp[(μ - σ²/2)dt + σ√dt × Z]

where Z ~ N(0,1)
```

---

### Greeks

**Option sensitivities to market parameters**

```python
from options.greeks import (
    delta_call, delta_put,
    gamma,
    vega,
    theta_call, theta_put,
    rho_call, rho_put,
    vanna, volga
)

S, K, T, r, sigma = 100, 100, 0.25, 0.05, 0.20

# First-order Greeks
print(f"Delta (call): {delta_call(S, K, T, r, sigma):.4f}")
print(f"Delta (put):  {delta_put(S, K, T, r, sigma):.4f}")
print(f"Vega:         ${vega(S, K, T, r, sigma):.4f} per 1% vol")
print(f"Theta (call): ${theta_call(S, K, T, r, sigma):.4f} per day")
print(f"Rho (call):   ${rho_call(S, K, T, r, sigma):.4f} per 1% rate")

# Second-order Greeks
print(f"Gamma:        {gamma(S, K, T, r, sigma):.6f}")
print(f"Vanna:        {vanna(S, K, T, r, sigma):.6f}")
print(f"Volga:        {volga(S, K, T, r, sigma):.6f}")
```

**Definitions:**
- **Delta (Δ)**: ∂C/∂S - Rate of change with respect to spot price
- **Gamma (Γ)**: ∂²C/∂S² - Rate of change of delta
- **Vega (ν)**: ∂C/∂σ - Sensitivity to volatility
- **Theta (Θ)**: ∂C/∂t - Time decay
- **Rho (ρ)**: ∂C/∂r - Sensitivity to interest rate
- **Vanna**: ∂²C/∂S∂σ - Cross-sensitivity (spot × vol)
- **Volga**: ∂²C/∂σ² - Convexity in volatility

---

### Variance Reduction Techniques

**Improve Monte Carlo efficiency**

⚠️ **Note:** Current implementation has import errors. See AUDIT_REPORT.md for fixes.

#### Antithetic Variates
```python
from options.variance_reduction import antithetic_variates_call

price, std_error, variance_reduction = antithetic_variates_call(
    S0=100, K=100, T=0.25, r=0.05, sigma=0.20, n_paths=100000
)

print(f"Price: ${price:.4f}")
print(f"Standard Error: ${std_error:.6f}")
print(f"Variance Reduction: {variance_reduction:.1f}x")
```

**Method:** For each random path Z, also compute path with -Z. Average the two payoffs.

**Benefit:** ~2x variance reduction (50% reduction in standard error)

#### Control Variates
```python
from options.variance_reduction import control_variates_call

price, std_error, variance_reduction = control_variates_call(
    S0=100, K=100, T=0.25, r=0.05, sigma=0.20, n_paths=100000
)
```

**Method:** Use S_T as control variate (known expectation: S₀e^(rT))

**Benefit:** ~3-5x variance reduction

#### Importance Sampling
```python
from options.variance_reduction import importance_sampling_call

# Best for deep out-of-the-money options
price, std_error = importance_sampling_call(
    S0=100, K=130, T=0.25, r=0.05, sigma=0.20, 
    n_paths=100000, shift=1.0
)
```

**Method:** Shift drift to sample payoff region more frequently, then reweight

**Benefit:** Significant for deep OTM options where standard MC is inefficient

---

## Portfolio Optimization

### Mean-Variance Optimization (Markowitz)

**Find optimal portfolio weights**

```python
from portfolio.markowitz import (
    optimize_sharpe,
    optimize_min_variance,
    optimize_target_return
)
import numpy as np

# Example: 5 assets
mean_returns = np.array([0.12, 0.10, 0.14, 0.08, 0.11])  # Annualized
cov_matrix = np.array([...])  # 5x5 covariance matrix

# Maximum Sharpe ratio portfolio
max_sharpe = optimize_sharpe(
    mean_returns, 
    cov_matrix, 
    risk_free_rate=0.02,
    allow_short=False  # Long-only constraint
)

print(f"Expected Return: {max_sharpe['return']*100:.2f}%")
print(f"Volatility: {max_sharpe['volatility']*100:.2f}%")
print(f"Sharpe Ratio: {max_sharpe['sharpe']:.3f}")
print(f"Weights: {max_sharpe['weights']}")

# Minimum variance portfolio
min_var = optimize_min_variance(mean_returns, cov_matrix)

# Target return portfolio (for efficient frontier)
weights, vol = optimize_target_return(
    mean_returns, cov_matrix, target_return=0.10
)
```

**Optimization Problem:**
```
Maximize: (E[R_p] - R_f) / σ_p

Subject to:
- Σw_i = 1 (weights sum to 1)
- w_i ≥ 0 (long-only, optional)

where:
E[R_p] = w^T μ (expected return)
σ_p = √(w^T Σ w) (portfolio volatility)
```

---

### Risk Parity

**Equal risk contribution allocation**

```python
from portfolio.risk_parity import (
    optimize_risk_parity,
    risk_contribution_pct,
    compare_allocations
)

# Optimize for equal risk contribution
result = optimize_risk_parity(cov_matrix)

print(f"Weights: {result['weights']}")
print(f"Risk Contributions: {result['risk_contributions']}")
print(f"Volatility: {result['volatility']*100:.2f}%")

# Verify equal risk contribution
rc = result['risk_contributions']
print(f"Risk Contribution Std: {np.std(rc)*100:.4f}%")  # Should be near 0

# Compare with other strategies
results = compare_allocations(mean_returns, cov_matrix)
for strategy, data in results.items():
    print(f"{strategy}: Return={data['return']*100:.1f}%, "
          f"Vol={data['volatility']*100:.1f}%, "
          f"Sharpe={data['sharpe']:.2f}")
```

**Objective:**
```
Minimize: Σ(RC_i - RC_target)²

where:
RC_i = w_i × (Σw)_i / σ_p (risk contribution of asset i)
RC_target = 1/n (equal contribution)
```

**Strategies Compared:**
1. Equal Weight (1/n)
2. Inverse Volatility (1/σ_i)
3. Risk Parity (equal RC)
4. Max Sharpe
5. Min Variance

---

### Backtesting

**Test strategies on historical data**

```python
from portfolio.backtesting import run_backtest, plot_backtest_results
import matplotlib.pyplot as plt

# Define universe
tickers = ['SPY', 'AGG', 'GLD', 'VNQ', 'EFA']

# Run backtest
results = run_backtest(
    tickers,
    start_date='2018-01-01',
    end_date='2023-12-31',
    strategies=['equal_weight', 'risk_parity', 'max_sharpe', 'min_variance'],
    rebalance_freq='M',  # Monthly rebalancing
    lookback=252         # 1 year lookback for optimization
)

# Print metrics
for strategy, data in results.items():
    metrics = data['metrics']
    print(f"{strategy}:")
    print(f"  Ann. Return: {metrics['ann_return']*100:.1f}%")
    print(f"  Ann. Vol: {metrics['ann_volatility']*100:.1f}%")
    print(f"  Sharpe: {metrics['sharpe']:.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown']*100:.1f}%")
    print(f"  Calmar: {metrics['calmar']:.2f}")

# Plot results
fig = plot_backtest_results(results, tickers)
plt.show()
```

**Rebalancing Frequencies:**
- `'D'` - Daily
- `'W'` - Weekly
- `'M'` - Monthly (recommended)
- `'Q'` - Quarterly
- `'Y'` - Yearly
- `None` - Buy and hold

**Performance Metrics:**
- **Annualized Return**: Geometric mean return
- **Annualized Volatility**: Standard deviation of returns
- **Sharpe Ratio**: (Return - RiskFree) / Volatility
- **Max Drawdown**: Largest peak-to-trough decline
- **Calmar Ratio**: Return / Max Drawdown

---

## Factor Models

### Fama-French 3-Factor Model

**Decompose returns into systematic factors**

```python
from factors.ff3_model import FF3Model, analyze_stock

# Quick analysis
model = analyze_stock('AAPL', period='5y')

# Manual fitting
from factors.data_loader import fetch_stock_returns, fetch_ff_factors, align_data

# Fetch data
stock_returns = fetch_stock_returns('AAPL', period='5y')
ff_factors = fetch_ff_factors(model='3', frequency='daily')

# Align on common dates
excess_returns, factors = align_data(stock_returns, ff_factors)

# Fit model
model = FF3Model()
model.fit(excess_returns, factors)

# Get results
summary = model.summary(annualize=True)
print(f"Alpha: {summary['alpha']*100:.2f}%")
print(f"Market Beta: {summary['betas']['Mkt-RF']:.3f}")
print(f"SMB Beta: {summary['betas']['SMB']:.3f}")
print(f"HML Beta: {summary['betas']['HML']:.3f}")
print(f"R-squared: {summary['r_squared']:.4f}")

# Print formatted summary
model.print_summary('AAPL')
```

**Regression Model:**
```
R_i - R_f = α + β_mkt(R_m - R_f) + β_smb(SMB) + β_hml(HML) + ε

Factors:
- Mkt-RF: Market risk premium (market return - risk-free rate)
- SMB: Small Minus Big (size factor)
- HML: High Minus Low (value factor)
```

**Interpretation:**
- **α (Alpha)**: Excess return not explained by factors (skill/luck)
  - Positive & significant → Outperformance
  - Negative & significant → Underperformance
  
- **β_mkt (Market Beta)**: Systematic risk
  - β > 1: More volatile than market (aggressive)
  - β < 1: Less volatile than market (defensive)
  - β ≈ 1: Similar to market
  
- **β_smb (Size Beta)**: 
  - Positive: Small-cap exposure
  - Negative: Large-cap exposure
  
- **β_hml (Value Beta)**:
  - Positive: Value stock characteristics
  - Negative: Growth stock characteristics

---

### Fama-French 5-Factor Model

**Extended model with profitability and investment factors**

```python
from factors.ff5_model import FF5Model, compare_ff3_ff5

# Compare FF3 vs FF5
ff3_model, ff5_model = compare_ff3_ff5('AAPL', period='5y')

# Manual fitting
from factors.data_loader import fetch_ff_factors

ff5_factors = fetch_ff_factors(model='5', frequency='daily')
excess_returns, factors = align_data(stock_returns, ff5_factors)

model = FF5Model()
model.fit(excess_returns, factors)

summary = model.summary()
print(f"RMW Beta: {summary['betas']['RMW']:.3f}")  # Profitability
print(f"CMA Beta: {summary['betas']['CMA']:.3f}")  # Investment
print(f"R-squared: {summary['r_squared']:.4f}")
```

**Additional Factors:**
- **RMW**: Robust Minus Weak (profitability factor)
  - Positive: High profitability exposure (quality)
  - Negative: Low profitability exposure
  
- **CMA**: Conservative Minus Aggressive (investment factor)
  - Positive: Conservative investment (low capex)
  - Negative: Aggressive investment (high capex)

**Model Comparison:**
```python
# Compare R-squared improvement
r2_improvement = ff5_summary['r_squared'] - ff3_summary['r_squared']
print(f"R² improvement: {r2_improvement*100:.2f}%")

# Typically 1-3% improvement for most stocks
```

---

## Visualization

### Generate All Plots

```bash
# Options plots
cd options
python generate_plots.py

# Portfolio plots
cd ../portfolio
python generate_plots.py

# Factor plots
cd ../factors
python generate_plots.py
```

**Generated plots:**
- `plots/options/gbm_paths.png` - Stock price simulations
- `plots/options/option_payoffs.png` - Call/put payoff diagrams
- `plots/options/greeks.png` - Greeks vs spot price
- `plots/options/mc_convergence.png` - MC convergence analysis
- `plots/portfolio/efficient_frontier.png` - Risk-return tradeoff
- `plots/portfolio/risk_parity.png` - Risk contribution comparison
- `plots/portfolio/backtest_cumulative.png` - Strategy performance
- `plots/portfolio/drawdowns.png` - Drawdown analysis
- `plots/factors/factor_betas.png` - Factor exposures
- `plots/factors/return_decomposition.png` - Alpha vs factor returns
- `plots/factors/model_fit.png` - Actual vs predicted returns

---

## API Reference

### Options Module

#### `black_scholes.py`
```python
black_scholes_call(S0, K, r, sigma, T) -> float
black_scholes_put(S0, K, r, sigma, T) -> float
```

#### `european_options.py`
```python
price_european_call(S0, K, r, sigma, T, n_paths=10000, n_steps=252) -> float
price_european_put(S0, K, r, sigma, T, n_paths=10000, n_steps=252) -> float
```

#### `gbm.py`
```python
simulate_gbm(S0, mu, sigma, T, dt, n_paths) -> (time_array, price_array)
```

#### `greeks.py`
```python
delta_call(S, K, T, r, sigma) -> float
delta_put(S, K, T, r, sigma) -> float
gamma(S, K, T, r, sigma) -> float
vega(S, K, T, r, sigma) -> float  # Per 1% vol change
theta_call(S, K, T, r, sigma) -> float  # Per day
theta_put(S, K, T, r, sigma) -> float
rho_call(S, K, T, r, sigma) -> float  # Per 1% rate change
rho_put(S, K, T, r, sigma) -> float
vanna(S, K, T, r, sigma) -> float
volga(S, K, T, r, sigma) -> float
```

### Portfolio Module

#### `markowitz.py`
```python
optimize_sharpe(mean_returns, cov_matrix, risk_free_rate=0.02, allow_short=False) -> dict
optimize_min_variance(mean_returns, cov_matrix, allow_short=False) -> dict
optimize_target_return(mean_returns, cov_matrix, target_return, allow_short=False) -> (weights, volatility)
portfolio_return(weights, mean_returns) -> float
portfolio_volatility(weights, cov_matrix) -> float
portfolio_sharpe(weights, mean_returns, cov_matrix, risk_free_rate=0.02) -> float
```

#### `risk_parity.py`
```python
optimize_risk_parity(cov_matrix, target_risk=None) -> dict
risk_contribution(weights, cov_matrix) -> array
risk_contribution_pct(weights, cov_matrix) -> array
inverse_volatility_weights(cov_matrix) -> array
compare_allocations(mean_returns, cov_matrix, risk_free_rate=0.02) -> dict
```

#### `backtesting.py`
```python
backtest_portfolio(prices, weights, rebalance_freq='M') -> pd.Series
calculate_metrics(portfolio_value, risk_free_rate=0.02) -> dict
run_backtest(tickers, start_date, end_date, strategies=None, rebalance_freq='M', lookback=252) -> dict
plot_backtest_results(results, tickers=None, save_path=None) -> Figure
```

#### `data_loader.py`
```python
fetch_prices(tickers, start_date=None, end_date=None, period='5y') -> pd.DataFrame
calculate_returns(prices, method='log') -> pd.DataFrame
annualize_returns(returns, periods_per_year=252) -> pd.Series
annualize_volatility(returns, periods_per_year=252) -> pd.Series
```

### Factors Module

#### `ff3_model.py`
```python
class FF3Model:
    fit(excess_returns, factor_data) -> self
    summary(annualize=True) -> dict
    predict(factor_data) -> array
    print_summary(ticker='Stock') -> None

analyze_stock(ticker, period='5y') -> FF3Model
```

#### `ff5_model.py`
```python
class FF5Model:
    fit(excess_returns, factor_data) -> self
    summary(annualize=True) -> dict
    print_summary(ticker='Stock') -> None

compare_ff3_ff5(ticker, period='5y') -> (FF3Model, FF5Model)
```

#### `data_loader.py`
```python
fetch_ff_factors(model='3', frequency='daily') -> pd.DataFrame
fetch_stock_returns(ticker, start_date=None, end_date=None, period='5y') -> pd.Series
align_data(stock_returns, factor_data) -> (excess_returns, factors_aligned)
generate_synthetic_factors(model='3', frequency='daily', years=5) -> pd.DataFrame
```

---

## Mathematical Background

### Black-Scholes PDE

**Partial Differential Equation:**
```
∂V/∂t + ½σ²S²∂²V/∂S² + rS∂V/∂S - rV = 0
```

**Assumptions:**
1. Frictionless markets (no transaction costs)
2. Constant risk-free rate and volatility
3. Log-normal stock price distribution
4. No dividends
5. European exercise only

**Solution for Call:**
```
C(S,t) = SN(d₁) - Ke⁻ʳ⁽ᵀ⁻ᵗ⁾N(d₂)

d₁ = [ln(S/K) + (r + σ²/2)(T-t)] / [σ√(T-t)]
d₂ = d₁ - σ√(T-t)
```

### Modern Portfolio Theory

**Mean-Variance Framework:**

Portfolio return:
```
E[R_p] = Σw_i E[R_i] = w^T μ
```

Portfolio variance:
```
Var(R_p) = Σ Σ w_i w_j Cov(R_i, R_j) = w^T Σ w
```

**Sharpe Ratio:**
```
SR = (E[R_p] - R_f) / σ_p
```

**Efficient Frontier:**
Set of portfolios that maximize return for given risk level, or minimize risk for given return level.

### Risk Parity

**Risk Contribution:**
```
RC_i = w_i × (Σw)_i / σ_p

where (Σw)_i is the i-th element of Σw (marginal contribution to risk)
```

**Objective:**
```
Minimize: Σ(RC_i - 1/n)²

Subject to: Σw_i = 1, w_i > 0
```

### Fama-French Models

**FF3 Regression:**
```
R_i,t - R_f,t = α_i + β_i,mkt(R_m,t - R_f,t) + β_i,smb SMB_t + β_i,hml HML_t + ε_i,t
```

**FF5 Regression:**
```
R_i,t - R_f,t = α_i + β_i,mkt MKT_t + β_i,smb SMB_t + β_i,hml HML_t 
                + β_i,rmw RMW_t + β_i,cma CMA_t + ε_i,t
```

**Factor Construction:**
- **SMB**: Return of small-cap portfolio minus large-cap portfolio
- **HML**: Return of high book-to-market minus low book-to-market
- **RMW**: Return of robust profitability minus weak profitability
- **CMA**: Return of conservative investment minus aggressive investment

---

## Troubleshooting

### Common Issues

#### 1. Import Errors in `variance_reduction.py`
**Error:**
```
ImportError: cannot import name 'monte_carlo_call' from 'european_options'
```

**Fix:**
```python
# Option A: Update imports
from european_options import price_european_call as monte_carlo_call

# Option B: Rename functions in european_options.py
def monte_carlo_call(...):  # Instead of price_european_call
```

#### 2. Missing Dependencies
**Error:**
```
ModuleNotFoundError: No module named 'statsmodels'
```

**Fix:**
```bash
pip install statsmodels requests
```

#### 3. Data Fetching Failures
**Error:**
```
Error fetching data: ...
Using synthetic data for demonstration...
```

**Cause:** Network issues or API rate limits

**Fix:**
- Check internet connection
- Wait and retry (Ken French library may be temporarily unavailable)
- Synthetic data is automatically used as fallback

#### 4. Optimization Failures
**Error:**
```
Optimization terminated successfully, but result.success = False
```

**Cause:** Infeasible constraints (e.g., target return too high)

**Fix:**
- Reduce target return
- Check if covariance matrix is positive definite
- Increase bounds on weights

#### 5. Singular Matrix Errors
**Error:**
```
LinAlgError: Singular matrix
```

**Cause:** Perfectly correlated assets or insufficient data

**Fix:**
- Remove highly correlated assets
- Increase data period
- Add small regularization to covariance matrix:
```python
cov_matrix += np.eye(n) * 1e-8
```

### Performance Tips

1. **Monte Carlo Simulations:**
   - Use variance reduction for better accuracy
   - Start with 10,000 paths for testing
   - Use 100,000+ paths for production

2. **Portfolio Optimization:**
   - Use monthly rebalancing (good tradeoff)
   - Lookback period: 1-3 years (252-756 days)
   - Regularize covariance matrix for stability

3. **Factor Models:**
   - Use at least 3 years of data
   - Daily frequency preferred for accuracy
   - Check for statistical significance (p < 0.05)

---

## Contributing

### Code Style
- Follow PEP 8
- Use type hints where applicable
- Add docstrings to all functions
- Include mathematical formulas in comments

### Testing
```bash
pytest tests/
```

### Adding New Features
1. Create feature branch
2. Implement with tests
3. Update documentation
4. Submit pull request

---

## License

MIT License - See LICENSE file for details

---

## References

### Academic Papers
1. Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
2. Markowitz, H. (1952). "Portfolio Selection"
3. Fama, E. F., & French, K. R. (1993). "Common risk factors in the returns on stocks and bonds"
4. Fama, E. F., & French, K. R. (2015). "A five-factor asset pricing model"

### Data Sources
- Ken French Data Library: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- Yahoo Finance: https://finance.yahoo.com

### Further Reading
- Hull, J. C. (2018). "Options, Futures, and Other Derivatives"
- Bodie, Z., Kane, A., & Marcus, A. J. (2018). "Investments"
- Grinold, R. C., & Kahn, R. N. (2000). "Active Portfolio Management"

---

**Last Updated:** January 10, 2026
