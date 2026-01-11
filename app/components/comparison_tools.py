"""
Comparison Tools Component
Side-by-side comparison and analysis tools.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def compare_options(options_list):
    """
    Compare multiple options side-by-side.
    
    Parameters:
    -----------
    options_list : list of dict
        Each dict contains 'params' and 'results'
        
    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    comparison_data = []
    
    for i, opt in enumerate(options_list):
        params = opt['params']
        results = opt['results']
        
        comparison_data.append({
            'Option': f"#{i+1}",
            'Type': params.get('option_type', 'N/A'),
            'Stock': f"${params.get('S0', 0):.2f}",
            'Strike': f"${params.get('K', 0):.2f}",
            'Vol': f"{params.get('sigma', 0)*100:.1f}%",
            'Time': f"{params.get('T', 0):.2f}y",
            'Method': params.get('method', 'N/A'),
            'Price': f"${results.get('price', 0):.4f}",
            'Delta': f"{results.get('delta', 0):.4f}",
            'Gamma': f"{results.get('gamma', 0):.6f}",
            'Vega': f"${results.get('vega', 0):.4f}",
            'Theta': f"${results.get('theta', 0):.4f}",
            'Rho': f"${results.get('rho', 0):.4f}"
        })
    
    return pd.DataFrame(comparison_data)


def create_options_comparison_chart(options_list, metric='price'):
    """
    Create bar chart comparing options.
    
    Parameters:
    -----------
    options_list : list of dict
        Options to compare
    metric : str
        Metric to compare ('price', 'delta', 'gamma', etc.)
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    labels = [f"Option #{i+1}" for i in range(len(options_list))]
    values = [opt['results'].get(metric, 0) for opt in options_list]
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            text=[f'{v:.4f}' for v in values],
            textposition='outside',
            marker_color='#1f77b4'
        )
    ])
    
    fig.update_layout(
        title=f"{metric.capitalize()} Comparison",
        xaxis_title="Option",
        yaxis_title=metric.capitalize(),
        height=400,
        showlegend=False
    )
    
    return fig


def compare_portfolios(portfolios_list):
    """
    Compare multiple portfolio allocations.
    
    Parameters:
    -----------
    portfolios_list : list of dict
        Each dict contains 'name', 'weights', 'return', 'volatility', 'sharpe'
        
    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    comparison_data = []
    
    for portfolio in portfolios_list:
        comparison_data.append({
            'Portfolio': portfolio['name'],
            'Return': f"{portfolio['return']*100:.2f}%",
            'Volatility': f"{portfolio['volatility']*100:.2f}%",
            'Sharpe Ratio': f"{portfolio['sharpe']:.3f}",
            'Max Weight': f"{max(portfolio['weights'])*100:.1f}%",
            'Min Weight': f"{min(portfolio['weights'])*100:.1f}%",
            'Concentration': f"{(portfolio['weights']**2).sum():.3f}"
        })
    
    return pd.DataFrame(comparison_data)


def create_portfolio_comparison_chart(portfolios_list):
    """Create comparison chart for portfolios."""
    names = [p['name'] for p in portfolios_list]
    returns = [p['return'] * 100 for p in portfolios_list]
    vols = [p['volatility'] * 100 for p in portfolios_list]
    sharpes = [p['sharpe'] for p in portfolios_list]
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Expected Return', 'Volatility', 'Sharpe Ratio')
    )
    
    # Returns
    fig.add_trace(
        go.Bar(x=names, y=returns, name='Return', marker_color='green'),
        row=1, col=1
    )
    
    # Volatility
    fig.add_trace(
        go.Bar(x=names, y=vols, name='Volatility', marker_color='orange'),
        row=1, col=2
    )
    
    # Sharpe
    fig.add_trace(
        go.Bar(x=names, y=sharpes, name='Sharpe', marker_color='blue'),
        row=1, col=3
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text="%", row=1, col=2)
    fig.update_yaxes(title_text="Ratio", row=1, col=3)
    
    fig.update_layout(height=400, showlegend=False, title_text="Portfolio Comparison")
    
    return fig


def create_allocation_comparison(portfolios_list, asset_names):
    """Create stacked bar chart comparing allocations."""
    fig = go.Figure()
    
    for portfolio in portfolios_list:
        fig.add_trace(go.Bar(
            name=portfolio['name'],
            x=asset_names,
            y=portfolio['weights'] * 100,
            text=[f'{w*100:.1f}%' for w in portfolio['weights']],
            textposition='inside'
        ))
    
    fig.update_layout(
        title="Allocation Comparison",
        xaxis_title="Asset",
        yaxis_title="Weight (%)",
        barmode='group',
        height=400
    )
    
    return fig


def compare_factor_models(models_list):
    """
    Compare multiple factor model results.
    
    Parameters:
    -----------
    models_list : list of dict
        Each dict contains 'ticker', 'model', 'alpha', 'betas', 'r_squared'
        
    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    comparison_data = []
    
    for model in models_list:
        comparison_data.append({
            'Stock': model['ticker'],
            'Model': model['model'],
            'Alpha': f"{model['alpha']*100:.2f}%",
            'R-squared': f"{model['r_squared']:.4f}",
            'Market Beta': f"{model['betas'].get('Mkt-RF', 0):.3f}",
            'SMB Beta': f"{model['betas'].get('SMB', 0):.3f}",
            'HML Beta': f"{model['betas'].get('HML', 0):.3f}"
        })
    
    return pd.DataFrame(comparison_data)


def create_beta_comparison_chart(models_list):
    """Create comparison chart for factor betas."""
    tickers = [m['ticker'] for m in models_list]
    
    # Get all unique factors
    all_factors = set()
    for model in models_list:
        all_factors.update(model['betas'].keys())
    all_factors = sorted(list(all_factors))
    
    fig = go.Figure()
    
    for factor in all_factors:
        betas = [m['betas'].get(factor, 0) for m in models_list]
        fig.add_trace(go.Bar(
            name=factor,
            x=tickers,
            y=betas
        ))
    
    fig.update_layout(
        title="Factor Beta Comparison",
        xaxis_title="Stock",
        yaxis_title="Beta",
        barmode='group',
        height=400
    )
    
    return fig


def create_difference_heatmap(comparison_df, numeric_columns):
    """
    Create heatmap showing differences from baseline.
    
    Parameters:
    -----------
    comparison_df : pd.DataFrame
        Comparison dataframe
    numeric_columns : list
        Columns to include in heatmap
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Extract numeric values
    data = comparison_df[numeric_columns].copy()
    
    # Convert percentage strings to floats if needed
    for col in data.columns:
        if data[col].dtype == object:
            data[col] = data[col].str.rstrip('%').astype(float)
    
    # Calculate differences from first row (baseline)
    baseline = data.iloc[0]
    differences = data - baseline
    
    fig = go.Figure(data=go.Heatmap(
        z=differences.values,
        x=differences.columns,
        y=comparison_df.iloc[:, 0],  # First column as labels
        colorscale='RdYlGn',
        zmid=0,
        text=differences.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Difference")
    ))
    
    fig.update_layout(
        title="Difference from Baseline",
        xaxis_title="Metric",
        yaxis_title="Comparison Item",
        height=400
    )
    
    return fig
