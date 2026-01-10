"""
Fetch Fama-French factor data from Ken French's data library.
"""

import pandas as pd
import numpy as np
from io import StringIO
import requests
from zipfile import ZipFile
from io import BytesIO


def fetch_ff_factors(model='3', frequency='daily'):
    """
    Fetch Fama-French factor data.
    
    Parameters:
    -----------
    model : str
        '3' for 3-factor (Mkt-RF, SMB, HML)
        '5' for 5-factor (adds RMW, CMA)
    frequency : str
        'daily' or 'monthly'
    
    Returns:
    --------
    pd.DataFrame : Factor returns with date index
    """
    base_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    
    if model == '3':
        if frequency == 'daily':
            filename = "F-F_Research_Data_Factors_daily_CSV.zip"
        else:
            filename = "F-F_Research_Data_Factors_CSV.zip"
    elif model == '5':
        if frequency == 'daily':
            filename = "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
        else:
            filename = "F-F_Research_Data_5_Factors_2x3_CSV.zip"
    else:
        raise ValueError("model must be '3' or '5'")
    
    url = base_url + filename
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with ZipFile(BytesIO(response.content)) as z:
            csv_name = z.namelist()[0]
            with z.open(csv_name) as f:
                content = f.read().decode('utf-8')
        
        # Find where data starts (skip header text)
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and line.strip()[0].isdigit():
                start_idx = i
                break
        
        # Find where data ends (before annual data)
        end_idx = len(lines)
        for i in range(start_idx, len(lines)):
            if 'Annual' in lines[i] or lines[i].strip() == '':
                if i > start_idx + 10:  # Make sure we have some data
                    end_idx = i
                    break
        
        # Parse data
        data_text = '\n'.join(lines[start_idx-1:end_idx])
        df = pd.read_csv(StringIO(data_text))
        
        # Clean up
        df.columns = df.columns.str.strip()
        date_col = df.columns[0]
        df = df.rename(columns={date_col: 'Date'})
        
        # Parse dates
        if frequency == 'daily':
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
        else:
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m')
        
        df = df.set_index('Date')
        
        # Convert to decimal (data is in percent)
        df = df / 100
        
        return df
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Using synthetic data for demonstration...")
        return generate_synthetic_factors(model, frequency)


def generate_synthetic_factors(model='3', frequency='daily', years=5):
    """
    Generate synthetic factor data for testing.
    Based on historical factor characteristics.
    """
    np.random.seed(42)
    
    if frequency == 'daily':
        periods = years * 252
        dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq='B')
    else:
        periods = years * 12
        dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq='M')
    
    # Approximate factor characteristics (daily)
    # Annual: Mkt~8%, SMB~2%, HML~3%, RMW~3%, CMA~3%
    if frequency == 'daily':
        scale = 1/252
    else:
        scale = 1/12
    
    data = {
        'Mkt-RF': np.random.normal(0.08 * scale, 0.16 * np.sqrt(scale), periods),
        'SMB': np.random.normal(0.02 * scale, 0.10 * np.sqrt(scale), periods),
        'HML': np.random.normal(0.03 * scale, 0.10 * np.sqrt(scale), periods),
        'RF': np.ones(periods) * 0.02 * scale  # Risk-free rate
    }
    
    if model == '5':
        data['RMW'] = np.random.normal(0.03 * scale, 0.08 * np.sqrt(scale), periods)
        data['CMA'] = np.random.normal(0.03 * scale, 0.08 * np.sqrt(scale), periods)
    
    return pd.DataFrame(data, index=dates)


def fetch_stock_returns(ticker, start_date=None, end_date=None, period='5y'):
    """
    Fetch stock returns from Yahoo Finance.
    """
    import yfinance as yf
    
    if start_date and end_date:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    else:
        data = yf.download(ticker, period=period, progress=False)
    
    prices = data['Adj Close']
    returns = prices.pct_change().dropna()
    
    return returns


def align_data(stock_returns, factor_data):
    """
    Align stock returns with factor data on common dates.
    """
    # Find common dates
    common_dates = stock_returns.index.intersection(factor_data.index)
    
    stock_aligned = stock_returns.loc[common_dates]
    factors_aligned = factor_data.loc[common_dates]
    
    # Calculate excess returns
    excess_returns = stock_aligned - factors_aligned['RF']
    
    return excess_returns, factors_aligned


if __name__ == "__main__":
    # Example: Fetch FF3 factors
    print("Fetching Fama-French 3-Factor data...")
    ff3 = fetch_ff_factors(model='3', frequency='daily')
    
    print(f"\nData shape: {ff3.shape}")
    print(f"Date range: {ff3.index[0].date()} to {ff3.index[-1].date()}")
    print(f"\nColumns: {list(ff3.columns)}")
    
    print("\nFactor Summary Statistics (annualized):")
    print("-" * 40)
    for col in ['Mkt-RF', 'SMB', 'HML']:
        mean_ann = ff3[col].mean() * 252 * 100
        vol_ann = ff3[col].std() * np.sqrt(252) * 100
        print(f"{col}: Mean={mean_ann:.2f}%, Vol={vol_ann:.2f}%")
    
    print(f"\nRisk-Free Rate (avg): {ff3['RF'].mean() * 252 * 100:.2f}%")
