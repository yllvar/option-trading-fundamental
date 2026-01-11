"""
Scenario Analysis Component
Tools for stress testing and what-if analysis.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def options_scenario_analysis(S0, K, r, sigma, T, option_type, pricing_func):
    """
    Run scenario analysis for options.
    
    Parameters:
    -----------
    S0 : float
        Current stock price
    K : float
        Strike price
    r : float
        Risk-free rate
    sigma : float
        Volatility
    T : float
        Time to maturity
    option_type : str
        'Call' or 'Put'
    pricing_func : callable
        Pricing function to use
        
    Returns:
    --------
    pd.DataFrame : Scenario results
    """
    # Base case price
    base_price = pricing_func(S0, K, r, sigma, T)
    
    scenarios = {
        'Base Case': (S0, sigma, T, r),
        'Stock +20%': (S0 * 1.2, sigma, T, r),
        'Stock +10%': (S0 * 1.1, sigma, T, r),
        'Stock -10%': (S0 * 0.9, sigma, T, r),
        'Stock -20%': (S0 * 0.8, sigma, T, r),
        'Vol +50%': (S0, sigma * 1.5, T, r),
        'Vol +25%': (S0, sigma * 1.25, T, r),
        'Vol -25%': (S0, sigma * 0.75, T, r),
        'Vol -50%': (S0, sigma * 0.5, T, r),
        'Time Halved': (S0, sigma, T * 0.5, r),
        'Time Doubled': (S0, sigma, T * 2.0, r),
        'Rate +2%': (S0, sigma, T, r + 0.02),
        'Rate -2%': (S0, sigma, T, max(r - 0.02, 0))
    }
    
    results = []
    for name, (s, sig, t, rate) in scenarios.items():
        try:
            price = pricing_func(s, K, rate, sig, t)
            change = price - base_price
            change_pct = (change / base_price) * 100 if base_price > 0 else 0
            
            results.append({
                'Scenario': name,
                'Stock Price': f'${s:.2f}',
                'Volatility': f'{sig*100:.1f}%',
                'Time': f'{t:.2f}y',
                'Rate': f'{rate*100:.1f}%',
                'Option Price': f'${price:.4f}',
                'Change': f'${change:.4f}',
                'Change %': f'{change_pct:+.2f}%'
            })
        except:
            continue
    
    return pd.DataFrame(results)


def create_scenario_heatmap(S_range, vol_range, pricing_func, K, r, T):
    """
    Create 2D heatmap of option prices across stock price and volatility scenarios.
    
    Parameters:
    -----------
    S_range : array
        Range of stock prices
    vol_range : array
        Range of volatilities
    pricing_func : callable
        Pricing function
    K : float
        Strike price
    r : float
        Risk-free rate
    T : float
        Time to maturity
        
    Returns:
    --------
    plotly.graph_objects.Figure : Heatmap figure
    """
    prices = np.zeros((len(vol_range), len(S_range)))
    
    for i, vol in enumerate(vol_range):
        for j, S in enumerate(S_range):
            try:
                prices[i, j] = pricing_func(S, K, r, vol, T)
            except:
                prices[i, j] = np.nan
    
    fig = go.Figure(data=go.Heatmap(
        z=prices,
        x=S_range,
        y=[v*100 for v in vol_range],
        colorscale='Viridis',
        colorbar=dict(title="Option<br>Price ($)"),
        hovertemplate='Stock: $%{x:.2f}<br>Vol: %{y:.1f}%<br>Price: $%{z:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Option Price Sensitivity Heatmap",
        xaxis_title="Stock Price ($)",
        yaxis_title="Volatility (%)",
        height=500
    )
    
    return fig


def portfolio_scenario_analysis(weights, mean_returns, cov_matrix, asset_names):
    """
    Run scenario analysis for portfolio.
    
    Parameters:
    -----------
    weights : array
        Portfolio weights
    mean_returns : array
        Expected returns
    cov_matrix : array
        Covariance matrix
    asset_names : list
        Asset names
        
    Returns:
    --------
    pd.DataFrame : Scenario results
    """
    from portfolio.markowitz import portfolio_return, portfolio_volatility, portfolio_sharpe
    
    # Base case
    base_return = portfolio_return(weights, mean_returns)
    base_vol = portfolio_volatility(weights, cov_matrix)
    base_sharpe = portfolio_sharpe(weights, mean_returns, cov_matrix, 0.02)
    
    scenarios = []
    
    # Market crash scenario
    crash_returns = mean_returns * 0.5  # 50% reduction
    crash_cov = cov_matrix * 2  # Doubled volatility
    scenarios.append({
        'Scenario': 'Market Crash (-50%)',
        'Return': portfolio_return(weights, crash_returns),
        'Volatility': portfolio_volatility(weights, crash_cov),
        'Sharpe': portfolio_sharpe(weights, crash_returns, crash_cov, 0.02)
    })
    
    # Bull market
    bull_returns = mean_returns * 1.5
    scenarios.append({
        'Scenario': 'Bull Market (+50%)',
        'Return': portfolio_return(weights, bull_returns),
        'Volatility': base_vol,
        'Sharpe': portfolio_sharpe(weights, bull_returns, cov_matrix, 0.02)
    })
    
    # Correlation breakdown
    uncorr_cov = np.diag(np.diag(cov_matrix))  # Zero correlation
    scenarios.append({
        'Scenario': 'Zero Correlation',
        'Return': base_return,
        'Volatility': portfolio_volatility(weights, uncorr_cov),
        'Sharpe': portfolio_sharpe(weights, mean_returns, uncorr_cov, 0.02)
    })
    
    # High correlation
    high_corr_cov = cov_matrix.copy()
    vols = np.sqrt(np.diag(cov_matrix))
    corr = np.ones((len(vols), len(vols))) * 0.9
    np.fill_diagonal(corr, 1.0)
    high_corr_cov = np.outer(vols, vols) * corr
    scenarios.append({
        'Scenario': 'High Correlation (0.9)',
        'Return': base_return,
        'Volatility': portfolio_volatility(weights, high_corr_cov),
        'Sharpe': portfolio_sharpe(weights, mean_returns, high_corr_cov, 0.02)
    })
    
    # Asset failure (largest weight goes to zero)
    max_idx = np.argmax(weights)
    failure_returns = mean_returns.copy()
    failure_returns[max_idx] = -0.5  # 50% loss
    scenarios.append({
        'Scenario': f'{asset_names[max_idx]} Failure',
        'Return': portfolio_return(weights, failure_returns),
        'Volatility': base_vol,
        'Sharpe': portfolio_sharpe(weights, failure_returns, cov_matrix, 0.02)
    })
    
    # Add base case
    scenarios.insert(0, {
        'Scenario': 'Base Case',
        'Return': base_return,
        'Volatility': base_vol,
        'Sharpe': base_sharpe
    })
    
    df = pd.DataFrame(scenarios)
    
    # Add change columns
    df['Return Change'] = ((df['Return'] / base_return) - 1) * 100
    df['Vol Change'] = ((df['Volatility'] / base_vol) - 1) * 100
    df['Sharpe Change'] = ((df['Sharpe'] / base_sharpe) - 1) * 100
    
    # Format
    df['Return'] = df['Return'].apply(lambda x: f'{x*100:.2f}%')
    df['Volatility'] = df['Volatility'].apply(lambda x: f'{x*100:.2f}%')
    df['Sharpe'] = df['Sharpe'].apply(lambda x: f'{x:.3f}')
    df['Return Change'] = df['Return Change'].apply(lambda x: f'{x:+.1f}%')
    df['Vol Change'] = df['Vol Change'].apply(lambda x: f'{x:+.1f}%')
    df['Sharpe Change'] = df['Sharpe Change'].apply(lambda x: f'{x:+.1f}%')
    
    return df


def create_stress_test_chart(scenario_df):
    """Create visualization of stress test results."""
    # Extract numeric values for plotting
    scenarios = scenario_df['Scenario'].tolist()
    
    # Parse percentage changes
    return_changes = [float(x.strip('%+')) for x in scenario_df['Return Change']]
    vol_changes = [float(x.strip('%+')) for x in scenario_df['Vol Change']]
    sharpe_changes = [float(x.strip('%+')) for x in scenario_df['Sharpe Change']]
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Return Impact', 'Volatility Impact', 'Sharpe Impact')
    )
    
    # Return changes
    fig.add_trace(
        go.Bar(x=scenarios, y=return_changes, name='Return',
               marker_color=['green' if x > 0 else 'red' for x in return_changes]),
        row=1, col=1
    )
    
    # Volatility changes
    fig.add_trace(
        go.Bar(x=scenarios, y=vol_changes, name='Volatility',
               marker_color=['red' if x > 0 else 'green' for x in vol_changes]),
        row=1, col=2
    )
    
    # Sharpe changes
    fig.add_trace(
        go.Bar(x=scenarios, y=sharpe_changes, name='Sharpe',
               marker_color=['green' if x > 0 else 'red' for x in sharpe_changes]),
        row=1, col=3
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="Change (%)", row=1, col=1)
    fig.update_yaxes(title_text="Change (%)", row=1, col=2)
    fig.update_yaxes(title_text="Change (%)", row=1, col=3)
    
    fig.update_layout(height=400, showlegend=False, title_text="Stress Test Results")
    
    return fig
