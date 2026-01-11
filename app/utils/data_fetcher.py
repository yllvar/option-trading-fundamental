"""
Data fetching utilities for real market data.
Integrates with yfinance for stock prices and market data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(ticker, start_date=None, end_date=None, period='1y'):
    """
    Fetch stock price data from Yahoo Finance.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    start_date : str or datetime, optional
        Start date
    end_date : str or datetime, optional
        End date
    period : str
        Period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
    --------
    pd.DataFrame : Stock price data
    """
    try:
        import yfinance as yf
        
        if start_date and end_date:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        else:
            data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        # Ensure 'Adj Close' exists for compatibility, or use 'Close'
        if 'Adj Close' not in data.columns and 'Close' in data.columns:
            data['Adj Close'] = data['Close']
            
        return data
    
    except ImportError:
        raise ImportError("yfinance not installed. Install with: pip install yfinance")
    except Exception as e:
        raise Exception(f"Error fetching data for {ticker}: {e}")


@st.cache_data(ttl=3600)
def fetch_multiple_stocks(tickers, start_date=None, end_date=None, period='1y'):
    """
    Fetch data for multiple stocks.
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols
    start_date : str or datetime, optional
        Start date
    end_date : str or datetime, optional
        End date
    period : str
        Period
        
    Returns:
    --------
    pd.DataFrame : Multi-column dataframe with adjusted close prices
    """
    try:
        import yfinance as yf
        
        if start_date and end_date:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)
        else:
            data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
        
        if data.empty:
            # Try fetching one by one if bulk fails
            all_prices = {}
            for t in tickers:
                t_data = yf.download(t, period=period, progress=False, auto_adjust=True)
                if not t_data.empty:
                    all_prices[t] = t_data['Close']
            
            if not all_prices:
                raise ValueError(f"No data found for tickers {tickers}")
            prices = pd.DataFrame(all_prices)
            return prices
        
        # Extract adjusted close prices (Close is adjusted because of auto_adjust=True)
        # Handle both single and multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            if 'Close' in data.columns.levels[0]:
                prices = data['Close']
            elif 'Adj Close' in data.columns.levels[0]:
                prices = data['Adj Close']
            else:
                # Last resort: try to find any price-like column
                alt_cols = ['Close', 'Adj Close', 'Price']
                found = False
                for col in alt_cols:
                    if col in data.columns.levels[0]:
                        prices = data[col]
                        found = True
                        break
                if not found:
                    raise KeyError(f"Could not find price column in {data.columns.levels[0]}")
        else:
            # Single ticker usually returns single level columns
            if 'Close' in data.columns:
                prices = data['Close'].to_frame()
            elif 'Adj Close' in data.columns:
                prices = data['Adj Close'].to_frame()
            else:
                raise KeyError(f"Could not find price column in {data.columns}")
            prices.columns = tickers if len(tickers) == 1 else prices.columns

        return prices
    
    except ImportError:
        raise ImportError("yfinance not installed. Install with: pip install yfinance")
    except Exception as e:
        raise Exception(f"Error fetching data: {e}")


def calculate_returns(prices, method='simple'):
    """
    Calculate returns from price data.
    
    Parameters:
    -----------
    prices : pd.DataFrame or pd.Series
        Price data
    method : str
        'simple' or 'log'
        
    Returns:
    --------
    pd.DataFrame or pd.Series : Returns
    """
    if method == 'simple':
        returns = prices.pct_change()
    elif method == 'log':
        returns = np.log(prices / prices.shift(1))
    else:
        raise ValueError("method must be 'simple' or 'log'")
    
    # Fill small gaps (up to 3 days) and drop remaining NaNs
    returns = returns.ffill(limit=3).dropna(how='any')
    
    return returns


def calculate_statistics(returns):
    """
    Calculate return statistics.
    
    Parameters:
    -----------
    returns : pd.DataFrame or pd.Series
        Return data
        
    Returns:
    --------
    dict : Statistics
    """
    stats = {
        'mean': returns.mean(),
        'std': returns.std(),
        'min': returns.min(),
        'max': returns.max(),
        'skew': returns.skew(),
        'kurt': returns.kurt()
    }
    
    # Annualize (assuming daily data)
    stats['annual_return'] = stats['mean'] * 252
    stats['annual_volatility'] = stats['std'] * np.sqrt(252)
    stats['sharpe'] = stats['annual_return'] / stats['annual_volatility']
    
    return stats


@st.cache_data(ttl=3600)
def get_stock_info(ticker):
    """
    Get stock information.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker
        
    Returns:
    --------
    dict : Stock information
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'beta': info.get('beta', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A')
        }
    
    except ImportError:
        raise ImportError("yfinance not installed")
    except Exception as e:
        return {'error': str(e)}


