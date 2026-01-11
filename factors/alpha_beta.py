"""
Alpha and Beta decomposition analysis.
Performance attribution and risk decomposition.
"""

import numpy as np
import pandas as pd
from factors.ff3_model import FF3Model
from factors.ff5_model import FF5Model
from factors.data_loader import fetch_ff_factors, fetch_stock_returns, align_data


def decompose_returns(ticker, model_type='3', period='5y'):
    """
    Decompose stock returns into systematic and idiosyncratic components.
    
    Total Return = Risk-Free + Factor Returns + Alpha + Residual
    
    Parameters:
    -----------
    ticker : str
        Stock ticker
    model_type : str
        '3' for FF3, '5' for FF5
    period : str
        Data period
    
    Returns:
    --------
    dict : Decomposition results
    """
    # Fetch data
    stock_returns = fetch_stock_returns(ticker, period=period)
    ff_factors = fetch_ff_factors(model=model_type, frequency='daily')
    excess_returns, factors = align_data(stock_returns, ff_factors)
    
    # Fit model
    if model_type == '3':
        model = FF3Model()
        factor_names = ['Mkt-RF', 'SMB', 'HML']
    else:
        model = FF5Model()
        factor_names = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']
    
    model.fit(excess_returns, factors)
    
    # Decompose returns
    n_days = len(excess_returns)
    ann_factor = 252 / n_days
    
    # Risk-free contribution
    rf_contribution = factors['RF'].sum()
    
    # Factor contributions
    factor_contributions = {}
    for factor in factor_names:
        beta = model.betas[factor]
        factor_return = factors[factor].sum()
        contribution = beta * factor_return
        factor_contributions[factor] = contribution
    
    # Alpha contribution
    alpha_contribution = model.alpha * n_days
    
    # Total explained
    explained = rf_contribution + sum(factor_contributions.values()) + alpha_contribution
    
    # Actual total return
    total_return = stock_returns.sum()
    
    # Residual (unexplained)
    residual = total_return - explained
    
    return {
        'ticker': ticker,
        'total_return': total_return,
        'risk_free': rf_contribution,
        'factor_contributions': factor_contributions,
        'alpha': alpha_contribution,
        'residual': residual,
        'model': model,
        'period_days': n_days
    }


def print_decomposition(decomp):
    """Print return decomposition."""
    print("="*60)
    print(f"Return Decomposition: {decomp['ticker']}")
    print("="*60)
    
    total = decomp['total_return'] * 100
    print(f"\nTotal Return: {total:.2f}%")
    print("-"*40)
    
    print(f"\nContributions:")
    print(f"  {'Risk-Free Rate:':<25} {decomp['risk_free']*100:>8.2f}%")
    
    factor_total = 0
    for factor, contrib in decomp['factor_contributions'].items():
        print(f"  {factor + ':':<25} {contrib*100:>8.2f}%")
        factor_total += contrib
    
    print(f"  {'Alpha:':<25} {decomp['alpha']*100:>8.2f}%")
    print(f"  {'Residual:':<25} {decomp['residual']*100:>8.2f}%")
    
    print("-"*40)
    explained = decomp['risk_free'] + factor_total + decomp['alpha']
    print(f"  {'Explained:':<25} {explained*100:>8.2f}%")
    print(f"  {'Total:':<25} {total:>8.2f}%")
    
    # Factor attribution summary
    print("\n" + "-"*60)
    print("Attribution Summary:")
    pct_systematic = factor_total / decomp['total_return'] * 100 if decomp['total_return'] != 0 else 0
    pct_alpha = decomp['alpha'] / decomp['total_return'] * 100 if decomp['total_return'] != 0 else 0
    print(f"  Systematic (factor) return: {pct_systematic:.1f}% of total")
    print(f"  Alpha (skill): {pct_alpha:.1f}% of total")


def risk_decomposition(ticker, model_type='3', period='5y'):
    """
    Decompose portfolio variance into factor and idiosyncratic risk.
    
    Total Variance = Systematic Variance + Idiosyncratic Variance
    """
    # Fetch data
    stock_returns = fetch_stock_returns(ticker, period=period)
    ff_factors = fetch_ff_factors(model=model_type, frequency='daily')
    excess_returns, factors = align_data(stock_returns, ff_factors)
    
    # Fit model
    if model_type == '3':
        model = FF3Model()
        factor_names = ['Mkt-RF', 'SMB', 'HML']
    else:
        model = FF5Model()
        factor_names = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']
    
    model.fit(excess_returns, factors)
    
    # Total variance
    total_var = excess_returns.var()
    
    # Systematic variance (from factors)
    factor_data = factors[factor_names]
    betas = np.array([model.betas[f] for f in factor_names])
    factor_cov = factor_data.cov()
    systematic_var = np.dot(betas.T, np.dot(factor_cov, betas))
    
    # Idiosyncratic variance (residual)
    residuals = excess_returns - model.results.predict()
    idio_var = residuals.var()
    
    # R-squared check
    r_squared = systematic_var / total_var
    
    return {
        'ticker': ticker,
        'total_variance': total_var,
        'systematic_variance': systematic_var,
        'idiosyncratic_variance': idio_var,
        'systematic_pct': systematic_var / total_var * 100,
        'idiosyncratic_pct': idio_var / total_var * 100,
        'total_vol_ann': np.sqrt(total_var * 252) * 100,
        'systematic_vol_ann': np.sqrt(systematic_var * 252) * 100,
        'idiosyncratic_vol_ann': np.sqrt(idio_var * 252) * 100
    }


def print_risk_decomposition(risk_decomp):
    """Print risk decomposition."""
    r = risk_decomp
    
    print("="*60)
    print(f"Risk Decomposition: {r['ticker']}")
    print("="*60)
    
    print(f"\nAnnualized Volatility: {r['total_vol_ann']:.2f}%")
    print("-"*40)
    
    print(f"\nVariance Decomposition:")
    print(f"  {'Systematic (factor):':<25} {r['systematic_pct']:>6.1f}%")
    print(f"  {'Idiosyncratic (specific):':<25} {r['idiosyncratic_pct']:>6.1f}%")
    
    print(f"\nVolatility Decomposition (annualized):")
    print(f"  {'Systematic:':<25} {r['systematic_vol_ann']:>6.2f}%")
    print(f"  {'Idiosyncratic:':<25} {r['idiosyncratic_vol_ann']:>6.2f}%")
    
    print("\n" + "-"*60)
    if r['idiosyncratic_pct'] > 50:
        print("High idiosyncratic risk: Stock-specific factors dominate")
        print("  → Diversification would significantly reduce risk")
    else:
        print("High systematic risk: Market factors dominate")
        print("  → Diversification has limited benefit")


if __name__ == "__main__":
    # Analyze a few stocks
    tickers = ['AAPL', 'XOM', 'JPM']
    
    for ticker in tickers:
        print("\n" + "="*70)
        
        # Return decomposition
        decomp = decompose_returns(ticker, model_type='3', period='3y')
        print_decomposition(decomp)
        
        # Risk decomposition
        risk = risk_decomposition(ticker, model_type='3', period='3y')
        print_risk_decomposition(risk)
