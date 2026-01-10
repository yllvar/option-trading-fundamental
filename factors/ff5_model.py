"""
Fama-French 5-Factor Model Implementation.
Extends FF3 with profitability (RMW) and investment (CMA) factors.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from data_loader import fetch_ff_factors, fetch_stock_returns, align_data


class FF5Model:
    """
    Fama-French 5-Factor Model.
    
    Factors:
    - Mkt-RF: Market risk premium
    - SMB: Small Minus Big (size)
    - HML: High Minus Low (value)
    - RMW: Robust Minus Weak (profitability)
    - CMA: Conservative Minus Aggressive (investment)
    """
    
    def __init__(self):
        self.model = None
        self.results = None
        self.alpha = None
        self.betas = None
        self.r_squared = None
        self.factor_names = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']
    
    def fit(self, excess_returns, factor_data):
        """
        Fit the 5-factor model using OLS regression.
        """
        X = factor_data[self.factor_names]
        y = excess_returns
        
        X = sm.add_constant(X)
        
        self.model = sm.OLS(y, X)
        self.results = self.model.fit()
        
        self.alpha = self.results.params['const']
        self.betas = {
            factor: self.results.params[factor] 
            for factor in self.factor_names
        }
        self.r_squared = self.results.rsquared
        self.adj_r_squared = self.results.rsquared_adj
        
        return self
    
    def summary(self, annualize=True):
        """Return model summary statistics."""
        if self.results is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        ann_factor = 252 if annualize else 1
        
        return {
            'alpha': self.alpha * ann_factor,
            'alpha_t_stat': self.results.tvalues['const'],
            'alpha_p_value': self.results.pvalues['const'],
            'betas': self.betas,
            'beta_t_stats': {
                factor: self.results.tvalues[factor] 
                for factor in self.factor_names
            },
            'beta_p_values': {
                factor: self.results.pvalues[factor] 
                for factor in self.factor_names
            },
            'r_squared': self.r_squared,
            'adj_r_squared': self.adj_r_squared,
            'observations': self.results.nobs
        }
    
    def print_summary(self, ticker='Stock'):
        """Print formatted summary."""
        s = self.summary()
        
        print("="*60)
        print(f"Fama-French 5-Factor Model: {ticker}")
        print("="*60)
        
        print(f"\nAlpha (annualized): {s['alpha']*100:.2f}%")
        print(f"  t-stat: {s['alpha_t_stat']:.2f}, p-value: {s['alpha_p_value']:.4f}")
        
        print(f"\nFactor Betas:")
        print(f"  {'Factor':<10} {'Beta':>10} {'t-stat':>10} {'p-value':>10}")
        print("-"*45)
        for factor in self.factor_names:
            beta = s['betas'][factor]
            t = s['beta_t_stats'][factor]
            p = s['beta_p_values'][factor]
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
            print(f"  {factor:<10} {beta:>10.3f} {t:>10.2f} {p:>10.4f} {sig}")
        
        print(f"\nR-squared: {s['r_squared']:.4f}")
        print(f"Adjusted R-squared: {s['adj_r_squared']:.4f}")
        
        # Interpretation of new factors
        print("\n" + "-"*60)
        print("Factor Interpretation:")
        
        rmw_beta = s['betas']['RMW']
        if rmw_beta > 0.2:
            print(f"  • RMW Beta={rmw_beta:.2f}: High profitability exposure (quality)")
        elif rmw_beta < -0.2:
            print(f"  • RMW Beta={rmw_beta:.2f}: Low profitability exposure")
        
        cma_beta = s['betas']['CMA']
        if cma_beta > 0.2:
            print(f"  • CMA Beta={cma_beta:.2f}: Conservative investment (low capex)")
        elif cma_beta < -0.2:
            print(f"  • CMA Beta={cma_beta:.2f}: Aggressive investment (high capex)")


def compare_ff3_ff5(ticker, period='5y'):
    """
    Compare FF3 and FF5 model results for a stock.
    """
    from ff3_model import FF3Model
    
    print(f"Fetching data for {ticker}...")
    stock_returns = fetch_stock_returns(ticker, period=period)
    
    # FF3 data
    ff3_factors = fetch_ff_factors(model='3', frequency='daily')
    excess_3, factors_3 = align_data(stock_returns, ff3_factors)
    
    # FF5 data
    ff5_factors = fetch_ff_factors(model='5', frequency='daily')
    excess_5, factors_5 = align_data(stock_returns, ff5_factors)
    
    # Fit models
    ff3 = FF3Model()
    ff3.fit(excess_3, factors_3)
    
    ff5 = FF5Model()
    ff5.fit(excess_5, factors_5)
    
    # Compare
    print("="*60)
    print(f"Model Comparison: {ticker}")
    print("="*60)
    
    s3 = ff3.summary()
    s5 = ff5.summary()
    
    print(f"\n{'Metric':<25} {'FF3':>15} {'FF5':>15}")
    print("-"*55)
    print(f"{'Alpha (annualized)':<25} {s3['alpha']*100:>14.2f}% {s5['alpha']*100:>14.2f}%")
    print(f"{'Alpha t-stat':<25} {s3['alpha_t_stat']:>15.2f} {s5['alpha_t_stat']:>15.2f}")
    print(f"{'R-squared':<25} {s3['r_squared']:>15.4f} {s5['r_squared']:>15.4f}")
    print(f"{'Adj R-squared':<25} {s3['adj_r_squared']:>15.4f} {s5['adj_r_squared']:>15.4f}")
    
    print(f"\n{'Factor Betas:':<25}")
    print(f"{'  Mkt-RF':<25} {s3['betas']['Mkt-RF']:>15.3f} {s5['betas']['Mkt-RF']:>15.3f}")
    print(f"{'  SMB':<25} {s3['betas']['SMB']:>15.3f} {s5['betas']['SMB']:>15.3f}")
    print(f"{'  HML':<25} {s3['betas']['HML']:>15.3f} {s5['betas']['HML']:>15.3f}")
    print(f"{'  RMW':<25} {'N/A':>15} {s5['betas']['RMW']:>15.3f}")
    print(f"{'  CMA':<25} {'N/A':>15} {s5['betas']['CMA']:>15.3f}")
    
    # Test if FF5 is significantly better
    r2_improvement = s5['r_squared'] - s3['r_squared']
    print(f"\nR² improvement from FF3 to FF5: {r2_improvement*100:.2f}%")
    
    return ff3, ff5


if __name__ == "__main__":
    # Compare models for tech stocks
    for ticker in ['AAPL', 'MSFT', 'JPM']:
        compare_ff3_ff5(ticker, period='3y')
        print("\n")
