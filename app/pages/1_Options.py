"""
Options Pricing Page
Interactive options pricing calculator with Greeks and visualizations.
Phase 3: Export, History, Real Data, Scenario Analysis
"""

import streamlit as st
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from options.black_scholes import black_scholes_call, black_scholes_put
from options.european_options import price_european_call, price_european_put
from options.greeks import (
    delta_call, delta_put, gamma, vega,
    theta_call, theta_put, rho_call, rho_put
)
from utils.validation import validate_option_params, ValidationError

# Phase 3: Import utilities
from app.utils.export import export_to_csv, export_to_json, format_results_for_export
from app.utils.session_state import init_session_state, add_to_history, get_history_dataframe
from app.utils.data_fetcher import get_current_price, estimate_volatility, fetch_stock_data, calculate_returns

# Page configuration
st.set_page_config(
    page_title="Options Pricing - Quant Fundamentals",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

@st.cache_data
def calculate_options_results(S0, K, r, sigma, T, option_type, pricing_method, n_paths=100000):
    # Calculate option price
    if pricing_method == "Black-Scholes (Analytical)":
        if option_type == "Call":
            price = black_scholes_call(S0, K, r, sigma, T)
        else:
            price = black_scholes_put(S0, K, r, sigma, T)
        std_err = None
        
    elif pricing_method == "Monte Carlo":
        if option_type == "Call":
            price = price_european_call(S0, K, r, sigma, T, n_paths=n_paths)
        else:
            price = price_european_put(S0, K, r, sigma, T, n_paths=n_paths)
        std_err = None
        
    else:  # Parallel Monte Carlo
        from options.monte_carlo_parallel import (
            price_european_call_parallel,
            price_european_put_parallel
        )
        if option_type == "Call":
            price, std_err = price_european_call_parallel(S0, K, r, sigma, T, n_paths=n_paths)
        else:
            price, std_err = price_european_put_parallel(S0, K, r, sigma, T, n_paths=n_paths)
    
    # Calculate Greeks
    if option_type == "Call":
        delta = delta_call(S0, K, T, r, sigma)
        theta = theta_call(S0, K, T, r, sigma)
        rho = rho_call(S0, K, T, r, sigma)
    else:
        delta = delta_put(S0, K, T, r, sigma)
        theta = theta_put(S0, K, T, r, sigma)
        rho = rho_put(S0, K, T, r, sigma)
    
    gamma_val = gamma(S0, K, T, r, sigma)
    vega_val = vega(S0, K, T, r, sigma)
    
    return price, std_err, delta, gamma_val, vega_val, theta, rho

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
    st.title("📊 Options Pricing")
    st.markdown("Price options and calculate Greeks using Black-Scholes or Monte Carlo methods")
with col2:
    if st.button("🏠 Home"):
        st.switch_page("main.py")

st.markdown("---")

# Sidebar - Input Parameters
with st.sidebar:
    st.header("⚙️ Parameters")
    
    # Phase 3: Real Data Input
    st.subheader("📊 Data Source")
    use_real_data = st.checkbox("Use Real Stock Data", help="Fetch current price and volatility from market")
    
    if use_real_data:
        ticker = st.text_input("Stock Ticker", value="AAPL", help="Enter stock symbol (e.g., AAPL, MSFT)")
        
        if ticker:
            try:
                with st.spinner(f"Fetching data for {ticker}..."):
                    # Get current price
                    S0 = get_current_price(ticker)
                    st.success(f"✅ Current price: ${S0:.2f}")
                    
                    # Estimate volatility
                    prices = fetch_stock_data(ticker, period='1y')
                    sigma = estimate_volatility(prices['Adj Close'])
                    st.info(f"📊 Estimated volatility: {sigma*100:.2f}%")
            except Exception as e:
                st.error(f"❌ Error fetching data: {e}")
                st.warning("Using manual input instead")
                use_real_data = False
    
    st.markdown("---")
    
    # Basic parameters
    st.subheader("Option Parameters")
    
    if not use_real_data:
        S0 = st.number_input(
            "Stock Price (S₀)",
            min_value=0.01,
            value=100.0,
            step=1.0,
            help="Current price of the underlying stock"
        )
    else:
        st.metric("Stock Price (S₀)", f"${S0:.2f}", help="Fetched from market")
    
    K = st.number_input(
        "Strike Price (K)",
        min_value=0.01,
        value=100.0,
        step=1.0,
        help="Strike price of the option"
    )
    
    r = st.slider(
        "Risk-Free Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.1,
        help="Annual risk-free interest rate"
    ) / 100
    
    if not use_real_data:
        sigma = st.slider(
            "Volatility (%)",
            min_value=1.0,
            max_value=200.0,
            value=20.0,
            step=1.0,
            help="Annual volatility (standard deviation)"
        ) / 100
    else:
        st.metric("Volatility", f"{sigma*100:.2f}%", help="Estimated from historical data")
    
    T = st.slider(
        "Time to Maturity (years)",
        min_value=0.01,
        max_value=5.0,
        value=1.0,
        step=0.01,
        help="Time until option expiration"
    )
    
    st.markdown("---")
    
    # Option type
    option_type = st.radio(
        "Option Type",
        ["Call", "Put"],
        help="Type of option"
    )
    
    st.markdown("---")
    
    # Pricing method
    st.subheader("Pricing Method")
    pricing_method = st.selectbox(
        "Method",
        ["Black-Scholes (Analytical)", "Monte Carlo", "Monte Carlo (Parallel)"],
        help="Choose pricing method"
    )
    
    # Monte Carlo parameters (if selected)
    if "Monte Carlo" in pricing_method:
        n_paths = st.slider(
            "Number of Paths",
            min_value=10000,
            max_value=1000000,
            value=100000,
            step=10000,
            help="Number of simulation paths"
        )
    
    st.markdown("---")
    
    # Calculate button
    calculate_button = st.button(
        "🚀 Calculate",
        type="primary",
        use_container_width=True
    )

if calculate_button:
    try:
        # Validate inputs
        validate_option_params(S0, K, r, sigma, T)
        
        # Show progress
        with st.spinner("Calculating..."):
            n_val = n_paths if "Monte Carlo" in pricing_method else None
            price, std_err, delta, gamma_val, vega_val, theta, rho = calculate_options_results(
                S0, K, r, sigma, T, option_type, pricing_method, n_val
            )
        
        # Phase 3: Save to history
        params = {
            'S0': S0, 'K': K, 'r': r, 'sigma': sigma, 'T': T,
            'option_type': option_type,
            'method': pricing_method,
            'ticker': ticker if use_real_data else None
        }
        results = {
            'price': price,
            'std_err': std_err,
            'delta': delta,
            'gamma': gamma_val,
            'vega': vega_val,
            'theta': theta,
            'rho': rho
        }
        add_to_history('options', params, results)
        
        # Display results
        st.success("✅ Calculation complete!")
        
        # Results section
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 💰 Option Price")
            if std_err is not None:
                st.metric(
                    "Price",
                    f"${price:.4f}",
                    delta=f"± ${std_err:.4f}",
                    help="Option price with 95% confidence interval"
                )
            else:
                st.metric("Price", f"${price:.4f}")
            
            st.markdown("### 📊 The Greeks")
            
            # Greeks display
            greeks_data = {
                "Delta (Δ)": (delta, "Sensitivity to stock price"),
                "Gamma (Γ)": (gamma_val, "Rate of change of delta"),
                "Vega (ν)": (vega_val, "Sensitivity to volatility"),
                "Theta (Θ)": (theta, "Time decay per day"),
                "Rho (ρ)": (rho, "Sensitivity to interest rate")
            }
            
            for greek_name, (greek_value, greek_desc) in greeks_data.items():
                st.markdown(f"""
                <div class="metric-card">
                    <div class="greek-label">{greek_name}</div>
                    <div class="greek-value">{greek_value:.6f}</div>
                    <div style="font-size: 0.8rem; color: #888;">{greek_desc}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Moneyness indicator
            moneyness = S0 / K
            if moneyness > 1.05:
                st.info(f"📈 **In-the-Money** (S/K = {moneyness:.2f})")
            elif moneyness < 0.95:
                st.warning(f"📉 **Out-of-the-Money** (S/K = {moneyness:.2f})")
            else:
                st.success(f"🎯 **At-the-Money** (S/K = {moneyness:.2f})")
        
        with col2:
            # Payoff Diagram
            st.markdown("### 📈 Payoff Diagram")
            
            S_range = np.linspace(0.5 * K, 1.5 * K, 100)
            
            if option_type == "Call":
                intrinsic = np.maximum(S_range - K, 0)
                payoff = intrinsic - price
            else:
                intrinsic = np.maximum(K - S_range, 0)
                payoff = intrinsic - price
            
            fig_payoff = go.Figure()
            
            # Payoff line
            fig_payoff.add_trace(go.Scatter(
                x=S_range,
                y=payoff,
                mode='lines',
                name='Payoff',
                line=dict(color='#1f77b4', width=3),
                hovertemplate='Stock Price: $%{x:.2f}<br>Profit/Loss: $%{y:.2f}<extra></extra>'
            ))
            
            # Zero line
            fig_payoff.add_hline(
                y=0,
                line_dash="dash",
                line_color="gray",
                annotation_text="Break-even"
            )
            
            # Strike line
            fig_payoff.add_vline(
                x=K,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Strike: ${K}"
            )
            
            # Current stock price
            fig_payoff.add_vline(
                x=S0,
                line_dash="dot",
                line_color="green",
                annotation_text=f"Current: ${S0}"
            )
            
            # Profit/loss regions
            fig_payoff.add_hrect(
                y0=0, y1=max(payoff),
                fillcolor="green", opacity=0.1,
                line_width=0, annotation_text="Profit", annotation_position="top left"
            )
            fig_payoff.add_hrect(
                y0=min(payoff), y1=0,
                fillcolor="red", opacity=0.1,
                line_width=0, annotation_text="Loss", annotation_position="bottom left"
            )
            
            fig_payoff.update_layout(
                title=f"{option_type} Option Payoff at Expiration",
                xaxis_title="Stock Price at Expiry ($)",
                yaxis_title="Profit/Loss ($)",
                hovermode='x unified',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_payoff, use_container_width=True)
            
            # Greeks vs Spot Price
            st.markdown("### 📊 Greeks vs Spot Price")
            
            S_range_greeks = np.linspace(0.7 * K, 1.3 * K, 50)
            
            if option_type == "Call":
                deltas = [delta_call(s, K, T, r, sigma) for s in S_range_greeks]
            else:
                deltas = [delta_put(s, K, T, r, sigma) for s in S_range_greeks]
            
            gammas = [gamma(s, K, T, r, sigma) for s in S_range_greeks]
            
            fig_greeks = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Delta vs Spot", "Gamma vs Spot")
            )
            
            # Delta
            fig_greeks.add_trace(
                go.Scatter(x=S_range_greeks, y=deltas, name='Delta',
                          line=dict(color='#1f77b4', width=2)),
                row=1, col=1
            )
            
            # Gamma
            fig_greeks.add_trace(
                go.Scatter(x=S_range_greeks, y=gammas, name='Gamma',
                          line=dict(color='#ff7f0e', width=2)),
                row=1, col=2
            )
            
            # Strike lines
            fig_greeks.add_vline(x=K, line_dash="dash", line_color="red", row=1, col=1)
            fig_greeks.add_vline(x=K, line_dash="dash", line_color="red", row=1, col=2)
            
            fig_greeks.update_xaxes(title_text="Stock Price ($)", row=1, col=1)
            fig_greeks.update_xaxes(title_text="Stock Price ($)", row=1, col=2)
            fig_greeks.update_yaxes(title_text="Delta", row=1, col=1)
            fig_greeks.update_yaxes(title_text="Gamma", row=1, col=2)
            
            fig_greeks.update_layout(height=350, showlegend=False)
            
            st.plotly_chart(fig_greeks, use_container_width=True)
        
        # Additional information
        st.markdown("---")
        st.markdown("### 📋 Calculation Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **Input Parameters:**
            - Stock Price: ${S0:.2f}
            - Strike Price: ${K:.2f}
            - Risk-Free Rate: {r*100:.2f}%
            - Volatility: {sigma*100:.2f}%
            - Time to Maturity: {T:.2f} years
            """)
        
        with col2:
            st.markdown(f"""
            **Option Details:**
            - Type: {option_type}
            - Pricing Method: {pricing_method}
            - Moneyness: {moneyness:.4f}
            - Intrinsic Value: ${max(S0-K, 0) if option_type=='Call' else max(K-S0, 0):.2f}
            - Time Value: ${price - max(S0-K, 0) if option_type=='Call' else price - max(K-S0, 0):.2f}
            """)
        
        with col3:
            st.markdown(f"""
            **Greeks Summary:**
            - Delta: {delta:.4f}
            - Gamma: {gamma_val:.6f}
            - Vega: ${vega_val:.4f}
            - Theta: ${theta:.4f}/day
            - Rho: ${rho:.4f}
            """)
        
        # Phase 3: Export Results
        st.markdown("---")
        st.markdown("### 📥 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            export_df = pd.DataFrame({
                'Metric': ['Stock Price', 'Strike', 'Rate', 'Volatility', 'Time', 
                          'Type', 'Method', 'Price', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho'],
                'Value': [f'${S0:.2f}', f'${K:.2f}', f'{r*100:.1f}%', f'{sigma*100:.1f}%', 
                         f'{T:.2f}y', option_type, pricing_method, f'${price:.4f}',
                         f'{delta:.6f}', f'{gamma_val:.6f}', f'${vega_val:.4f}', 
                         f'${theta:.4f}', f'${rho:.4f}']
            })
            csv_data = export_to_csv(export_df)
            st.download_button("📄 Download CSV", csv_data, 
                             f"options_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                             "text/csv", use_container_width=True)
        
        with col2:
            json_data = export_to_json({
                'timestamp': datetime.now().isoformat(),
                'parameters': params,
                'results': {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                           for k, v in results.items() if v is not None}
            })
            st.download_button("📋 Download JSON", json_data,
                             f"options_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                             "application/json", use_container_width=True)
        
        with col3:
            history_count = len(get_history_dataframe('options'))
            st.info(f"💾 Saved to history\n\n{history_count} total calculations")

        # Phase 3: Scenario Analysis
        st.markdown("---")
        st.markdown("### 🎯 Scenario Analysis")
        
        with st.expander("📊 View Scenario Analysis", expanded=False):
            from app.components.scenario_analysis import options_scenario_analysis, create_scenario_heatmap
            
            # Run scenarios
            pricing_func = black_scholes_call if option_type == "Call" else black_scholes_put
            scenario_df = options_scenario_analysis(S0, K, r, sigma, T, option_type, pricing_func)
            
            st.dataframe(scenario_df, use_container_width=True, hide_index=True)
            
            # Heatmap
            st.markdown("#### Price Sensitivity Heatmap")
            S_range_heat = np.linspace(S0 * 0.7, S0 * 1.3, 20)
            vol_range_heat = np.linspace(sigma * 0.5, sigma * 1.5, 20)
            heatmap_fig = create_scenario_heatmap(S_range_heat, vol_range_heat, pricing_func, K, r, T)
            st.plotly_chart(heatmap_fig, use_container_width=True)
        
    except ValidationError as e:
        st.error(f"❌ **Invalid Input:** {e}")
        st.info("💡 Please check your input parameters and try again.")
    
    except Exception as e:
        st.error(f"❌ **Error:** {e}")
        st.exception(e)

else:
    # Initial state - show instructions
    st.info("""
    👈 **Get Started:**
    1. Enter option parameters in the sidebar
    2. Choose option type (Call or Put)
    3. Select pricing method
    4. Click **Calculate** to see results
    
    **Features:**
    - Black-Scholes analytical pricing
    - Monte Carlo simulation (standard and parallel)
    - Complete Greeks calculation
    - Interactive payoff diagrams
    - Greeks visualization
    """)
    
    # Example parameters
    st.markdown("### 📝 Example Parameters")
    st.markdown("""
    Try these example scenarios:
    
    **At-the-Money Call:**
    - Stock Price: $100, Strike: $100
    - Volatility: 20%, Time: 1 year
    - Risk-Free Rate: 5%
    
    **Out-of-the-Money Put:**
    - Stock Price: $100, Strike: $90
    - Volatility: 25%, Time: 0.5 years
    - Risk-Free Rate: 3%
    
    **Deep In-the-Money Call:**
    - Stock Price: $120, Strike: $100
    - Volatility: 15%, Time: 2 years
    - Risk-Free Rate: 4%
    """)

# Sidebar footer
with st.sidebar:
    # Phase 3: History Panel
    st.markdown("---")
    st.markdown("### 📜 Calculation History")
    
    history_df = get_history_dataframe('options')
    if not history_df.empty:
        st.dataframe(history_df.tail(5), use_container_width=True, hide_index=True)
        if st.button("Clear History", use_container_width=True):
            from app.utils.session_state import clear_history
            clear_history('options')
            st.rerun()
    else:
        st.info("No calculations yet")
        
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - **Delta** measures price sensitivity
    - **Gamma** shows delta's rate of change
    - **Vega** indicates volatility sensitivity
    - **Theta** represents time decay
    - **Rho** shows interest rate sensitivity
    """)
