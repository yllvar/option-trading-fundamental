"""
Quant Fundamentals - About & Documentation
Background information and mathematical references.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page configuration
st.set_page_config(
    page_title="About - Quant Fundamentals",
    page_icon="ℹ️",
    layout="wide"
)

# Custom CSS Loading
def load_css():
    css_file = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Header
st.markdown('<div class="main-header">ℹ️ About the Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Background, Mathematics, and Technical Architecture</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Project Overview", 
    "🧮 Mathematical Reference", 
    "🧪 Test Coverage",
    "📚 Documentation"
])

with tab1:
    st.header("📂 Project Overview")
    st.markdown("""
    **Quant Fundamentals** is an open-source quantitative finance library and interactive 
    web application designed for financial analysts, researchers, and students.
    
    ### Key Modules
    
    1.  **📊 Options Pricing**
        - Implementation of the Black-Scholes-Merton model for European options.
        - High-performance Monte Carlo simulations with parallel processing support.
        - Comprehensive Greeks analysis (Delta, Gamma, Vega, Theta, Rho).
    
    2.  **💼 Portfolio Optimization**
        - Modern Portfolio Theory (MPT) implementations.
        - Various optimization strategies: Maximum Sharpe Ratio, Minimum Volatility, Risk Parity.
        - Backtesting engine for historical performance evaluation.
    
    3.  **📈 Factor Models**
        - Fama-French 3-Factor and 5-Factor models.
        - Statistical analysis of asset returns and factor sensitivities.
        - Alpha and Beta decomposition.
    
    ### Technologies Used
    - **Python 3.11+**
    - **NumPy & Pandas**: Data manipulation and numerical computing.
    - **SciPy**: Optimization and statistical functions.
    - **Streamlit**: Web interface framework.
    - **Plotly**: Dynamic financial visualizations.
    """)

with tab2:
    st.header("🧮 Mathematical Reference")
    
    st.subheader("Black-Scholes-Merton Model")
    st.latex(r"""
    C(S, t) = S_0 \Phi(d_1) - K e^{-r(T-t)} \Phi(d_2)
    """)
    st.latex(r"""
    P(S, t) = K e^{-r(T-t)} \Phi(-d_2) - S_0 \Phi(-d_1)
    """)
    st.markdown("Where:")
    st.latex(r"""
    d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)(T-t)}{\sigma\sqrt{T-t}}
    """)
    st.latex(r"""
    d_2 = d_1 - \sigma\sqrt{T-t}
    """)
    
    st.subheader("Monte Carlo Pricing")
    st.markdown("""
    Asset prices are modeled using Geometric Brownian Motion (GBM):
    """)
    st.latex(r"""
    S_T = S_0 \exp\left( (r - \frac{1}{2}\sigma^2)T + \sigma\sqrt{T}Z \right)
    """)
    st.markdown("Where $Z \sim N(0, 1)$. The option price is then the discounted expected payoff:")
    st.latex(r"""
    V_0 = e^{-rT} E[Payoff(S_T)]
    """)
    
    st.subheader("Fama-French 5-Factor Model")
    st.latex(r"""
    R_{it} - R_{ft} = \alpha_i + \beta_{iMkt}(R_{Mt} - R_{ft}) + \beta_{is}SMB_t + \beta_{ih}HML_t + \beta_{ir}RMW_t + \beta_{ic}CMA_t + \epsilon_{it}
    """)

with tab3:
    st.header("🧪 Test Coverage")
    st.markdown("""
    The core library is backed by a robust testing suite with over **112 unique tests** 
    covering edge cases, numerical accuracy, and architectural integrity.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Options Module**")
        st.write("- Black-Scholes vs. Monte Carlo convergence tests.")
        st.write("- Greeks verification against finite difference methods.")
        st.write("- Parallel processing scaling tests.")
        
    with col2:
        st.info("**Portfolio & Factors**")
        st.write("- Optimization convergence and constraint adherence.")
        st.write("- Factor model regression accuracy.")
        st.write("- Cross-asset correlation consistency.")

with tab4:
    st.header("📚 Documentation")
    st.markdown("""
    For complete API documentation and development guides, please visit our 
    [GitHub Repository](https://github.com/yourusername/quant-fundamentals).
    
    ### Community & Support
    - **Report a bug**: Open an issue on GitHub.
    - **Contribute**: Pull requests are welcome!
    - **License**: MIT License.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem 0;">
    <p>Version 1.0.0 | Built by the Quant Fundamentals Team</p>
</div>
""", unsafe_allow_html=True)
