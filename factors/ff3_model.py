"""
Fama-French 3-Factor Model Implementation.
R_i - R_f = α + β_mkt(R_m - R_f) + β_smb(SMB) + β_hml(HML) + ε
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from data_loader import fetch_ff_factors, fetch_stock_returns, align_data


class FF3Model:
    """
    Fama-French 3-Factor Model.
    
    Factors:
    - Mkt-RF: Market risk premium (market return minus risk-free rate)
    - SMB: Small Minus Big (size factor)
    - HML: High Minus Low (value factor)
    """
    
    def __init__(self):
        self.model = None
        self.results = None
        self.alpha = None
        self.betas = None
        self.r_squared = None
        self.factor_names = ['Mkt-RF', 'SMB', 'HML']
    
    def fit(self, excess_returns, factor_data):
        """
        Fit the 3-factor model using OLS regression.
        
        Parameters:
        -----------
        excess_returns : pd.Series
            Stock excess returns (R_i - R_f)
        factor_data : pd.DataFrame
            Factor returns (must contain Mkt-RF, SMB, HML)
        
        Returns:
        --------
        self
        """
        # Extract factors
        X = factor_data[self.factor_names]
        y = excess_returns
        
        # Add constant for alpha
        X = sm.add_constant(X)
        
        # OLS regression
        self.model = sm.OLS(y, X)
        self.results = self.model.fit()
        
        # Extract coefficients
        self.alpha = self.results.params['const']
        self.betas = {
            factor: self.results.params[factor] 
            for factor in self.factor_names
        }
        self.r_squared = self.results.rsquared
        self.adj_r_squared = self.results.rsquared_adj
        
        return self
    
    def summary(self, annualize=True):
        """
        Return model summary statistics.
        """
        if self.results is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        ann_factor = 252 if annualize else 1
        
        summary = {
            'alpha': self.alpha * ann_factor,  # Annualized alpha
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
        
        return summary
    
    def predict(self, factor_data):
        """
        Predict expected excess returns given factor values.
        """
        if self.results is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X = factor_data[self.factor_names]
        X = sm.add_constant(X)
        
        return self.results.predict(X)
    
    def print_summary(self, ticker='Stock'):
        """
        Print formatted summary.
        """
        s = self.summary()
        
        print("="*60)
        print(f"Fama-French 3-Factor Model: {ticker}")
        print("="*60)
        
        print(f"\nAlpha (annualized): {s['alpha']*100:.2f}%")
        print(f"  t-stat: {s['alpha_t_stat']:.2f}")
        print(f"  p-value: {s['alpha_p_value']:.4f}")
        sig = "***" if s['alpha_p_value'] < 0.01 else "**" if s['alpha_p_value'] < 0.05 else "*" if s['alpha_p_value'] < 0.10 else ""
        print(f"  Significance: {sig}")
        
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
        print(f"Observations: {int(s['observations'])}")
        
        # Interpretation
        print("\n" + "-"*60)
        print("Interpretation:")
        
        mkt_beta = s['betas']['Mkt-RF']
        if mkt_beta > 1.1:
            print(f"  • Market Beta={mkt_beta:.2f}: More volatile than market (aggressive)")
        elif mkt_beta < 0.9:
            print(f"  • Market Beta={mkt_beta:.2f}: Less volatile than market (defensive)")
        else:
            print(f"  • Market Beta={mkt_beta:.2f}: Similar volatility to market")
        
        smb_beta = s['betas']['SMB']
        if smb_beta > 0.2:
            print(f"  • SMB Beta={smb_beta:.2f}: Positive size tilt (small-cap exposure)")
        elif smb_beta < -0.2:
            print(f"  • SMB Beta={smb_beta:.2f}: Negative size tilt (large-cap exposure)")
        
        hml_beta = s['betas']['HML']
        if hml_beta > 0.2:
            print(f"  • HML Beta={hml_beta:.2f}: Value stock characteristics")
        elif hml_beta < -0.2:
            print(f"  • HML Beta={hml_beta:.2f}: Growth stock characteristics")


def analyze_stock(ticker, period='5y'):
    """
    Convenience function to run FF3 analysis on a stock.
    """
    # Fetch data
    print(f"Fetching data for {ticker}...")
    stock_returns = fetch_stock_returns(ticker, period=period)
    ff_factors = fetch_ff_factors(model='3', frequency='daily')
    
    # Align data
    excess_returns, factors = align_data(stock_returns, ff_factors)
    print(f"Analysis period: {excess_returns.index[0].date()} to {excess_returns.index[-1].date()}")
    print(f"Observations: {len(excess_returns)}")
    
    # Fit model
    model = FF3Model()
    model.fit(excess_returns, factors)
    model.print_summary(ticker)
    
    return model


if __name__ == "__main__":
    # Example: Analyze Apple stock
    model = analyze_stock('AAPL', period='5y')
