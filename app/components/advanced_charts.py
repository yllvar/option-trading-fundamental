"""
Advanced Charts Component
3D visualizations, enhanced heatmaps, and interactive dashboards.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_volatility_surface_3d(strikes, maturities, option_prices, title="3D Volatility Surface"):
    """
    Create 3D surface plot of option prices.
    
    Parameters:
    -----------
    strikes : array
        Strike prices
    maturities : array
        Times to maturity
    option_prices : 2D array
        Option prices [maturity, strike]
    title : str
        Chart title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure(data=[go.Surface(
        x=strikes,
        y=maturities,
        z=option_prices,
        colorscale='Viridis',
        colorbar=dict(title="Price ($)"),
        hovertemplate='Strike: $%{x:.2f}<br>Maturity: %{y:.2f}y<br>Price: $%{z:.4f}<extra></extra>'
    )])
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Strike Price ($)",
            yaxis_title="Time to Maturity (years)",
            zaxis_title="Option Price ($)",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=600,
        margin=dict(l=0, r=0, b=0, t=40)
    )
    
    return fig


def create_greeks_surface_3d(strikes, maturities, greek_values, greek_name="Delta"):
    """Create 3D surface for Greeks."""
    fig = go.Figure(data=[go.Surface(
        x=strikes,
        y=maturities,
        z=greek_values,
        colorscale='RdYlGn',
        colorbar=dict(title=greek_name),
        hovertemplate=f'Strike: $%{{x:.2f}}<br>Maturity: %{{y:.2f}}y<br>{greek_name}: %{{z:.4f}}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f"3D {greek_name} Surface",
        scene=dict(
            xaxis_title="Strike Price ($)",
            yaxis_title="Time to Maturity (years)",
            zaxis_title=greek_name,
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=600
    )
    
    return fig


def create_correlation_heatmap_enhanced(corr_matrix, labels, title="Enhanced Correlation Matrix"):
    """
    Enhanced correlation heatmap with annotations and clustering.
    
    Parameters:
    -----------
    corr_matrix : array
        Correlation matrix
    labels : list
        Asset labels
    title : str
        Chart title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Create annotations
    annotations = []
    for i, row in enumerate(corr_matrix):
        for j, value in enumerate(row):
            annotations.append(
                dict(
                    x=labels[j],
                    y=labels[i],
                    text=f'{value:.2f}',
                    showarrow=False,
                    font=dict(
                        color='white' if abs(value) > 0.5 else 'black',
                        size=10
                    )
                )
            )
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=labels,
        y=labels,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        colorbar=dict(title="Correlation"),
        hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        annotations=annotations,
        height=500,
        xaxis=dict(side='bottom'),
        yaxis=dict(side='left', autorange='reversed')
    )
    
    return fig


def create_risk_decomposition_chart(weights, risk_contributions, labels, title="Risk Decomposition"):
    """
    Create waterfall chart showing risk contribution by asset.
    
    Parameters:
    -----------
    weights : array
        Portfolio weights
    risk_contributions : array
        Risk contributions (percentage)
    labels : list
        Asset labels
    title : str
        Chart title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Sort by risk contribution
    sorted_indices = np.argsort(risk_contributions)[::-1]
    sorted_labels = [labels[i] for i in sorted_indices]
    sorted_risk = risk_contributions[sorted_indices] * 100
    sorted_weights = weights[sorted_indices] * 100
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Risk Contribution', 'Portfolio Weight'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Risk contribution
    fig.add_trace(
        go.Bar(
            x=sorted_labels,
            y=sorted_risk,
            name='Risk %',
            marker_color='lightcoral',
            text=[f'{r:.1f}%' for r in sorted_risk],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Portfolio weight
    fig.add_trace(
        go.Bar(
            x=sorted_labels,
            y=sorted_weights,
            name='Weight %',
            marker_color='lightblue',
            text=[f'{w:.1f}%' for w in sorted_weights],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="Risk Contribution (%)", row=1, col=1)
    fig.update_yaxes(title_text="Portfolio Weight (%)", row=1, col=2)
    
    fig.update_layout(
        title_text=title,
        height=400,
        showlegend=False
    )
    
    return fig


def create_efficient_frontier_enhanced(frontier_returns, frontier_vols, frontier_sharpes,
                                       optimal_return, optimal_vol, asset_returns, asset_vols,
                                       asset_names):
    """
    Enhanced efficient frontier with multiple overlays.
    
    Parameters:
    -----------
    frontier_returns : array
        Frontier returns
    frontier_vols : array
        Frontier volatilities
    frontier_sharpes : array
        Frontier Sharpe ratios
    optimal_return : float
        Optimal portfolio return
    optimal_vol : float
        Optimal portfolio volatility
    asset_returns : array
        Individual asset returns
    asset_vols : array
        Individual asset volatilities
    asset_names : list
        Asset names
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    # Efficient frontier (colored by Sharpe)
    fig.add_trace(go.Scatter(
        x=frontier_vols * 100,
        y=frontier_returns * 100,
        mode='markers',
        name='Efficient Frontier',
        marker=dict(
            size=10,
            color=frontier_sharpes,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Sharpe<br>Ratio", x=1.15)
        ),
        text=[f'Return: {r*100:.2f}%<br>Vol: {v*100:.2f}%<br>Sharpe: {s:.3f}'
              for r, v, s in zip(frontier_returns, frontier_vols, frontier_sharpes)],
        hovertemplate='%{text}<extra></extra>'
    ))
    
    # Optimal portfolio
    fig.add_trace(go.Scatter(
        x=[optimal_vol * 100],
        y=[optimal_return * 100],
        mode='markers',
        name='Optimal Portfolio',
        marker=dict(size=20, color='red', symbol='star', line=dict(color='darkred', width=2)),
        text=[f'Optimal<br>Return: {optimal_return*100:.2f}%<br>Vol: {optimal_vol*100:.2f}%'],
        hovertemplate='%{text}<extra></extra>'
    ))
    
    # Individual assets
    fig.add_trace(go.Scatter(
        x=asset_vols * 100,
        y=asset_returns * 100,
        mode='markers+text',
        name='Individual Assets',
        marker=dict(size=12, color='orange', line=dict(color='darkorange', width=1)),
        text=asset_names,
        textposition='top center',
        textfont=dict(size=10),
        hovertemplate='%{text}<br>Return: %{y:.2f}%<br>Vol: %{x:.2f}%<extra></extra>'
    ))
    
    # Capital Market Line (if applicable)
    if len(frontier_sharpes) > 0:
        max_sharpe_idx = np.argmax(frontier_sharpes)
        max_sharpe_return = frontier_returns[max_sharpe_idx]
        max_sharpe_vol = frontier_vols[max_sharpe_idx]
        
        # CML from risk-free rate through max Sharpe portfolio
        cml_vols = np.linspace(0, max(frontier_vols) * 1.2, 100)
        cml_returns = 0.02 + (max_sharpe_return - 0.02) / max_sharpe_vol * cml_vols
        
        fig.add_trace(go.Scatter(
            x=cml_vols * 100,
            y=cml_returns * 100,
            mode='lines',
            name='Capital Market Line',
            line=dict(color='green', dash='dash', width=2),
            hovertemplate='CML<br>Vol: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title="Enhanced Efficient Frontier",
        xaxis_title="Volatility (Risk) %",
        yaxis_title="Expected Return %",
        hovermode='closest',
        height=600,
        showlegend=True,
        legend=dict(x=0.02, y=0.98)
    )
    
    return fig


def create_performance_dashboard(returns_series, benchmark_returns=None):
    """
    Create comprehensive performance dashboard.
    
    Parameters:
    -----------
    returns_series : pd.Series
        Time series of returns
    benchmark_returns : pd.Series, optional
        Benchmark returns
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Calculate cumulative returns
    cum_returns = (1 + returns_series).cumprod()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Cumulative Returns', 'Rolling Volatility (30d)',
                       'Return Distribution', 'Drawdown'),
        specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
               [{'type': 'histogram'}, {'type': 'scatter'}]]
    )
    
    # Cumulative returns
    fig.add_trace(
        go.Scatter(x=cum_returns.index, y=cum_returns.values,
                  name='Portfolio', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    
    if benchmark_returns is not None:
        cum_bench = (1 + benchmark_returns).cumprod()
        fig.add_trace(
            go.Scatter(x=cum_bench.index, y=cum_bench.values,
                      name='Benchmark', line=dict(color='gray', dash='dash')),
            row=1, col=1
        )
    
    # Rolling volatility
    rolling_vol = returns_series.rolling(30).std() * np.sqrt(252) * 100
    fig.add_trace(
        go.Scatter(x=rolling_vol.index, y=rolling_vol.values,
                  name='Volatility', line=dict(color='orange', width=2)),
        row=1, col=2
    )
    
    # Return distribution
    fig.add_trace(
        go.Histogram(x=returns_series * 100, nbinsx=50,
                    name='Returns', marker_color='lightblue'),
        row=2, col=1
    )
    
    # Drawdown
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max * 100
    fig.add_trace(
        go.Scatter(x=drawdown.index, y=drawdown.values,
                  name='Drawdown', fill='tozeroy',
                  line=dict(color='red', width=1)),
        row=2, col=2
    )
    
    # Update axes
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_xaxes(title_text="Return (%)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=2)
    
    fig.update_yaxes(title_text="Cumulative Return", row=1, col=1)
    fig.update_yaxes(title_text="Volatility (%)", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=2)
    
    fig.update_layout(
        title_text="Performance Dashboard",
        height=700,
        showlegend=True
    )
    
    return fig


def create_factor_exposure_radar(betas, factor_names):
    """
    Create radar chart of factor exposures.
    
    Parameters:
    -----------
    betas : dict or array
        Factor betas
    factor_names : list
        Factor names
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    if isinstance(betas, dict):
        beta_values = [betas.get(f, 0) for f in factor_names]
    else:
        beta_values = list(betas)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=beta_values,
        theta=factor_names,
        fill='toself',
        name='Factor Exposure',
        line_color='blue'
    ))
    
    # Add neutral line at 0
    fig.add_trace(go.Scatterpolar(
        r=[0] * len(factor_names),
        theta=factor_names,
        mode='lines',
        name='Neutral',
        line=dict(color='gray', dash='dash')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[-1, 2])
        ),
        title="Factor Exposure Profile",
        height=500,
        showlegend=True
    )
    
    return fig
