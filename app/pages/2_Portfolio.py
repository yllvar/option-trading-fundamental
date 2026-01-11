"""
Portfolio Optimization Page
Optimize portfolios using Markowitz, Risk Parity, and other methods.
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from portfolio.markowitz import (
    portfolio_return, portfolio_volatility, portfolio_sharpe,
    optimize_sharpe, optimize_min_variance, optimize_target_return
)
from portfolio.risk_parity import (
    optimize_risk_parity, inverse_volatility_weights,
    risk_contribution_pct
)
from portfolio.efficient_frontier import compute_efficient_frontier
from app.utils.data_fetcher import fetch_multiple_stocks, calculate_returns

# Force reload of validation to bypass Streamlit caching
import importlib
import utils.validation
importlib.reload(utils.validation)
from utils.validation import validate_covariance_matrix_v3, validate_weights, ValidationError

# Phase 3: Import utilities
from app.utils.export import export_to_csv, export_to_json, format_results_for_export
from app.utils.session_state import init_session_state, add_to_history, get_history_dataframe

# Page config
st.set_page_config(
    page_title="Portfolio Optimization - Quant Fundamentals",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

@st.cache_data
def run_optimization(opt_method, mean_returns, cov_matrix, risk_free_rate, allow_short, target_return=None):
    # Convert inputs to numpy for numerical stability
    if hasattr(mean_returns, 'values'):
        mean_returns = mean_returns.values.flatten()
    if hasattr(cov_matrix, 'values') and not isinstance(cov_matrix, np.ndarray):
        cov_matrix = cov_matrix.values
        
    if opt_method == "Maximum Sharpe Ratio":
        result = optimize_sharpe(
            mean_returns, cov_matrix,
            risk_free_rate=risk_free_rate,
            allow_short=allow_short
        )
    elif opt_method == "Minimum Variance":
        result = optimize_min_variance(
            mean_returns, cov_matrix,
            allow_short=allow_short
        )
    elif opt_method == "Risk Parity":
        result = optimize_risk_parity(cov_matrix)
    elif opt_method == "Inverse Volatility":
        weights = inverse_volatility_weights(cov_matrix)
        ret = portfolio_return(weights, mean_returns)
        vol = portfolio_volatility(weights, cov_matrix)
        sharpe = portfolio_sharpe(weights, mean_returns, cov_matrix, risk_free_rate)
        result = {
            'weights': weights,
            'return': ret,
            'volatility': vol,
            'sharpe': sharpe
        }
    else:  # Target Return
        weights, vol = optimize_target_return(
            mean_returns, cov_matrix, target_return,
            allow_short=allow_short
        )
        if weights is None:
            return None
        sharpe = (target_return - risk_free_rate) / vol
        result = {
            'weights': weights,
            'return': target_return,
            'volatility': vol,
            'sharpe': sharpe
        }
    return result

@st.cache_data
def get_efficient_frontier(mean_returns, cov_matrix, risk_free_rate, allow_short):
    # Convert inputs to numpy
    if hasattr(mean_returns, 'values'):
        mean_returns = mean_returns.values.flatten()
    if hasattr(cov_matrix, 'values') and not isinstance(cov_matrix, np.ndarray):
        cov_matrix = cov_matrix.values
        
    result = compute_efficient_frontier(
        mean_returns, cov_matrix,
        risk_free_rate=risk_free_rate,
        allow_short=allow_short,
        n_points=50
    )
    result['sharpes'] = (result['returns'] - risk_free_rate) / result['volatilities']
    return result

# Custom CSS Loading
def load_css():
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Header
col1, col2 = st.columns([6, 1])
with col1:
    st.title("💼 Portfolio Optimization")
    st.markdown("Optimize portfolios using modern portfolio theory")
with col2:
    if st.button("🏠 Home"):
        st.switch_page("main.py")

st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Data input method
    st.subheader("Data Input")
    input_method = st.radio(
        "Input Method",
        ["Manual (Example Data)", "Real Market Data (yfinance)", "Custom Returns & Covariance"],
        help="Choose how to input portfolio data"
    )
    
    if input_method == "Manual (Example Data)":
        # Use example data
        st.info("Using 5-asset example portfolio")
        n_assets = 5
        asset_names = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        
        # Generate example data
        np.random.seed(42)
        mean_returns = np.array([0.12, 0.10, 0.14, 0.08, 0.11])
        vols = np.array([0.20, 0.15, 0.25, 0.10, 0.18])
        
        # Correlation matrix
        corr = np.array([
            [1.0, 0.3, 0.4, 0.2, 0.35],
            [0.3, 1.0, 0.35, 0.25, 0.3],
            [0.4, 0.35, 1.0, 0.3, 0.4],
            [0.2, 0.25, 0.3, 1.0, 0.2],
            [0.35, 0.3, 0.4, 0.2, 1.0]
        ])
        
        cov_matrix = np.outer(vols, vols) * corr

    elif input_method == "Real Market Data (yfinance)":
        tickers_str = st.text_input(
            "Enter Tickers (comma-separated)",
            value="AAPL, MSFT, GOOGL, AMZN",
            help="e.g. AAPL, MSFT, BTC-USD"
        )
        tickers = [t.strip().upper() for t in tickers_str.split(",")]
        
        lookback = st.selectbox(
            "Lookback Period",
            ["1y", "2y", "5y", "max"],
            index=0
        )
        
        with st.spinner("Fetching market data..."):
            data = fetch_multiple_stocks(tickers, period=lookback)
            if not data.empty:
                returns = calculate_returns(data)
                
                asset_names = returns.columns.tolist()
                n_assets = len(asset_names)
                
                # Check for shared data points
                n_days = len(returns)
                if n_days < 20:  # Warning if fewer than 20 common days
                    st.warning(f"⚠️ Only {n_days} shared trading days found. Data might be insufficient for reliable optimization.")
                else:
                    st.success(f"✅ Fetched data for {n_assets} assets ({n_days} shared trading days)")
                
                mean_returns = returns.mean() * 252  # Annualized
                cov_matrix = returns.cov() * 252     # Annualized
            else:
                st.error("❌ Failed to fetch data. Falling back to example.")
                input_method = "Manual (Example Data)"
                st.rerun()
        
    else:
        # Custom input
        n_assets = st.number_input("Number of Assets", min_value=2, max_value=10, value=3)
        asset_names = [f"Asset {i+1}" for i in range(n_assets)]
        
        st.markdown("**Expected Returns (Annual %)**")
        mean_returns = np.array([
            st.number_input(f"{name}", value=10.0, key=f"ret_{i}") / 100
            for i, name in enumerate(asset_names)
        ])
        
        st.markdown("**Volatilities (Annual %)**")
        vols = np.array([
            st.number_input(f"{name}", value=15.0, key=f"vol_{i}") / 100
            for i, name in enumerate(asset_names)
        ])
        
        # Simple correlation assumption
        avg_corr = st.slider("Average Correlation", 0.0, 1.0, 0.3, 0.05)
        corr = np.eye(n_assets) + avg_corr * (np.ones((n_assets, n_assets)) - np.eye(n_assets))
        cov_matrix = np.outer(vols, vols) * corr
    
    st.markdown("---")
    
    # Optimization method
    st.subheader("Optimization Method")
    opt_method = st.selectbox(
        "Method",
        [
            "Maximum Sharpe Ratio",
            "Minimum Variance",
            "Risk Parity",
            "Inverse Volatility",
            "Target Return"
        ],
        help="Choose optimization objective"
    )
    
    # Risk-free rate
    risk_free_rate = st.slider(
        "Risk-Free Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
        help="Annual risk-free rate"
    ) / 100
    
    # Target return (if applicable)
    if opt_method == "Target Return":
        target_return = st.slider(
            "Target Return (%)",
            min_value=float(mean_returns.min() * 100),
            max_value=float(mean_returns.max() * 100),
            value=float(mean_returns.mean() * 100),
            step=0.5
        ) / 100
    
    # Constraints
    st.markdown("---")
    st.subheader("Constraints")
    allow_short = st.checkbox("Allow Short Selling", value=False)
    
    st.markdown("---")
    
    # Optimize button
    optimize_button = st.button(
        "🚀 Optimize",
        type="primary",
        use_container_width=True
    )

# Main content
if optimize_button:
    try:
        # Validate inputs
        
        # Call v3 and update reference
        validate_covariance_matrix_v3(cov_matrix)
        if hasattr(cov_matrix, 'values'):
             cov_matrix = cov_matrix.values
        
        with st.spinner("Optimizing portfolio..."):
            t_ret = target_return if opt_method == "Target Return" else None
            result = run_optimization(
                opt_method, mean_returns, cov_matrix, 
                risk_free_rate, allow_short, t_ret
            )
            
            if result is None:
                st.error("❌ Target return not achievable with given constraints")
                st.stop()
                
            weights = result['weights']
            
            # Validate weights
            validate_weights(weights, allow_short=allow_short)
        
        st.success("✅ Optimization complete!")
        
        # Display results
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📊 Portfolio Metrics")
            
            # Key metrics
            st.metric("Expected Return", f"{result['return']*100:.2f}%")
            st.metric("Volatility (Risk)", f"{result['volatility']*100:.2f}%")
            st.metric("Sharpe Ratio", f"{result['sharpe']:.3f}")
            
            st.markdown("---")
            
            # Allocation table
            st.markdown("### 💰 Allocation")
            
            allocation_df = pd.DataFrame({
                'Asset': asset_names,
                'Weight': weights,
                'Weight %': weights * 100
            })
            allocation_df = allocation_df.sort_values('Weight', ascending=False)
            
            # Display with formatting
            st.dataframe(
                allocation_df.style.format({
                    'Weight': '{:.4f}',
                    'Weight %': '{:.2f}%'
                }).background_gradient(subset=['Weight'], cmap='Blues'),
                hide_index=True,
                use_container_width=True
            )
            
            # Risk contribution (if available)
            if opt_method == "Risk Parity":
                st.markdown("---")
                st.markdown("### ⚖️ Risk Contribution")
                risk_contrib = result['risk_contributions']
                
                risk_df = pd.DataFrame({
                    'Asset': asset_names,
                    'Risk %': risk_contrib * 100
                })
                st.dataframe(
                    risk_df.style.format({'Risk %': '{:.2f}%'}),
                    hide_index=True,
                    use_container_width=True
                )
        
        with col2:
            # Pie chart - Allocation
            st.markdown("### 🥧 Portfolio Allocation")
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=asset_names,
                values=weights,
                hole=0.3,
                marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'][:n_assets])
            )])
            
            fig_pie.update_layout(
                showlegend=True,
                height=350
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Bar chart - Weights
            st.markdown("### 📊 Asset Weights")
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=asset_names,
                    y=weights * 100,
                    marker_color='#1f77b4',
                    text=[f'{w*100:.1f}%' for w in weights],
                    textposition='outside'
                )
            ])
            
            fig_bar.update_layout(
                yaxis_title="Weight (%)",
                xaxis_title="Asset",
                showlegend=False,
                height=350
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Efficient Frontier
        st.markdown("---")
        st.markdown("### 📈 Efficient Frontier")
        
        with st.spinner("Computing efficient frontier..."):
            # Compute efficient frontier
            frontier_data = get_efficient_frontier(
                mean_returns, cov_matrix, risk_free_rate, allow_short
            )
        
        # Create efficient frontier plot
        fig_ef = go.Figure()
        
        # Efficient frontier line
        fig_ef.add_trace(go.Scatter(
            x=frontier_data['volatilities'] * 100,
            y=frontier_data['returns'] * 100,
            mode='markers',
            name='Efficient Frontier',
            marker=dict(
                size=8,
                color=frontier_data['sharpes'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe<br>Ratio")
            ),
            text=[f"Return: {r*100:.2f}%<br>Vol: {v*100:.2f}%<br>Sharpe: {s:.3f}"
                  for r, v, s in zip(frontier_data['returns'], frontier_data['volatilities'], frontier_data['sharpes'])],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        # Optimal portfolio
        fig_ef.add_trace(go.Scatter(
            x=[result['volatility'] * 100],
            y=[result['return'] * 100],
            mode='markers',
            name='Optimal Portfolio',
            marker=dict(size=15, color='red', symbol='star'),
            text=[f"Optimal<br>Return: {result['return']*100:.2f}%<br>Vol: {result['volatility']*100:.2f}%"],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        # Individual assets
        fig_ef.add_trace(go.Scatter(
            x=vols * 100,
            y=mean_returns * 100,
            mode='markers+text',
            name='Individual Assets',
            marker=dict(size=10, color='orange'),
            text=asset_names,
            textposition='top center',
            hovertemplate='%{text}<br>Return: %{y:.2f}%<br>Vol: %{x:.2f}%<extra></extra>'
        ))
        
        fig_ef.update_layout(
            title="Efficient Frontier",
            xaxis_title="Volatility (Risk) %",
            yaxis_title="Expected Return %",
            hovermode='closest',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_ef, use_container_width=True)
        
        # Correlation matrix heatmap
        st.markdown("---")
        st.markdown("### 🔥 Correlation Matrix")
        
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr,
            x=asset_names,
            y=asset_names,
            colorscale='RdBu',
            zmid=0,
            text=corr,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig_corr.update_layout(
            title="Asset Correlation Matrix",
            height=400
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Summary statistics
        st.markdown("---")
        st.markdown("### 📋 Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **Portfolio Metrics:**
            - Expected Return: {result['return']*100:.2f}%
            - Volatility: {result['volatility']*100:.2f}%
            - Sharpe Ratio: {result['sharpe']:.3f}
            - Risk-Free Rate: {risk_free_rate*100:.2f}%
            """)
        
        with col2:
            st.markdown(f"""
            **Allocation Stats:**
            - Number of Assets: {n_assets}
            - Max Weight: {weights.max()*100:.2f}%
            - Min Weight: {weights.min()*100:.2f}%
            - Concentration (HHI): {(weights**2).sum():.3f}
            """)
        
        with col3:
            st.markdown(f"""
            **Optimization:**
            - Method: {opt_method}
            - Short Selling: {'Allowed' if allow_short else 'Not Allowed'}
            - Constraints: {'Long-only' if not allow_short else 'Unconstrained'}
            """)
        
        # Phase 3: Save to history
        params = {
            'method': opt_method,
            'n_assets': n_assets,
            'assets': ", ".join(asset_names),
            'risk_free': risk_free_rate,
            'input': input_method
        }
        results_hist = {
            'return': result['return'],
            'volatility': result['volatility'],
            'sharpe': result['sharpe']
        }
        add_to_history('portfolio', params, results_hist)
        
        # Phase 3: Export Results
        st.markdown("---")
        st.markdown("### 📥 Export Results")
        
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        
        with col_ex1:
            export_df = pd.DataFrame({
                'Asset': asset_names,
                'Weight': weights,
                'Weight %': weights * 100
            })
            csv_data = export_to_csv(export_df)
            st.download_button("📄 Download CSV", csv_data, 
                             f"portfolio_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                             "text/csv", use_container_width=True)
        
        with col_ex2:
            json_data = export_to_json({
                'timestamp': pd.Timestamp.now().isoformat(),
                'parameters': params,
                'results': {k: float(v) for k, v in results_hist.items()}
            })
            st.download_button("📋 Download JSON", json_data,
                             f"portfolio_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                             "application/json", use_container_width=True)
            
        with col_ex3:
            history_count = len(get_history_dataframe('portfolio'))
            st.info(f"💾 Saved to history\n\n{history_count} total optimizations")
        
    except ValidationError as e:
        st.error(f"❌ **Validation Error:** {e}")
        st.info("💡 Please check your input parameters.")
    
    except Exception as e:
        st.error(f"❌ **Error:** {e}")
        st.exception(e)

else:
    # Initial state
    st.info("""
    👈 **Get Started:**
    1. Choose data input method (Manual or Custom)
    2. Select optimization method
    3. Set risk-free rate and constraints
    4. Click **Optimize** to see results
    
    **Features:**
    - Maximum Sharpe Ratio optimization
    - Minimum Variance portfolio
    - Risk Parity allocation
    - Inverse Volatility weighting
    - Target Return optimization
    - Efficient Frontier visualization
    - Correlation analysis
    """)
    
    # Example scenarios
    st.markdown("### 📝 Example Scenarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Maximum Sharpe Ratio:**
        - Use example 5-asset portfolio
        - Risk-free rate: 2%
        - Long-only constraints
        - Maximizes risk-adjusted returns
        """)
    
    with col2:
        st.markdown("""
        **Risk Parity:**
        - Equal risk contribution from each asset
        - Diversification across risk sources
        - No return assumptions needed
        - Stable allocation
        """)

# Sidebar footer
with st.sidebar:
    # Phase 3: History Panel
    st.markdown("---")
    st.markdown("### 📜 Optimization History")
    
    history_df = get_history_dataframe('portfolio')
    if not history_df.empty:
        st.dataframe(history_df.tail(5), use_container_width=True, hide_index=True)
        if st.button("Clear History", use_container_width=True):
            from app.utils.session_state import clear_history
            clear_history('portfolio')
            st.rerun()
    else:
        st.info("No optimizations yet")
        
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - **Sharpe Ratio** measures risk-adjusted return
    - **Risk Parity** equalizes risk contributions
    - **Efficient Frontier** shows optimal portfolios
    - **Correlation** affects diversification benefits
    """)