def estimate_volatility(prices, window=30):
    """
    Estimate historical volatility.
    
    Parameters:
    -----------
    prices : pd.Series
        Price data
    window : int
        Rolling window size
        
    Returns:
    --------
    float : Annualized volatility
    """
    returns = calculate_returns(prices, method='log')
    volatility = returns.rolling(window=window).std().iloc[-1]
    annual_vol = volatility * np.sqrt(252)
    
    return annual_vol


def get_current_price(ticker):
    """
    Get current stock price.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker
        
    Returns:
    --------
    float : Current price
    """
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d')
        
        if data.empty:
            raise ValueError(f"No data for {ticker}")
        
        return data['Close'].iloc[-1]
    
    except ImportError:
        raise ImportError("yfinance not installed")
    except Exception as e:
        raise Exception(f"Error getting price for {ticker}: {e}")


class DataValidator:
    """Validate fetched data."""
    
    @staticmethod
    def validate_ticker(ticker):
        """Check if ticker is valid."""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            return 'regularMarketPrice' in info or 'currentPrice' in info
        except:
            return False
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validate date range."""
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        if end_date > datetime.now():
            raise ValueError("End date cannot be in the future")
        
        return True
    
    @staticmethod
    def check_data_quality(data, min_observations=30):
        """Check data quality."""
        issues = []
        
        if len(data) < min_observations:
            issues.append(f"Insufficient data: {len(data)} < {min_observations}")
        
        if data.isnull().any().any():
            issues.append("Data contains missing values")
        
        if (data == 0).any().any():
            issues.append("Data contains zero values")
        
        return issues if issues else None


# Fallback to synthetic data if yfinance not available
def get_data_with_fallback(ticker, period='1y', use_synthetic=False):
    """
    Get data with fallback to synthetic.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker
    period : str
        Period
    use_synthetic : bool
        Force synthetic data
        
    Returns:
    --------
    pd.DataFrame : Price data
    """
    if use_synthetic:
        return generate_synthetic_prices(ticker, period)
    
    try:
        return fetch_stock_data(ticker, period=period)
    except:
        st.warning(f"Could not fetch real data for {ticker}. Using synthetic data.")
        return generate_synthetic_prices(ticker, period)


def generate_synthetic_prices(ticker, period='1y'):
    """Generate synthetic price data for demonstration."""
    # Parse period
    period_days = {
        '1mo': 30, '3mo': 90, '6mo': 180,
        '1y': 252, '2y': 504, '5y': 1260
    }
    
    n_days = period_days.get(period, 252)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(n_days * 1.4))  # Account for weekends
    dates = pd.bdate_range(start=start_date, end=end_date)[:n_days]
    
    # Generate prices using GBM
    np.random.seed(hash(ticker) % 2**32)
    S0 = 100
    mu = 0.10 / 252  # Daily drift
    sigma = 0.20 / np.sqrt(252)  # Daily volatility
    
    returns = np.random.normal(mu, sigma, n_days)
    prices = S0 * np.exp(np.cumsum(returns))
    
    # Create dataframe
    df = pd.DataFrame({
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, n_days)),
        'High': prices * (1 + np.random.uniform(0, 0.02, n_days)),
        'Low': prices * (1 + np.random.uniform(-0.02, 0, n_days)),
        'Close': prices,
        'Adj Close': prices,
        'Volume': np.random.randint(1000000, 10000000, n_days)
    }, index=dates)
    
    return df
