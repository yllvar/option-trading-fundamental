"""
Fetch historical price data for portfolio analysis.
Uses yfinance for free market data access.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def fetch_prices(tickers, start_date=None, end_date=None, period='5y'):
    """
    Fetch adjusted closing prices for a list of tickers.
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
    start_date : str, optional
        Start date in 'YYYY-MM-DD' format
    end_date : str, optional
        End date in 'YYYY-MM-DD' format
    period : str
        Period to fetch if dates not specified ('1y', '5y', '10y', 'max')
    
    Returns:
    --------
    pd.DataFrame : Adjusted closing prices, columns are tickers
    """
    if start_date and end_date:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
    else:
        data = yf.download(tickers, period=period, progress=False)
    
    # Extract adjusted close prices
    if len(tickers) == 1:
        prices = data['Adj Close'].to_frame(tickers[0])
    else:
        prices = data['Adj Close']
    
    # Drop any rows with missing data
    prices = prices.dropna()
    
    return prices


def calculate_returns(prices, method='log'):
    """
    Calculate returns from price data.
    
    Parameters:
    -----------
    prices : pd.DataFrame
        Price data with dates as index
    method : str
        'log' for log returns, 'simple' for arithmetic returns
    
    Returns:
    --------
    pd.DataFrame : Returns
    """
    if method == 'log':
        returns = np.log(prices / prices.shift(1))
    else:
        returns = prices.pct_change()
    
    return returns.dropna()


def get_market_data(market_ticker='^GSPC', period='5y'):
    """
    Fetch market benchmark data (default: S&P 500).
    """
    return fetch_prices([market_ticker], period=period)


def annualize_returns(returns, periods_per_year=252):
    """
    Annualize daily returns.
    """
    mean_daily = returns.mean()
    return mean_daily * periods_per_year


def annualize_volatility(returns, periods_per_year=252):
    """
    Annualize daily volatility.
    """
    daily_vol = returns.std()
    return daily_vol * np.sqrt(periods_per_year)


if __name__ == "__main__":
    # Example: Fetch tech stocks
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    print("Fetching price data...")
    prices = fetch_prices(tickers, period='2y')
    print(f"Fetched {len(prices)} trading days of data")
    print(f"Date range: {prices.index[0].date()} to {prices.index[-1].date()}")
    
    # Calculate returns
    returns = calculate_returns(prices)
    
    # Summary statistics
    print("\nAnnualized Returns:")
    ann_ret = annualize_returns(returns)
    for ticker in tickers:
        print(f"  {ticker}: {ann_ret[ticker]*100:.1f}%")
    
    print("\nAnnualized Volatility:")
    ann_vol = annualize_volatility(returns)
    for ticker in tickers:
        print(f"  {ticker}: {ann_vol[ticker]*100:.1f}%")
    
    print("\nCorrelation Matrix:")
    print(returns.corr().round(2))
