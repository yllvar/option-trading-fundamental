"""
Factor Models Page
Analyze stocks using Fama-French factor models.
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

from app.utils.data_fetcher import fetch_stock_data, calculate_returns

# Force reload of factors modules to ensure latest logic is picked up
import importlib
import factors.data_loader
import factors.ff3_model
import factors.ff5_model
importlib.reload(factors.data_loader)
importlib.reload(factors.ff3_model)
importlib.reload(factors.ff5_model)

from factors.ff3_model import FF3Model
from factors.ff5_model import FF5Model
from factors.data_loader import generate_synthetic_factors, align_data
import datetime
st.sidebar.caption(f"🔄 Modules reloaded: {datetime.datetime.now().strftime('%H:%M:%S')}")

# Phase 3: Import utilities
from app.utils.export import export_to_csv, export_to_json, format_results_for_export
from app.utils.session_state import init_session_state, add_to_history, get_history_dataframe

# Page config
st.set_page_config(
    page_title="Factor Models - Quant Fundamentals",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

@st.cache_data
def run_factor_analysis(model_type, stock_returns, factor_data, frequency):
    if model_type == "Fama-French 3-Factor (FF3)":
        model = FF3Model()
    else:
        model = FF5Model()
    
    model.fit(stock_returns, factor_data)
    summary = model.summary(annualize=(frequency == "Daily"))
    predictions = model.predict(factor_data)
    
    return summary, predictions

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
    st.title("📈 Factor Model Analysis")
    st.markdown("Analyze stocks using Fama-French factor models")
with col2:
    if st.button("🏠 Home"):
        st.switch_page("main.py")

st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    st.subheader("Factor Model")
    model_type = st.radio(
        "Model",
        ["Fama-French 3-Factor (FF3)", "Fama-French 5-Factor (FF5)"],
        help="Choose factor model"
    )
    
    st.markdown("---")
    
    # Data input
    st.subheader("Data Input")
    data_source = st.radio(
        "Data Source",
        ["Synthetic Data (Demo)", "Real Stock Data (yfinance)", "Custom Returns"],
        help="Choose data source"
    )
    
    if data_source == "Synthetic Data (Demo)":
        st.info("Using synthetic factor data for demonstration")
        
        # Synthetic data parameters
        years = st.slider("Years of Data", 1, 5, 3)
        frequency = st.radio("Frequency", ["Daily", "Monthly"])
        
        # Generate synthetic data
        freq_map = {"Daily": "daily", "Monthly": "monthly"}
        model_map = {
            "Fama-French 3-Factor (FF3)": "3",
            "Fama-French 5-Factor (FF5)": "5"
        }
        
        factor_data = generate_synthetic_factors(
            model=model_map[model_type],
            frequency=freq_map[frequency],
            years=years
        )
        
        # Generate synthetic stock returns
        np.random.seed(42)
        n_obs = len(factor_data)
        
        # True parameters
        true_alpha = 0.0001  # ~2.5% annual for daily
        true_beta_mkt = 1.2
        true_beta_smb = 0.3
        true_beta_hml = -0.2
        
        stock_returns = (
            true_alpha +
            true_beta_mkt * factor_data['Mkt-RF'] +
            true_beta_smb * factor_data['SMB'] +
            true_beta_hml * factor_data['HML']
        )
        
        if model_type == "Fama-French 5-Factor (FF5)":
            true_beta_rmw = 0.25
            true_beta_cma = -0.15
            stock_returns += (
                true_beta_rmw * factor_data['RMW'] +
                true_beta_cma * factor_data['CMA']
            )
        
        # Add noise
        stock_returns += np.random.normal(0, 0.01, n_obs)
        
        ticker = "DEMO"
        
    elif data_source == "Real Stock Data (yfinance)":
        ticker = st.text_input("Stock Ticker", value="AAPL").upper()
        lookback = st.slider("Years of Data", 1, 10, 5)
        frequency = st.radio("Frequency", ["Daily", "Monthly"])
        
        with st.spinner(f"Fetching data for {ticker}..."):
            stock_data = fetch_stock_data(ticker, period=f"{lookback}y")
            if not stock_data.empty:
                stock_returns = calculate_returns(stock_data)
                
                # Use synthetic factors aligned to stock dates
                freq_map = {"Daily": "daily", "Monthly": "monthly"}
                model_map = {"Fama-French 3-Factor (FF3)": "3", "Fama-French 5-Factor (FF5)": "5"}
                
                factor_data = generate_synthetic_factors(
                    model=model_map[model_type],
                    frequency=freq_map[frequency],
                    years=lookback
                )
                
                # Align dates
                stock_returns, factor_data = align_data(stock_returns, factor_data)
                
                if stock_returns.empty:
                    st.error(f"❌ No overlapping dates found between {ticker} and factor data.")
                    st.info("💡 Try selecting a longer lookback period or a different frequency.")
                    st.stop()
                    
                st.success(f"✅ Ready to analyze {ticker} ({len(stock_returns)} trading days)")
            else:
                st.error(f"❌ Could not fetch data for {ticker}")
                st.stop()
    else:
        st.warning("Custom CSV upload coming soon.")
        st.stop()
    
    st.markdown("---")
    
    # Analyze button
    analyze_button = st.button(
        "🚀 Analyze",
        type="primary",
        use_container_width=True
    )

# Main content
if analyze_button:
    try:
        with st.spinner("Analyzing factor model..."):
            # Fit model and get summary using cached function
            summary, predictions = run_factor_analysis(
                model_type, stock_returns, factor_data, frequency
            )
        
        st.success("✅ Analysis complete!")
        
        # Display results
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"### 📊 Model Results: {ticker}")
            
            # Alpha
            alpha_annual = summary['alpha']
            alpha_tstat = summary['alpha_t_stat']
            alpha_pval = summary['alpha_p_value']
            
            sig_stars = ""
            if alpha_pval < 0.001:
                sig_stars = "***"
            elif alpha_pval < 0.01:
                sig_stars = "**"
            elif alpha_pval < 0.05:
                sig_stars = "*"
            
            st.markdown(f"""
            <div class="factor-card">
                <h4>Alpha (α)</h4>
                <h2 style="color: {'#2ca02c' if alpha_annual > 0 else '#d62728'};">
                    {alpha_annual*100:.2f}% {sig_stars}
                </h2>
                <p class="significance">
                    t-stat: {alpha_tstat:.2f}, p-value: {alpha_pval:.4f}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # R-squared
            st.metric("R-squared", f"{summary['r_squared']:.4f}")
            st.metric("Observations", f"{summary['observations']:,}")
            
            st.markdown("---")
            
            # Factor Betas
            st.markdown("### 📊 Factor Betas")
            
            betas = summary['betas']
            beta_tstats = summary['beta_t_stats']
            beta_pvals = summary['beta_p_values']
            
            beta_df = pd.DataFrame({
                'Factor': list(betas.keys()),
                'Beta': list(betas.values()),
                't-stat': [beta_tstats[f] for f in betas.keys()],
                'p-value': [beta_pvals[f] for f in betas.keys()],
                'Sig': ['***' if beta_pvals[f] < 0.001 else '**' if beta_pvals[f] < 0.01 else '*' if beta_pvals[f] < 0.05 else '' for f in betas.keys()]
            })
            
            st.dataframe(
                beta_df.style.format({
                    'Beta': '{:.4f}',
                    't-stat': '{:.2f}',
                    'p-value': '{:.4f}'
                }).background_gradient(subset=['Beta'], cmap='RdYlGn', vmin=-1, vmax=1),
                hide_index=True,
                use_container_width=True
            )
            
            st.markdown("""
            <p class="significance">
            Significance: *** p<0.001, ** p<0.01, * p<0.05
            </p>
            """, unsafe_allow_html=True)
        
        with col2:
            # Factor Exposures Bar Chart
            st.markdown("### 📊 Factor Exposures")
            
            factors = list(betas.keys())
            beta_values = list(betas.values())
            colors = ['#1f77b4' if b > 0 else '#d62728' for b in beta_values]
            
            fig_betas = go.Figure(data=[
                go.Bar(
                    x=factors,
                    y=beta_values,
                    marker_color=colors,
                    text=[f'{b:.3f}' for b in beta_values],
                    textposition='outside'
                )
            ])
            
            fig_betas.update_layout(
                yaxis_title="Beta",
                xaxis_title="Factor",
                showlegend=False,
                height=350
            )
            
            fig_betas.add_hline(y=0, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig_betas, use_container_width=True)
            
            # Actual vs Predicted Returns
            st.markdown("### 📈 Actual vs Predicted Returns")
            
            # Predictions already returned from run_factor_analysis
            
            # Create scatter plot
            fig_scatter = go.Figure()
            
            fig_scatter.add_trace(go.Scatter(
                x=predictions,
                y=stock_returns,
                mode='markers',
                name='Returns',
                marker=dict(size=5, color='#1f77b4', opacity=0.6),
                text=[f'Actual: {a:.4f}<br>Predicted: {p:.4f}' 
                      for a, p in zip(stock_returns, predictions)],
                hovertemplate='%{text}<extra></extra>'
            ))
            
            # Add 45-degree line
            min_val = min(predictions.min(), stock_returns.min())
            max_val = max(predictions.max(), stock_returns.max())
            fig_scatter.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Perfect Fit',
                line=dict(color='red', dash='dash')
            ))
            
            fig_scatter.update_layout(
                xaxis_title="Predicted Returns",
                yaxis_title="Actual Returns",
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Residual Analysis
        st.markdown("---")
        st.markdown("### 📊 Residual Analysis")
        
        residuals = stock_returns - predictions
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Residuals histogram
            fig_hist = go.Figure(data=[
                go.Histogram(
                    x=residuals,
                    nbinsx=50,
                    marker_color='#1f77b4',
                    name='Residuals'
                )
            ])
            
            fig_hist.update_layout(
                title="Distribution of Residuals",
                xaxis_title="Residual",
                yaxis_title="Frequency",
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Residuals over time
            fig_time = go.Figure(data=[
                go.Scatter(
                    y=residuals,
                    mode='lines',
                    line=dict(color='#1f77b4', width=1),
                    name='Residuals'
                )
            ])
            
            fig_time.add_hline(y=0, line_dash="dash", line_color="gray")
            
            fig_time.update_layout(
                title="Residuals Over Time",
                xaxis_title="Observation",
                yaxis_title="Residual",
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Model Interpretation
        st.markdown("---")
        st.markdown("### 💡 Interpretation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **Alpha:**
            - Annual Alpha: {alpha_annual*100:.2f}%
            - Significance: {sig_stars if sig_stars else 'Not significant'}
            - Interpretation: {'Outperforming' if alpha_annual > 0 else 'Underperforming'} 
              the factor model
            """)
        
        with col2:
            st.markdown(f"""
            **Market Beta:**
            - Beta: {betas['Mkt-RF']:.3f}
            - Interpretation: {'More volatile' if betas['Mkt-RF'] > 1 else 'Less volatile'} 
              than market
            - Risk: {'Higher' if betas['Mkt-RF'] > 1 else 'Lower'} systematic risk
            """)
        
        with col3:
            st.markdown(f"""
            **Model Fit:**
            - R-squared: {summary['r_squared']:.2%}
            - Explained Variance: {summary['r_squared']:.2%}
            - Unexplained: {(1-summary['r_squared']):.2%}
            """)
        
        # Factor Descriptions
        st.markdown("---")
        st.markdown("### 📚 Factor Descriptions")
        
        factor_desc = {
            'Mkt-RF': 'Market excess return (market risk premium)',
            'SMB': 'Small Minus Big (size factor)',
            'HML': 'High Minus Low (value factor)',
            'RMW': 'Robust Minus Weak (profitability factor)',
            'CMA': 'Conservative Minus Aggressive (investment factor)'
        }
        
        for factor in betas.keys():
            if factor in factor_desc:
                beta_val = betas[factor]
                interpretation = ""
                
                if factor == 'Mkt-RF':
                    if beta_val > 1:
                        interpretation = "More sensitive to market movements (aggressive)"
                    elif beta_val < 1:
                        interpretation = "Less sensitive to market movements (defensive)"
                    else:
                        interpretation = "Moves with the market"
                
                elif factor == 'SMB':
                    if beta_val > 0:
                        interpretation = "Behaves like small-cap stocks"
                    else:
                        interpretation = "Behaves like large-cap stocks"
                
                elif factor == 'HML':
                    if beta_val > 0:
                        interpretation = "Behaves like value stocks"
                    else:
                        interpretation = "Behaves like growth stocks"
                
                elif factor == 'RMW':
                    if beta_val > 0:
                        interpretation = "Behaves like profitable companies"
                    else:
                        interpretation = "Behaves like less profitable companies"
                
                elif factor == 'CMA':
                    if beta_val > 0:
                        interpretation = "Behaves like conservative investors"
                    else:
                        interpretation = "Behaves like aggressive investors"
                
                st.markdown(f"""
                **{factor}** ({factor_desc[factor]})
                - Beta: {beta_val:.3f}
                - {interpretation}
                """)
        
        # Phase 3: Save to history
        params = {
            'model': model_type,
            'ticker': ticker,
            'source': data_source,
            'freq': frequency
        }
        results_hist = {
            'alpha': summary['alpha'],
            'r_squared': summary['r_squared']
        }
        add_to_history('factors', params, results_hist)
        
        # Phase 3: Export Results
        st.markdown("---")
        st.markdown("### 📥 Export Results")
        
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        
        with col_ex1:
            export_df = pd.DataFrame({
                'Factor': factors,
                'Beta': beta_values
            })
            csv_data = export_to_csv(export_df)
            st.download_button("📄 Download CSV", csv_data, 
                             f"factors_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                             "text/csv", use_container_width=True)
        
        with col_ex2:
            json_data = export_to_json({
                'timestamp': pd.Timestamp.now().isoformat(),
                'parameters': params,
                'results': {k: float(v) for k, v in results_hist.items()}
            })
            st.download_button("📋 Download JSON", json_data,
                             f"factors_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                             "application/json", use_container_width=True)
            
        with col_ex3:
            history_count = len(get_history_dataframe('factors'))
            st.info(f"💾 Saved to history\n\n{history_count} total analyses")
        
    except Exception as e:
        st.error(f"❌ **Error:** {e}")
        st.exception(e)

else:
    # Initial state
    st.info("""
    👈 **Get Started:**
    1. Choose factor model (FF3 or FF5)
    2. Select data source (Synthetic for demo)
    3. Configure data parameters
    4. Click **Analyze** to see results
    
    **Features:**
    - Fama-French 3-Factor model
    - Fama-French 5-Factor model
    - Statistical significance testing
    - Factor exposure visualization
    - Actual vs predicted returns
    - Residual analysis
    - Model interpretation
    """)
    
    # Model descriptions
    st.markdown("### 📚 Factor Models")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Fama-French 3-Factor (FF3):**
        - Market (Mkt-RF): Market risk premium
        - SMB: Small minus Big (size effect)
        - HML: High minus Low (value effect)
        
        **Formula:**
        ```
        R - Rf = α + β₁(Rm-Rf) + β₂(SMB) + β₃(HML) + ε
        ```
        """)
    
    with col2:
        st.markdown("""
        **Fama-French 5-Factor (FF5):**
        - All FF3 factors plus:
        - RMW: Robust minus Weak (profitability)
        - CMA: Conservative minus Aggressive (investment)
        
        **Formula:**
        ```
        R - Rf = α + β₁(Rm-Rf) + β₂(SMB) + β₃(HML) 
                 + β₄(RMW) + β₅(CMA) + ε
        ```
        """)

# Sidebar footer
with st.sidebar:
    # Phase 3: History Panel
    st.markdown("---")
    st.markdown("### 📜 Analysis History")
    
    history_df = get_history_dataframe('factors')
    if not history_df.empty:
        st.dataframe(history_df.tail(5), use_container_width=True, hide_index=True)
        if st.button("Clear History", use_container_width=True):
            from app.utils.session_state import clear_history
            clear_history('factors')
            st.rerun()
    else:
        st.info("No analyses yet")
        
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - **Alpha** measures excess return
    - **Beta** measures factor sensitivity
    - **R-squared** shows model fit
    - **Significance** indicated by stars (*, **, ***)
    """)
